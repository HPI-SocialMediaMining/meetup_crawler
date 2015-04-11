import Queue
import threading
import utilities
import time

import fetchers

class CrawlThread (threading.Thread):

  WAIT_THRESHOLD = 1000
  WAIT_TIME = 20

  def __init__(self, threadID, group_queue, persister_class, job_queue, start_time=-1, end_time=-1):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.group_queue = group_queue
    self.persister_class = persister_class
    self.job_queue = job_queue
    self.logger = utilities.logger_with_name("Thread " + str(self.threadID))
    self.start_time = start_time
    self.end_time = end_time

  def run(self):
    while not self.group_queue.empty():
      if self.job_queue.qsize() > self.WAIT_THRESHOLD:
        time.sleep(self.WAIT_TIME)
        self.logger.info("Waiting for persister...")
        continue

      group_id = self.group_queue.get()
      self.logger.info("Crawling information for Group " + str(group_id) + " (approx. " + str(self.group_queue.qsize()) + " remaining)")
      persister = self.persister_class(self.job_queue)
      fetchers.BoardFetcher(persister, self.logger, group_id['urlname']).fetch_deep()
      fetchers.ProfileFetcher(persister, self.logger, {'group_id' : group_id['id']}).fetch()
      fetchers.MemberFetcher(persister, self.logger, {'group_id' : group_id['id']}).fetch()
      event_data = {'group_id': group_id['id']}
      if self.start_time > 0 and self.end_time > 0:
        event_data['time'] = str(self.start_time) + ',' + str(self.end_time)
      fetchers.EventFetcher(persister, self.logger, event_data).fetch_deep()
      persister.finish_group(group_id['id'])
    self.logger.info("Exiting")
