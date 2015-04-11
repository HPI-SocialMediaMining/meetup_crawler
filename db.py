import operator, time, sqlite3
from contextlib import contextmanager

@contextmanager
def measure_time(name):
  t = time.time()
  yield
  print '%s: %s' %(name, time.time() - t)

import jpype
import jaydebeapi

class HANA:
  HOST = ''
  PORT = 30015 #HANA default Port: 3<instance number>15
  USER = ''
  PASSWORD = ''


url = 'jdbc:sap://%s:%s' %(HANA.HOST, HANA.PORT)

class DBManager:
  connections = []
  current = -1

  @staticmethod
  def init(thread_count):
    for _ in range(thread_count + 1):
      DBManager.connections.append(jaydebeapi.connect(
          'com.sap.db.jdbc.Driver',
          [url, HANA.USER, HANA.PASSWORD],
          'jdbc_driver.jar'))
      DBManager.current = 0

  @staticmethod
  def get_connection():
    if not jpype.isThreadAttachedToJVM():
      jpype.attachThreadToJVM()
    if DBManager.current >= 0 and DBManager.current < len(DBManager.connections):
      return DBManager.connections[DBManager.current]

  @staticmethod
  def close_connection():
    connection = DBManager.get_connection()
    if connection:
      connection.close()
      DBManager.current += 1

  @staticmethod
  def get_cursor():
    return DBManager.get_connection().cursor()


class Query(object):
  ORDER_BY = ''
  GROUP_BY = None

  def __init__(self):
    self.condition = AndCondition()

  def format_element(self, arg):
    return arg

  def filter_list(self, sql, li):
    self.condition.add_conditions(OrCondition(*map(lambda x: SimpleCondition(sql, x), li)))

  def filter(self, sql, arg = None):
    if isinstance(arg, list):
      self.filter_list(sql, arg)
    else:
      self.condition.add_conditions(SimpleCondition(sql, arg))

  def filter_if_set(self, sql, arg):
    if arg:
      return self.filter(sql, arg)

  def filter_player_if_set(self, sql, arg):
    if arg:
      return self.filter_player(sql, arg)

  def __str__(self):
    sql = '''SELECT {columns}
    FROM {table}'''.format(
      columns = ', '.join(self.COLUMNS),
      table = self.TABLE
    )
    if self.condition.__has_content__():
      sql += '\nWHERE ' + self.condition.__sql__()

    if self.GROUP_BY:
      sql += '\nGROUP BY ' + self.GROUP_BY

    if self.ORDER_BY:
      sql += '\nORDER BY ' + self.ORDER_BY

    return sql

  def execute(self, cur):
    print 'sql: ' + str(self)
    print self.condition.__params__()

    cur.execute(str(self), self.condition.__params__())

    return map(self.result_object, cur.fetchall())

class WhereCondition(object):
  def __init__(self, *conditions):
    self.subconditions = list(conditions)

  def add_conditions(self, *conditions):
    assert all( map(lambda x: isinstance(x, WhereCondition), conditions) )
    self.subconditions.extend(conditions)

  def __connector__(self):
    return ' ' + self._connector + ' '

  def __has_content__(self):
    return any(map(lambda x: x.__has_content__(), self.subconditions))

  def __sql__(self):
    conditions = filter(lambda x: x, map(lambda x: x.__sql__(), self.subconditions))
    if len(conditions) == 0:
      return ''
    if len(conditions) == 1:
      return conditions[0]
    return '(' + self.__connector__().join(conditions) + ')'

  def __params__(self):
    return reduce(lambda a, b: a + b, map(lambda x: x.__params__(), self.subconditions), [])

class AndCondition(WhereCondition):
  def __init__(self, *conditions):
    super(AndCondition, self).__init__(*conditions)
    self._connector = 'AND'

class OrCondition(WhereCondition):
  def __init__(self, *conditions):
    super(OrCondition, self).__init__(*conditions)
    self._connector = 'OR'

class SimpleCondition(WhereCondition):
  def __init__(self, sql, param):
    self.sql = sql
    self.param = param

  def __has_content__(self):
    return True

  def __sql__(self):
    return self.sql

  def __params__(self):
    return [self.param] if self.param is not None else []

class EmptyCondition(WhereCondition):
  def __has_content__(self):
    return False

  def __sql__(self):
    return ''

  def __params__(self):
    return []
