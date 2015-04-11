/*Event count*/
SELECT COUNT(*) FROM ~events~

/*Events with at least one RSVP*/
SELECT COUNT(event_id)
FROM (
  SELECT events.id AS event_id, COUNT(rsvps.rsvp_id) AS n_rsvps
  FROM ~events~ events
  JOIN ~rsvps~ rsvps
  ON events.id = rsvps.event_id
  GROUP BY events.id
)

/*RSVPs per event with RSVPs (AVG)*/
SELECT AVG(n_rsvps)
FROM (
  SELECT events.id, COUNT(rsvps.rsvp_id) AS n_rsvps
  FROM ~events~ events
  JOIN ~rsvps~ rsvps
  ON events.id = rsvps.event_id
  GROUP BY events.id
)

/*RSVPs per event with RSVPs (MEDIAN)*/
SELECT MEDIAN(n_rsvps)
FROM (
  SELECT events.id, COUNT(rsvps.rsvp_id) AS n_rsvps
  FROM ~events~ events
  JOIN ~rsvps~ rsvps
  ON events.id = rsvps.event_id
  GROUP BY events.id
)

/*Past events*/
SELECT COUNT(id) FROM ~events~ WHERE time < SECONDS_BETWEEN(TO_TIMESTAMP('1970-01-01 00:00:00.000'), TO_TIMESTAMP(CURRENT_UTCTIMESTAMP))

/*Events with duration*/
SELECT COUNT(id) FROM ~events~ WHERE duration IS NOT NULL

/*Average duration (min)*/
SELECT AVG(duration) / 1000 / 60 FROM ~events~ WHERE duration IS NOT NULL

/*Median duration (min)*/
SELECT MEDIAN(duration) / 1000 / 60 FROM ~events~ WHERE duration IS NOT NULL
