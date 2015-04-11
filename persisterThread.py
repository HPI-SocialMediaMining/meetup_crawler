import Queue
import threading
import utilities
import sys
import re

import fetchers
from db import DBManager

class PersisterThread (threading.Thread):

  def __init__(self, job_queue):
    threading.Thread.__init__(self)
    self.job_queue = job_queue
    self.should_run = True
    self.logger = utilities.logger_with_name("PersisterThread")

  def run(self):
    DBManager.get_connection().jconn.setAutoCommit(False)

    while self.should_run:
      try:
        jobs = self.job_queue.get(True, 5)
      except:
        self.logger.debug("No item in the queue. Waiting for something to do...")
        continue

      self.logger.info("Executing jobs on the database (approx. " + str(self.job_queue.qsize()) + " remaining)")
      for job in jobs:
        match = re.search('UPSERT (.*) VALUES .*', job.query_string)
        self.logger.info("  Job table: " + match.group(1) if match else "finishing group...")
        self.logger.info("  Job size: " + str(get_size(job.values_list) / 1024.0) + " KB")
        utilities.try_execution(
            lambda: DBManager.get_cursor().executemany(job.query_string, job.values_list),
            "Executing query: " + job.query_string + ", Last tuple: " + str(job.values_list[-1]),
            self.logger)

      DBManager.get_connection().commit()
      self.logger.info("Finished executing jobs on the database")
    self.logger.info("PersisterThread stopped")

  def stop(self):
    self.should_run = False


def get_size(list):
  item_size = 0
  for item in list:
    if type(item) is list:
      item_size += get_size(item)
    else:
      item_size += sys.getsizeof(item)
  return sys.getsizeof(list) + item_size