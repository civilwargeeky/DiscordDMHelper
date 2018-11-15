import botDiscord, logging, sys

class DiscordFilter(logging.Filter):
  def filter(self, record: logging.LogRecord):
    return int(not any(record.name.startswith(name) for name in ("discord", "websockets", "asyncio")))

log = logging.getLogger() # The root logger
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s'))
handler.addFilter(DiscordFilter())
log.addHandler(handler)

if __name__ == "__main__":
  client, thread = botDiscord.start()

  try:
    print('Press ctrl-C to exit.')
    while True:
      cmd = input("> ")
  except KeyboardInterrupt:
    print("Accepted Keyboard Interrupt!")