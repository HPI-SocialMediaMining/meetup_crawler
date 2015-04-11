/*No social media account linked*/
SELECT
    COUNT(id)
FROM (
    SELECT
        id,
        SUM(
            (case when other_services_twitter_identifier is null then 0 else 1 end) +
            (case when other_services_flickr_identifier is null then 0 else 1 end) +
            (case when other_services_tumblr_identifier is null then 0 else 1 end) +
            (case when other_services_linkedin_identifier is null then 0 else 1 end)
        ) AS number_of_accounts
    FROM
        ~members~
    GROUP BY
        id
    )
WHERE
    number_of_accounts = 0

/*exactly 1*/
SELECT COUNT(id) FROM (SELECT id, SUM((case when other_services_twitter_identifier is null then 0 else 1 end) + (case when other_services_flickr_identifier is null then 0 else 1 end) + (case when other_services_tumblr_identifier is null then 0 else 1 end) + (case when other_services_linkedin_identifier is null then 0 else 1 end)) AS number_of_accounts FROM ~members~ GROUP BY id) WHERE number_of_accounts = 1
/*exactly 2*/
SELECT COUNT(id) FROM (SELECT id, SUM((case when other_services_twitter_identifier is null then 0 else 1 end) + (case when other_services_flickr_identifier is null then 0 else 1 end) + (case when other_services_tumblr_identifier is null then 0 else 1 end) + (case when other_services_linkedin_identifier is null then 0 else 1 end)) AS number_of_accounts FROM ~members~ GROUP BY id) WHERE number_of_accounts = 2
/*exactly 3*/
SELECT COUNT(id) FROM (SELECT id, SUM((case when other_services_twitter_identifier is null then 0 else 1 end) + (case when other_services_flickr_identifier is null then 0 else 1 end) + (case when other_services_tumblr_identifier is null then 0 else 1 end) + (case when other_services_linkedin_identifier is null then 0 else 1 end)) AS number_of_accounts FROM ~members~ GROUP BY id) WHERE number_of_accounts = 3
/*exactly 4*/
SELECT COUNT(id) FROM (SELECT id, SUM((case when other_services_twitter_identifier is null then 0 else 1 end) + (case when other_services_flickr_identifier is null then 0 else 1 end) + (case when other_services_tumblr_identifier is null then 0 else 1 end) + (case when other_services_linkedin_identifier is null then 0 else 1 end)) AS number_of_accounts FROM ~members~ GROUP BY id) WHERE number_of_accounts = 4

/*percentage of members with at least one linked account*/
SELECT
    100 / (SELECT COUNT(*) FROM ~members~) *
    (SELECT
        COUNT(*)
    FROM
        ~members~
    WHERE
        other_services_twitter_identifier IS NOT NULL OR
        other_services_tumblr_identifier IS NOT NULL OR
        other_services_linkedin_identifier IS NOT NULL OR
        other_services_flickr_identifier IS NOT NULL)
FROM DUMMY