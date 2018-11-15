import botDiscord, logger, updater

if __name__ == "__main__":
  client, thread = botDiscord.start()

  try:
    print('Press ctrl-C to exit.')
    while True:
      cmd = input("> ")
  except KeyboardInterrupt:
    print("Accepted Keyboard Interrupt!")