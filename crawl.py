import Queue
import threading
import utilities
import cities

import argparse
import fetchers
import persister
import crawlThread
import persisterThread
import time
import db

class Crawler(object):

  def __init__(self, persister_class, number_of_threads, fresh, start_time=-1, end_time=-1):
    super(Crawler, self).__init__()
    self.persister_class = persister_class
    self.number_of_threads = number_of_threads
    self.fresh = fresh
    self.logger = utilities.logger_with_name("MainThread")
    self.start_time = start_time
    self.end_time = end_time

  def crawl_all(self):

    for group_filter in cities.CITIES.values():
      self.crawl(group_filter)

  def crawl(self, group_filter):
    self.logger.info('Crawling city: ' + group_filter['city'])
    job_queue = Queue.Queue()

    if self.fresh:
      group_ids = self.crawl_groups(group_filter, job_queue)
    else:
      group_ids = self.get_unfinished_groups(group_filter)

    persister_thread = persisterThread.PersisterThread(job_queue)
    persister_thread.start()

    group_id_queue = Queue.Queue(len(group_ids))
    for group_id in group_ids:
      group_id_queue.put(group_id)

    threads = []
    for i in range(self.number_of_threads):
      thread = crawlThread.CrawlThread(i, group_id_queue, self.persister_class,
                                        job_queue, self.start_time, self.end_time)
      thread.daemon = True
      thread.start()
      threads.append(thread)

    while not group_id_queue.empty():
      time.sleep(10)

    for t in threads:
      t.join()

    while not job_queue.empty():
      time.sleep(10)

    persister_thread.stop()
    persister_thread.join()

  def crawl_groups(self, group_filter, job_queue):
    return fetchers.GroupFetcher(
        self.persister_class(job_queue),
        self.logger,
        group_filter['city'],
        group_filter
    ).fetch(['id', 'urlname'])

  def get_unfinished_groups(self, group_filter):
    cursor = db.DBManager.get_cursor()
    cursor.execute(
      """ SELECT id, urlname
          FROM Meetup.Groups
          WHERE crawled_city=\'%s\' AND crawl_status=\'new\'""" % group_filter['city'])
    result = [{'id' : row[0], 'urlname' : row[1]} for row in cursor.fetchall()]
    cursor.close()
    db.DBManager.close_connection()
    return result

def meetup_timestamp(timestamp):
  factor = 1
  if timestamp > 0:
    factor = 1000
  return int(timestamp) * factor

if __name__ == '__main__':
  persisters = {
    'print' : persister.PrintPersister,
    'hana' : persister.DbPersister,
    'ignore' : persister.Persister,
  }

  parser = argparse.ArgumentParser(description='Crawl Meetup data.')
  parser.add_argument('--city', dest='city', action='store', default='all',
                     help='What city to crawl (all, ' + ', '.join(cities.CITIES.keys()) + ')')
  parser.add_argument('--persister', dest='persister', action='store', default='hana',
                     help='Choose what to do with the SQL statements (print, hana, ignore)')
  parser.add_argument('--fresh', dest='fresh', action='store_true', default=False,
                     help='If active, it starts with crawling all groups, overwriting existing entries, including the status')
  parser.add_argument('--threads', dest='threads', action='store', default=4,
                     help='Define how many threads should be used to crawl information relating to groups')
  parser.add_argument('--starttime', dest='start_time', action='store', default=-1,
                     help='Set the point in time from when events should be crawled (UNIX timestamp format).')
  parser.add_argument('--endtime', dest='end_time', action='store', default=-1,
                     help='Set the point in time up until events should be crawled (UNIX timestamp format).')
  args = parser.parse_args()

  db.DBManager.init(2)

  crawler = Crawler(persisters[args.persister], int(args.threads), args.fresh,
                    meetup_timestamp(args.start_time), meetup_timestamp(args.end_time))
  if args.city in cities.CITIES:
    crawler.crawl(cities.CITIES[args.city])
  else:
    crawler.crawl_all()
