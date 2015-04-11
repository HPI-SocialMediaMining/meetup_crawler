import urllib2
import urllib
import json
import serializers
import utilities
from apiKeyManager import APIKeyManager

class Fetcher(object):

  BASE_DATA = {
    'sign' : True,
    'page' : 200,
  }
  ENTITY_DATA = {}
  BASE_URL = 'https://api.meetup.com/2/'

  URL_SUFFIX = None
  SERIALIZER = None

  def __init__(self, persister, logger, data={}):
    super(Fetcher, self).__init__()
    self.data = data
    self.persister = persister
    self.logger = logger

  def get_url_suffix(self):
    return self.URL_SUFFIX

  def get_results(self, start_url):
    url = start_url
    while url:
      response = self.try_get_json(url)
      for result in response['results']:
        yield result
      url = response['meta']['next']

  def try_get_json(self, url):
    def get_json():
      response_raw = urllib2.urlopen(url).read()
      return json.loads(response_raw)

    default_result = {
        'results' : [],
        'meta' : {'next' : None},
    }

    return utilities.try_execution(
        get_json, "Connecting to meetup: " + url, self.logger, default_result)

  def fetch(self, attributes_to_return=['id']):
    attributes = []

    key = APIKeyManager.get_key()
    self.logger.info("Crawling " + self.get_url_suffix()  + " (using key: " + key + ")")
    self.BASE_DATA['key'] = key

    data = dict(self.BASE_DATA.items() + self.ENTITY_DATA.items() + self.data.items())
    get_params = urllib.urlencode(data)
    start_url = self.BASE_URL + self.get_url_suffix() + '?' + get_params

    for result in self.get_results(start_url):
      entity_id = self.get_serializer(result).serialize(attributes_to_return)
      attributes.append(entity_id)

    self.persister.finish()

    return attributes

  def encode(self, name):

    return urllib.quote(name.encode('utf-8'))

  def get_serializer(self, json):

    return self.SERIALIZER(json, self.persister)


class Api1Fetcher(Fetcher):
  """Fetcher for API 1 formats"""

  BASE_URL = 'https://api.meetup.com/'

  def get_results(self, start_url):
    response = self.try_get_json(start_url)
    for result in response:
      yield result


class GroupFetcher(Fetcher):

  URL_SUFFIX = 'groups'
  ENTITY_DATA = {
    'fields' : 'approved,is_simplehtml,join_info,membership_dues,other_services,short_link,sponsors,welcome_message',
  }

  def __init__(self, persister, logger, crawled_city, data={}):
    super(GroupFetcher, self).__init__(persister, logger, data)
    self.crawled_city = crawled_city

  def get_serializer(self, json):
    return serializers.GroupSerializer(json, self.persister, self.crawled_city)


class BoardFetcher(Api1Fetcher):

  SERIALIZER = serializers.BoardSerializer

  def __init__(self, persister, logger, group_url_name, data={}):
    super(BoardFetcher, self).__init__(persister, logger, data)
    self.group_url_name = group_url_name

  def get_url_suffix(self):
    return self.encode(self.group_url_name) + '/boards'

  def fetch_deep(self, attributes_to_return=['id']):
    attributes = self.fetch(attributes_to_return + ['id'])
    for attribute in attributes:
      DiscussionFetcher(self.persister, self.logger, self.group_url_name, attribute['id']).fetch_deep()
    return attributes


class DiscussionFetcher(Api1Fetcher):

  SERIALIZER = serializers.DiscussionSerializer

  def __init__(self, persister, logger, group_url_name, board_id, data={}):
    super(DiscussionFetcher, self).__init__(persister, logger, data)
    self.group_url_name = group_url_name
    self.board_id = board_id

  def get_url_suffix(self):
    return (self.encode(self.group_url_name) + '/boards/' +
        self.encode(str(self.board_id)) + '/discussions')

  def fetch_deep(self, attributes_to_return=['id']):
    attributes = self.fetch(attributes_to_return + ['id'])
    #for attribute in attributes:
    #  DiscussionPostFetcher(self.persister, self.logger, self.group_url_name, self.board_id, attribute['id']).fetch()
    return attributes


class DiscussionPostFetcher(Api1Fetcher):

  SERIALIZER = serializers.DiscussionPostSerializer

  def __init__(self, persister, logger, group_url_name, board_id, discussion_id, data={}):
    super(DiscussionPostFetcher, self).__init__(persister, logger, data)
    self.group_url_name = group_url_name
    self.board_id = board_id
    self.discussion_id = discussion_id

  def get_url_suffix(self):
    return (self.encode(self.group_url_name) + '/boards/' +
        self.encode(str(self.board_id)) + '/discussions/' +
        self.encode(str(self.discussion_id)))


class EventFetcher(Fetcher):

  URL_SUFFIX = 'events'
  SERIALIZER = serializers.EventSerializer
  ENTITY_DATA = {
    'fields' : 'comment_count,event_hosts,featured,is_simplehtml,photo_count,rsvp_rules,simple_html_description,survey_questions,timezone,trending_rank,venue_visibility',
    'status' : 'upcoming,past',
  }

  def fetch_deep(self, attributes_to_return=['id']):
    attributes = self.fetch(attributes_to_return)
    for attribute in attributes:
      RsvpFetcher(self.persister, self.logger, {'event_id' : attribute['id']}).fetch()
    return attributes


class RsvpFetcher(Fetcher):

  URL_SUFFIX = 'rsvps'
  SERIALIZER = serializers.RsvpSerializer


class MemberFetcher(Fetcher):

  URL_SUFFIX = 'members'
  SERIALIZER = serializers.MemberSerializer
  ENTITY_DATA = {
    'fields' : 'messagable,messaging_pref,reachable',
  }


class ProfileFetcher(Fetcher):

  URL_SUFFIX = 'profiles'
  SERIALIZER = serializers.ProfileSerializer
  ENTITY_DATA = {
    'fields' : 'member_city,member_country,member_state',
  }
