import logging, sys
import botDiscord, updater

log = logging.getLogger(__name__)

if __name__ == "__main__":
  isUpdating = updater.updateProgram()
  if isUpdating:
    log.info("Program updating! Exiting this instance")
    sys.exit()

  client, thread, clientLoop = botDiscord.start()
  helpString = """
  Command Prompt Commands (only need first letter):
    (h)elp: display this
    (p)ause: Pauses the currently playing stream. Plays if paused
    (s)et [text to set]: Set's the bot's "Now Playing" to the argument
  Discord Bot Commands (all should be prefixed with caret (^)):
    initialize: Set the voice channel the current user is connected to\n    as the active voice channel
    connect: Connects the bot to the active voice channel if disonnected
    disconnect: Disconnects the bot from the active voice channel
    pause: Pauses a playing stream, or plays if paused
    set game: Prompts to set the current "now playing" for the bot
  """

  try:
    print('Press ctrl-C to exit. "Help" for commands')
    while True:
      text = input("> ")
      cmd = (text.lower().split() or ["."])[0][0]
      if cmd == "h":
        print(helpString)
      if cmd == "p":
        client.pause()
      if cmd == "s":
        client.async_changeGame(" ".join(text.split()[1:]))
  except KeyboardInterrupt:
    print("Accepted Keyboard Interrupt!")
    client.async_logout()
    print("Finished logging out")