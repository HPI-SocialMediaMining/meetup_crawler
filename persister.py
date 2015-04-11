import abc
import re
from db import Query

class Persister(object):
  """Responsible for persisting values"""

  def __init__(self, job_queue):
    super(Persister, self).__init__()

  @abc.abstractmethod
  def persist(self, table_name, values, id_values={}):
    pass

  def finish(self):
    pass

  def value_to_string(self, value):
    if value is None:
      return 'NULL'
    if not isinstance(value, unicode):
      return str(value)
    return '"' + value + '"'


class PrintPersister(Persister):
  """Print SQL statements on the console"""

  def __init__(self, job_queue):
    super(PrintPersister, self).__init__(job_queue)

  def persist(self, table_name, values, id_values={}):
    converted_values = [self.value_to_string(value) for value in values]
    print self.create_sql_statement(table_name, converted_values).encode('utf-8')

  def create_sql_statement(self, table_name, values):
    return "INSERT INTO %s VALUES (%s)" % (table_name, ', '.join(values))


class MeetupQuery(Query):
  COLUMNS = '*'
  TABLE = None

  def __init__(self, table_name):
    super(MeetupQuery, self).__init__()
    self.TABLE = table_name

  def result_object(self, row):
    return 1

class DbPersister(Persister):
  """Persist tuples in the DB"""

  class Job(object):

    def __init__(self, query_string):
      self.query_string = query_string
      self.values_list = []

  def __init__(self, job_queue):
    super(DbPersister, self).__init__(job_queue)
    self.job_queue = job_queue
    self.jobs = {}

  def finish(self):
    self.job_queue.put(self.jobs.values())
    self.jobs = {}

  def finish_group(self, group_id):
    job = DbPersister.Job(
      "UPDATE Meetup.Groups SET crawl_status = \'done\' WHERE id = ?"
    )
    job.values_list.append((group_id,))
    self.job_queue.put([job])

  def persist(self, table_name, values, id_values={}):
    if not table_name in self.jobs:
      self.jobs[table_name] = DbPersister.Job(self.get_query_string(table_name, len(values), id_values))

    self.jobs[table_name].values_list.append(self.prepare_values(values, id_values))

  def prepare_values(self, values, id_values):
    all_values = []
    for value in (values + id_values.values()):
      if type(value) == int:
        all_values.append(long(value))
      else:
        all_values.append(value)
    return tuple(all_values)

  def get_query_string(self, table_name, n_values, id_values):
    n_placeholders = '?, ' * (n_values - 1) + '?'
    id_values_strings = ["%s = ?" % key for key in id_values.keys()]
    where_clause = ' AND '.join(id_values_strings)

    return "UPSERT %s VALUES (%s) WHERE %s" % (table_name, n_placeholders, where_clause)
