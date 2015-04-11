CREATE COLUMN TABLE Meetup.Boards (
    id INTEGER,
    created BIGINT,
    discussion_count INTEGER,
    group_id INTEGER,
    name NVARCHAR(255),
    post_count INTEGER,
    updated BIGINT,

    PRIMARY KEY (id)
);

CREATE COLUMN TABLE Meetup.Categories (
    id INTEGER,
    name NVARCHAR(255),
    shortname NVARCHAR(255),

    PRIMARY KEY (id)
);

CREATE COLUMN TABLE Meetup.DiscussionPosts (
    id INTEGER,
    body NCLOB,
    created BIGINT,
    discussion_id INTEGER,
    in_reply_to INTEGER,
    member_id INTEGER, -- member that started the discussion, not the one that wrote the post (docs)?!
    subject NVARCHAR(255),
    updated BIGINT,

    PRIMARY KEY (id)
);

CREATE COLUMN TABLE Meetup.Discussions (
    id INTEGER,
    board_id INTEGER,
    created BIGINT, -- redundant with Boards, as it is the creation time of the board according to the docs
    reply_count INTEGER,
    started_by_name NVARCHAR(255), -- probably redundant with member_id in the matching DiscussionPost
    updated BIGINT, -- probably redundant with updated of last post made in this Discussion

    PRIMARY KEY (id)
);

CREATE COLUMN TABLE Meetup.EventQuestions (
    id INTEGER,
    question NCLOB,
    required INTEGER,

    PRIMARY KEY (id)
);

CREATE COLUMN TABLE Meetup.Events (
    id NVARCHAR(255),
    comment_count INTEGER,
    created BIGINT,
    description NCLOB,
    duration BIGINT,
    event_url NVARCHAR(255),
    featured INTEGER,
    fee_accepts NVARCHAR(255),
    fee_amount DOUBLE,
    fee_currency NVARCHAR(255),
    fee_description NVARCHAR(255),
    fee_label NVARCHAR(255),
    fee_required INTEGER,
    group_id INTEGER,
    headcount INTEGER,
    how_to_find_us NCLOB,
    is_simplehtml INTEGER,
    maybe_rsvp_count INTEGER,
    name NVARCHAR(255),
    photo_count INTEGER,
    photo_url NVARCHAR(255),
    rating_average DOUBLE,
    rating_count INTEGER,
    rsvp_limit INTEGER,
    rsvp_rules_close_time BIGINT,
    rsvp_rules_closed INTEGER,
    rsvp_rules_guest_limit INTEGER,
    rsvp_rules_open_time BIGINT,
    rsvp_rules_waitlisting NVARCHAR(10),
    simple_html_description NCLOB,
    status NVARCHAR(255),
    time BIGINT,
    timezone NVARCHAR(255),
    trending_rank INTEGER,
    updated BIGINT,
    utc_offset INTEGER,
    venue_visibility NVARCHAR(255),
    visibility NVARCHAR(255),
    why NCLOB,
    yes_rsvp_count INTEGER,
    venue_id INTEGER,

    PRIMARY KEY (id)
);

CREATE COLUMN TABLE Meetup.Events_Survey_Questions (
    left_id NVARCHAR(255),
    right_id INTEGER,
    PRIMARY KEY (left_id, right_id)
);

CREATE COLUMN TABLE Meetup.GroupAnswers (
    group_id INTEGER,
    member_id INTEGER,
    question_id INTEGER,
    question NCLOB, -- redundant, but just in case
    answer NCLOB,

    PRIMARY KEY (group_id, member_id, question_id)
);

CREATE COLUMN TABLE Meetup.GroupQuestions (
    id INTEGER,
    question NCLOB,

    PRIMARY KEY (id)
);

CREATE COLUMN TABLE Meetup.Groups (
    id INTEGER,
    crawled_city NVARCHAR(255),
    crawl_status NVARCHAR(255),
    approved INTEGER,
    city NVARCHAR(255),
    country NVARCHAR(255),
    created BIGINT,
    description NCLOB,
    is_simplehtml INTEGER,
    join_mode NVARCHAR(255),
    lat DOUBLE,
    link NVARCHAR(255),
    list_mode NVARCHAR(10),
    lon DOUBLE,
    members INTEGER,
    membership_dues_currency NVARCHAR(10),
    membership_dues_fee INTEGER,
    membership_dues_fee_desc NVARCHAR(255),
    membership_dues_required INTEGER,
    name NVARCHAR(255),
    organizer_member_id INTEGER, -- redundant with role of a profile, although "role" is mightier as it describes Organizers as well as Assistant Organizers, Co-organizers, or Event Organizers
    other_services_flickr_identifier NVARCHAR(255),
    other_services_linkedin_identifier NVARCHAR(255),
    other_services_tumblr_identifier NVARCHAR(255),
    other_services_twitter_identifier NVARCHAR(255),
    primary_topic NVARCHAR(255),
    rating DOUBLE,
    short_link NVARCHAR(255),
    simple_html_description NCLOB,
    state NVARCHAR(255),
    timezone NVARCHAR(255),
    urlname NVARCHAR(255),
    visibility NVARCHAR(15),
    welcome_message NCLOB,
    who NVARCHAR(255),
    category_id INTEGER,

    PRIMARY KEY (id)
);

CREATE COLUMN TABLE Meetup.Groups_Join_Info_Questions (
    left_id INTEGER,
    right_id INTEGER,

    PRIMARY KEY (left_id, right_id)
);

CREATE COLUMN TABLE Meetup.Groups_Topics (
    left_id INTEGER,
    right_id INTEGER,

    PRIMARY KEY (left_id, right_id)
);

CREATE COLUMN TABLE Meetup.GroupSponsors (
    foreign_id INTEGER, --GROUP_ID
    details NCLOB,
    image_url NVARCHAR(255),
    info NCLOB,
    name NVARCHAR(255),
    url NVARCHAR(255),

    PRIMARY KEY (foreign_id, name)
);

CREATE COLUMN TABLE Meetup.Members (
    id INTEGER,
    bio NCLOB,
    city NVARCHAR(255),
    country NVARCHAR(255),
    hometown NVARCHAR(255),
    joined BIGINT,
    lat DOUBLE,
    link NVARCHAR(255),
    lon DOUBLE,
    membership_count INTEGER,
    name NVARCHAR(255),
    other_services_flickr_identifier NVARCHAR(255),
    other_services_linkedin_identifier NVARCHAR(255),
    other_services_tumblr_identifier NVARCHAR(255),
    other_services_twitter_identifier NVARCHAR(255),
    photo_id INTEGER,
    state NVARCHAR(255),
    visited BIGINT,

    PRIMARY KEY (id)
);

CREATE COLUMN TABLE Meetup.Members_Topics (
    left_id INTEGER,
    right_id INTEGER,

    PRIMARY KEY (left_id, right_id)
);

CREATE COLUMN TABLE Meetup.Profiles (
    group_id INTEGER,
    member_id INTEGER,
    additional NCLOB,
    bio NCLOB,
    comment NCLOB,
    created BIGINT,
    member_city NVARCHAR(255),
    member_country NVARCHAR(255),
    member_state NVARCHAR(255),
    name NVARCHAR(255), -- redundant with Member.name referenced by member_id
    photo_photo_id NVARCHAR(255),
    profile_url NVARCHAR(255),
    role NVARCHAR(255),
    site_name NVARCHAR(255),
    site_url NVARCHAR(255),
    status NVARCHAR(255),
    title NVARCHAR(255),
    updated BIGINT,
    visited BIGINT,

    PRIMARY KEY (group_id, member_id)
);

CREATE COLUMN TABLE Meetup.Profiles_Answers (
    left_group_id INTEGER,
    left_member_id INTEGER,
    right_group_id INTEGER,
    right_member_id INTEGER,
    right_question_id INTEGER,

    PRIMARY KEY (left_group_id, left_member_id, right_group_id, right_member_id, right_question_id)
);

CREATE COLUMN TABLE Meetup.RSVPs (
    rsvp_id INTEGER,
    comments NCLOB,
    created BIGINT,
    event_id NVARCHAR(255),
    group_id INTEGER,
    guests INTEGER,
    host INTEGER,
    member_member_id INTEGER,
    mtime BIGINT,
    response NVARCHAR(20),
    venue_id INTEGER,

    PRIMARY KEY (rsvp_id)
);

CREATE COLUMN TABLE Meetup.Topics (
    id INTEGER,
    name NVARCHAR(255),
    urlkey NVARCHAR(255),

    PRIMARY KEY (id)
);

CREATE COLUMN TABLE Meetup.Venues (
    id INTEGER,
    address_1 NVARCHAR(255),
    address_2 NVARCHAR(255),
    address_3 NVARCHAR(255),
    city NVARCHAR(255),
    country NVARCHAR(255),
    lat DOUBLE,
    lon DOUBLE,
    name NVARCHAR(255),
    phone NVARCHAR(255),
    rating Double,
    rating_count INTEGER,
    state NVARCHAR(255),
    venue_url NVARCHAR(255),
    zip NVARCHAR(255),

    PRIMARY KEY (id)
);