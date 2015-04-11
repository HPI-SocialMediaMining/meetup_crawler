import os
import time
import utilities

from db import DBManager


RELATIONS = {
    "~groups~": "(SELECT * FROM Meetup.groups WHERE crawled_city = !city!)",
    "~profiles~": "(SELECT p.* FROM Meetup.profiles p JOIN ~groups~ g ON p.group_id = g.id)",
    "~events~": "(SELECT e.* FROM Meetup.events e JOIN ~groups~ g ON e.group_id = g.id)",
    "~rsvps~": "(SELECT r.* FROM Meetup.rsvps r JOIN ~events~ e ON r.event_id = e.id)",
    "~members~": "(SELECT m.* FROM Meetup.members m JOIN (SELECT DISTINCT member_id FROM ~profiles~) p ON m.id = p.member_id)",
    "~boards": "(SELECT b.* FROM Meetup.boards b JOIN ~groups~ g ON b.group_id = g.id)",
    "~categories~": "(SELECT c.* FROM Meetup.categories c JOIN ~groups~ g ON g.category_id = c.id)",
    "~groupsponsors~": "(SELECT * FROM Meetup.groups groups JOIN Meetup.groupsponsors sponsors on groups.id = sponsors.foreign_id WHERE crawled_city = !city!)"
}

class MeetupStatisticsFetcher(object):
    """gathers statistics about crawled cities and dumps results to a dictionary or csv file"""

    def __init__(self, cities):
        super(MeetupStatisticsFetcher, self).__init__()
        DBManager.init(1)
        self.cursor = DBManager.get_cursor()
        self.cities = cities
        self.logger = utilities.logger_with_name("StatisticsFetcher")
        self.query, self.title = "", ""
        self.results = dict()

    def walk(self, directory):
        """recursively searches a directory for sql files to run"""
        self.logger.info("searching directory " + directory)
        for item in os.listdir(directory):
            if os.path.isdir(item):
                self.walk(item)
            else:
                self.process_file(directory + item)

    def process_file(self, filename):
        self.logger.info("processing file " + filename)
        for city in self.cities:
            for line in open(filename, 'r'):
                if is_comment(line):
                    self.run_query_if_needed(city)
                    self.title = filename + '/' + cleanup_title(line)
                    self.query = ""
                else:
                    self.query += line
            self.run_query_if_needed(city)

    def run_query_if_needed(self, city):
        if self.query != "":
            if not self.title in self.results:
                self.results[self.title] = dict()
            self.run_query(city)

    def run_query(self, city):
        try:
            self.cursor.execute(convert_query(self.query, city))
            for sequence in self.cursor.fetchall():
                self.results[self.title][city] = ",".join(map(str, sequence))
        except:
            self.results[self.title][city] = "#ERROR#"
            self.logger.error("[%s] failed for [%s]" % (self.title, city))

    def get_results(self):
        return self.results

    def dump_results_to_csv(self):
        self.logger.info("Writing output...")

        if not os.path.exists('stats/'):
            os.makedirs('stats/')

        header = ['key'] + sorted(self.cities)
        output = open('stats/output_%s.csv' % time.strftime("%Y%m%d-%H%M%S"), 'w')
        output.write(','.join(header) + '\n')

        for key in sorted(self.results.keys()):
            items = []
            for city in sorted(self.cities):
                items.append(self.results[key][city])
            output.write(key + ',' + ','.join(items) + '\n')

        output.close()
        self.logger.info("Done.")


def is_comment(line):
    return line.startswith("/*")

def cleanup_title(string):
    return string.replace('/*', '').replace('*/', '').replace('\n', '')

def convert_query(query, city):
    before = None
    while query != before:
        before = query
        for key in RELATIONS.keys():
            query = query.replace(key, RELATIONS[key])
    return query.replace("!city!", "'%s'" % city)



if __name__ == '__main__':
    fetcher = MeetupStatisticsFetcher(['berlin', 'hamburg', 'new york', 'san francisco', 'osaka', 'tokyo', 'london', 'york', 'chicago'])
    fetcher.walk('sql/')
    fetcher.dump_results_to_csv()
