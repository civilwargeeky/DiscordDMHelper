import logging, sys
import botDiscord, logger, updater

log = logging.getLogger(__name__)

if __name__ == "__main__":
  isUpdating = updater.updateProgram()
  if isUpdating:
    log.info("Program updating! Exiting this instance")
    sys.exit()

  client, thread = botDiscord.start()

  try:
    print('Press ctrl-C to exit.')
    while True:
      cmd = input("> ")
  except KeyboardInterrupt:
    print("Accepted Keyboard Interrupt!")