import logging, sys
import botDiscord, settings, updater

import logger
logger.setup()

log = logging.getLogger(__name__)

if __name__ == "__main__":
  isUpdating = updater.updateProgram()
  if isUpdating:
    log.info("Program updating! Exiting this instance")
    sys.exit()

  client, thread, clientLoop = botDiscord.start()
  def getHelp():
    return """
  Command Prompt Commands (only need first letter):
    (h)elp: display this
    (p)ause: Pauses the currently playing stream. Plays if paused
    (s)et [text to set]: Set's the bot's "Now Playing" to the argument
    (c)har [character]: Set's the bot's command character, currently "{0}"
                        discord commands must start with this character
    (x)it: "Exit", logs out gracefully
  Discord Bot Commands (all should be prefixed with prefix character ({0})):
    initialize: Set the voice channel the current user is connected to\n    as the active voice channel
    connect: Connects the bot to the active voice channel if disonnected
    disconnect: Disconnects the bot from the active voice channel
    pause: Pauses a playing stream, or plays if paused
    set game: Prompts to set the current "now playing" for the bot
  """.format(settings.discord["commandChar"])

  try:
    print('Press ctrl-C to exit. "Help" for commands')
    while True:
      text = input("> ")
      cmd = (text.lower().split() or ["."])[0][0]
      if cmd == "h":
        print(getHelp())
      if cmd == "p":
        client.pause()
      if cmd == "s":
        client.async_changeGame(" ".join(text.split()[1:]))
      if cmd == "c":
        try:
          char = text.split()[1][0]
        except IndexError:
          pass
        else: # If no error
          log.info("Changing command char to '"+char+"'")
          # Set to first character of text after c
          settings.discord["commandChar"] = char
          settings.save()
      if cmd == "x":
        raise KeyboardInterrupt
  except KeyboardInterrupt:
    print("Accepted Keyboard Interrupt!")
    client.async_logout()
    thread.join(timeout=5)
    if thread.is_alive():
      print("Wait for logout timed out")
    else:
      print("Successfully logged out")