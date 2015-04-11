import threading

class APIKeyManager(object):
  API_keys = [] #insert Meetup API Keys as Strings here to allow the crawler access to Meetup
  current_index = 0
  request_lock = threading.Lock()

  @staticmethod
  def get_key():
    APIKeyManager.request_lock.acquire()
    key = APIKeyManager.API_keys[APIKeyManager.current_index]
    APIKeyManager.current_index = (APIKeyManager.current_index + 1) % len(APIKeyManager.API_keys)
    APIKeyManager.request_lock.release()
    return key