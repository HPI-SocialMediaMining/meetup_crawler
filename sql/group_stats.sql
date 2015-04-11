/*number of groups*/
SELECT COUNT(*) FROM ~groups~

/*have description*/
SELECT COUNT(*) FROM ~groups~ WHERE description IS NOT NULL

/*avg. length of description*/
SELECT AVG(LENGTH(description)) FROM ~groups~

/*median length of description*/
SELECT MEDIAN(LENGTH(description)) FROM ~groups~

/*maximum length of description*/
SELECT MAX(LENGTH(description)) FROM ~groups~

/*open*/
SELECT COUNT(*) FROM ~groups~ WHERE join_mode = 'open'

/*membership dues*/
SELECT COUNT(*) FROM ~groups~ WHERE membership_dues_fee IS NOT NULL

/*number of different organizers*/
SELECT COUNT(DISTINCT(organizer_member_id)) FROM ~groups~

/*average rating*/
SELECT AVG(rating) FROM ~groups~

/*average rating (!= 0)*/
SELECT AVG(rating) FROM ~groups~ WHERE rating != 0

/*median rating*/
SELECT MEDIAN(rating) FROM ~groups~

/*sponsored groups*/
SELECT COUNT(*) FROM ~groupsponsors~

/*number of categories*/
SELECT COUNT(DISTINCT category_id) FROM ~groups~

/*most prominent category*/
SELECT name FROM ~categories~ GROUP BY name, id ORDER BY COUNT(id) DESC LIMIT 1

/*Groups that have at least one event*/
SELECT COUNT(group_id)
FROM (
  SELECT groups.id AS group_id, COUNT(events.id) AS n_events
  FROM ~groups~ groups
  JOIN ~events~ events
  ON groups.id = events.group_id
  GROUP BY groups.id
)

/*Events per group with events*/
SELECT AVG(n_events)
FROM (
  SELECT groups.id, COUNT(events.id) AS n_events
  FROM ~groups~ groups
  JOIN ~events~ events
  ON groups.id = events.group_id
  GROUP BY groups.id
)
