class RelationHandler(object):

  def __init__(self, object_location, object_class):
    self.object_location = object_location
    self.object_class = object_class


class Serializer(object):
  """Abstract class that serializes a JSON object according to parameters
  that are described by its subclasses."""

  TABLE_PREFIX = 'Meetup.'
  # Name of the Table the entity is stored in
  ENTITY_NAME = None
  # Array of strings that contains all the field names that should be stored
  # on the top level, as you would access it in the JS console,
  # e.g. 'foo.bar.value'
  FIELDS = []
  # List of fields that identify the entity
  IDS = ['id']
  # Array of RelationHandlers
  MANY_TO_ONE = []
  # Array of RelationHandlers (as MANY_TO_ONE) that point to an array in the JSON
  MANY_TO_MANY = []
  # Array of RelationHandlers (as MANY_TO_ONE) that point to an array in the JSON
  ONE_TO_MANY = []

  def __init__(self, json, persister, parent_id_values={}):
    super(Serializer, self).__init__()
    self.fields = self.get_fields()
    self.json = json
    self.persister = persister
    self.parent_id_values = parent_id_values

  def get_table_name(self):
    return self.TABLE_PREFIX + self.ENTITY_NAME

  def get_join_table_name(self, object_location):
    return "%s%s_%s" % (self.TABLE_PREFIX, self.ENTITY_NAME, self.escape(object_location))

  def get_fields(self):
    return (self.FIELDS + [(e.object_location + '.id') for e in self.MANY_TO_ONE])

  def get_escaped_fields(self):
    return [self.escape(field) for field in self.get_fields()]

  def escape(self, name):
    return name.replace('.', '_')

  def serialize(self, attributes_to_return=[]):
    self.persister.persist(
      self.get_table_name(), self.get_field_values(), self.get_id_values())

    for handler in self.MANY_TO_ONE:
      value = self.get_value(handler.object_location)
      if value is not None:
        serializer = handler.object_class(value, self.persister)
        serializer.serialize()

    for handler in self.ONE_TO_MANY:
      values = self.get_value(handler.object_location)
      if values is not None:
        for value in values:
          for id_key, id_value in self.get_id_values().iteritems():
            value["foreign_" + id_key] = id_value
          serializer = handler.object_class(value, self.persister)
          serializer.serialize()

    for handler in self.MANY_TO_MANY:
      serializer_class = handler.object_class
      join_table_name = self.get_join_table_name(handler.object_location)
      elements = self.get_value(handler.object_location)

      if elements is not None:
        for element in elements:
          def prefix_dict(dictionary, prefix):
            return {(prefix + key) : value for key, value in dictionary.iteritems()}
          def merge_dicts(dict1, dict2):
            return dict(dict1.items() + dict2.items())

          right = serializer_class(element, self.persister, self.get_id_values())
          right.serialize()

          id_values = merge_dicts(
              prefix_dict(self.get_id_values(), 'left_'),
              prefix_dict(right.get_id_values(), 'right_'))
          values = self.get_id_values_list() + right.get_id_values_list()
          self.persister.persist(join_table_name, values, id_values)

    return {self.escape(attr) : self.get_value(attr) for attr in attributes_to_return}

  def get_field_values(self):
    return [self.get_value(field) for field in self.fields]

  def get_id_values(self):
    return {self.escape(field) : self.get_value(field) for field in self.IDS}

  def get_id_values_list(self):
    return [self.get_value(field) for field in self.IDS]

  def get_value(self, key, json=None):
    value = self.json if json is None else json

    for key in key.split('.'):
      if value is None or not key in value:
        return self.parent_id_values.get(key)
      value = value[key]

    return value


class GroupSerializer(Serializer):

  class CategorySerializer(Serializer):
    ENTITY_NAME = 'Categories'
    FIELDS = ['id', 'name', 'shortname']

  class GroupQuestionSerializer(Serializer):
    ENTITY_NAME = 'GroupQuestions'
    FIELDS = ['id', 'question']

  class TopicSerializer(Serializer):
    ENTITY_NAME = 'Topics'
    FIELDS = ['id', 'name', 'urlkey']

  class SponsorSerializer(Serializer):
    ENTITY_NAME = 'GroupSponsors'
    FIELDS = ['foreign_id', 'details', 'info', 'image_url', 'name', 'url']
    IDS = ['foreign_id', 'name']

  ENTITY_NAME = 'Groups'
  #TODO: add membership_dues.reasons, membership_dues.reasons_other
  FIELDS = ['id', 'crawled_city', 'crawl_status', 'approved', 'city', 'country', 'created', 'description', 'is_simplehtml', 'join_mode', 'lat', 'link', 'list_mode', 'lon', 'members', 'membership_dues.currency', 'membership_dues.fee', 'membership_dues.fee_desc', 'membership_dues.required', 'name', 'organizer.member_id', 'other_services.flickr.identifier', 'other_services.linkedin.identifier', 'other_services.tumblr.identifier', 'other_services.twitter.identifier', 'primary_topic', 'rating', 'short_link', 'simple_html_description', 'state', 'timezone', 'urlname', 'visibility', 'welcome_message', 'who']
  MANY_TO_ONE = [
      RelationHandler('category', CategorySerializer),
  ]
  ONE_TO_MANY = [
      RelationHandler('sponsors', SponsorSerializer)
  ]
  MANY_TO_MANY = [
      RelationHandler('join_info.questions', GroupQuestionSerializer),
      RelationHandler('topics', TopicSerializer),
  ]

  def __init__(self, json, persister, crawled_city, parent_id_values={}):
    super(GroupSerializer, self).__init__(json, persister, parent_id_values)
    self.crawled_city = crawled_city

  def get_value(self, key, json=None):
    if key == 'crawled_city':
      return self.crawled_city
    if key == 'crawl_status':
      return 'new'
    return super(GroupSerializer, self).get_value(key, json)


class BoardSerializer(Serializer):

  ENTITY_NAME = 'Boards'
  FIELDS = ['id', 'created', 'discussion_count', 'group.id', 'name', 'post_count', 'updated']


class DiscussionSerializer(Serializer):

  ENTITY_NAME = 'Discussions'
  FIELDS = ['id', 'board.id', 'created', 'reply_count', 'started_by.name', 'updated']


class DiscussionPostSerializer(Serializer):

  ENTITY_NAME = 'DiscussionPosts'
  FIELDS = ['id', 'body', 'created', 'discussion.id', 'in_reply_to', 'member.id', 'subject', 'updated']


class EventSerializer(Serializer):

  class EventSurveyQuestionSerializer(Serializer):
    ENTITY_NAME = 'EventQuestions'
    FIELDS = ['id', 'question', 'required']

  class VenueSerializer(Serializer):
    ENTITY_NAME = 'Venues'
    FIELDS = ['id', 'address_1', 'address_2', 'address_3', 'city', 'country', 'lat', 'lon', 'name', 'phone', 'rating', 'rating_count', 'repinned', 'state', 'zip']

  ENTITY_NAME = 'Events'
  FIELDS = ['id', 'comment_count', 'created', 'description', 'duration', 'event_url', 'featured', 'fee.accepts', 'fee.amount', 'fee.currency', 'fee.description', 'fee.label', 'fee.required', 'group.id', 'headcount', 'how_to_find_us', 'is_simplehtml', 'maybe_rsvp_count', 'name', 'photo_count', 'photo_url', 'rating.average', 'rating.count', 'rsvp_limit', 'rsvp_rules.close_time', 'rsvp_rules.closed', 'rsvp_rules.guest_limit', 'rsvp_rules.open_time', 'rsvp_rules.waitlisting', 'simple_html_description', 'status', 'time', 'timezone', 'trending_rank', 'updated', 'utc_offset', 'venue_visibility', 'visibility', 'why', 'yes_rsvp_count']
  MANY_TO_ONE = [
      RelationHandler('venue', VenueSerializer),
  ]
  # TODO: Add event_hosts
  MANY_TO_MANY = [
      RelationHandler('survey_questions', EventSurveyQuestionSerializer),
  ]


class RsvpSerializer(Serializer):

  ENTITY_NAME = 'RSVPs'
  IDS = ['rsvp_id']
  FIELDS = ['rsvp_id', 'comments', 'created', 'event.id', 'group.id', 'guests', 'host', 'member.member_id', 'mtime', 'response', 'venue_id']


class MemberSerializer(Serializer):

  ENTITY_NAME = 'Members'
  FIELDS = ['id', 'bio', 'city', 'country', 'hometown', 'joined', 'lat', 'link', 'lon', 'membership_count', 'name', 'other_services.flickr.identifier', 'other_services.linkedin.identifier', 'other_services.tumblr.identifier', 'other_services.twitter.identifier', 'photo_id', 'state', 'visited']
  MANY_TO_MANY = [
      RelationHandler('topics', GroupSerializer.TopicSerializer),
  ]


class ProfileSerializer(Serializer):

  class GroupQuestionAnswerSerializer(Serializer):
    ENTITY_NAME = 'GroupAnswers'
    IDS = ['group_id', 'member_id', 'question_id']
    FIELDS = ['group_id', 'member_id', 'question_id', 'question', 'answer']


  ENTITY_NAME = 'Profiles'
  IDS = ['group.id', 'member_id']
  FIELDS = ['group.id', 'member_id', 'additional', 'bio', 'comment', 'created', 'member_city', 'member_country', 'member_state', 'name', 'photo.photo_id', 'profile_url', 'role', 'site_name', 'site_url', 'status', 'title', 'updated', 'visited']
  MANY_TO_MANY = [
      RelationHandler('answers', GroupQuestionAnswerSerializer)
  ]
