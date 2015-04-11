import logging
import traceback
import time
import random

def logger_with_name(name):
  extra = {'thread_name':name}
  logger = logging.getLogger(name)
  logger.setLevel(logging.DEBUG)
  sh = logging.StreamHandler()
  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(thread_name)s: %(message)s')
  sh.setFormatter(formatter)
  logger.addHandler(sh)
  logger = logging.LoggerAdapter(logger, extra)
  return logger

MAX_RETRY = 20

def try_execution(f, operation, logger, default_result=None):

  for i in range(MAX_RETRY):
    try:
      return f()
    except:
      wait_time = random.randint(0, 15)
      logger.warning(traceback.format_exc())
      logger.warning("Failed: " + operation)
      logger.warning("Try %d of %d", i + 1, MAX_RETRY)
      if i < MAX_RETRY - 1:
        logger.info("Next retry in %d s", wait_time)
        time.sleep(wait_time)

  logger.error("Operation failed %d times and was not completed", MAX_RETRY)
  return default_result
