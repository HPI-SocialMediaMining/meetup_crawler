# Meetup Crawler
A python based crawler for the EBSN Meetup

You have to fill in some information and setup the database, before you can run the crawler (also see the requirements section for information about require packages).
The database has to have a schema called `Meetup` containing tables as created by the commands in `schema.sql`.
To prepare the crawler you have to fill in the host, port, user and password for the prepared destination database instance.
Additionally, you need a JDBC driver that is able to communicate with your database.

To run the crawler, simply call `python crawl.py`.
To see all configuration capabilites, call `python crawl.py --help`.

## Supported Database Systems:
* SAP HANA

## Requirements:

* jaydebeapi (`pip install jaydebeapi`)
* JPype (see instructions below)


#### Install JPype on Mac OS X

* Download [JPype](http://sourceforge.net/projects/jpype/files/JPype/0.5.4/)
* Find out your JAVA_HOME by executing `/usr/libexec/java_home`
* In `setup.py` change `setupMacOSX()`:
  * Set `self.javaHome` to your JAVA_HOME
  * Set `self.jdkInclude` to `"darwin"`
* Execute `python setup.py install`

#### Install JPype on Windows

* go to [this site](http://www.lfd.uci.edu/~gohlke/pythonlibs/) and run the installer


--------------
#### db.py


A little demo:

```python
class TestQuery(Query):
  COLUMNS = 'id', 'name', 'type'
  TABLE = 'GROUPS'
  ORDER_BY = 'id'
  GROUP_BY = 'type'

  def result_object(self, row):
    return {
      'id':   row[0],
      'name': row[1],
      'type': row[2]
  }
```

This defines a query pattern, that now can be used to make specific queries:

```python
def get_sample_query(cur, fromID, toID):
  query = TestQuery()
  query.filter('id >= (?)', fromID)
  query.filter('id <= (?)', toID)

  with measure_time('simple test query'):
    return query.execute(cur)
```

**Attention:** Before you use `DBManager`, make sure to call `DBManager.init(number_of_connections)`.
This will make it thread-safe, as long as you close every opened connection before exiting a thread.
Each thread *needs* a seperate connection if it needs to communicate to the DB.
Connection and cursor objects must not be shared between threads!

Writing data to the database is very simple. You need a cursor:

    cursor = DBManager.get_cursor()

With that you can fire queries like this:

```python
cursor.execute('CREATE TABLE bla (INTEGER blub)')

# you can also use dynamic values (without string operations):
values = 'bla', 'INTEGER', 'blub'
cursor.execute('CREATE TABLE ? (? ?)', values)
```

You can use the same connection and cursor for multiple queries.
Make sure, that you commit your changes and close the connection to the database after you are done:

```python
DBManager.get_connection().commit()
DBManager.close_connection()
```


#### dbstats.py

A little tool for getting information about the crawled data. It runs all queries it can find in the `sql/` subdirectory. These can be placed in one or more files. A leading comment (`/* text here */`) defines the title of the query. The query itself can be written in one or more lines, but not in a comment line. Comments inside a query are not allowed.
There are some variables defined, which will be injected by the script:
* `!city!` (the current city)
* `~groups~` (only groups which have `crawled_city = !city!`)
* `~members~` (only members from `~groups~`)
* `~profiles~`
* `~categories~`
* `~boards~`
* `~events~`

These can be used inside the queries:

```SQL
SELECT COUNT(*) FROM ~members~
```

transforms to

```SQL
SELECT
  COUNT(*)
FROM
  (SELECT
    m.*
  FROM
    Meetup.members m
  JOIN
    (SELECT
      DISTINCT member_id
    FROM
      (SELECT
        p.*
      FROM
        Meetup.profiles p
      JOIN
        (SELECT
          *
        FROM
          Meetup.groups
        WHERE
          crawled_city = 'berlin') g
      ON p.group_id = g.id)) p
  ON m.id = p.member_id)
```
