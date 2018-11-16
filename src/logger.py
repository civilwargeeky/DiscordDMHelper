import logging, sys

# Discord.py uses the logging module, but I don't care about it
class DiscordFilter(logging.Filter):
  def filter(self, record: logging.LogRecord):
    return int(not any(record.name.startswith(name) for name in ("discord", "websockets", "asyncio")))

log = logging.getLogger() # The root logger
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
#handler.setFormatter(logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s'))
handler.setFormatter(logging.Formatter('%(levelname)s (%(name)s): %(message)s'))
handler.addFilter(DiscordFilter())
log.addHandler(handler)

def setup():
  """ May do something in the future, but for now just allows us to import without Unused import exception """
  pass