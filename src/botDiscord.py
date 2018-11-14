import audioop, collections, threading
import sounddevice as sd
import asyncio, discord
import logging

from settings import discord as settings, loadInitial, save as saveSettings

log = logging.getLogger(__name__)

class MockFile:
  """
  This is a mock file that will buffer output from a sounddevice recording.
  If not playing, output will not buffered to save RAM
  """
  def __init__(self):
    self.buffer = collections.deque(bytearray(), maxlen=960000) # Limit to ~100kB just in case it's left playing
    self.event = threading.Event()
    self.rateData = None

    self.playing = False # If this is false, nothing is actually buffered

  def play(self):
    """ Begins recording audio and clears the buffer """
    self.playing = True
    self.buffer.clear()  # Clear any existing buffer so there is as little latency as possible

  def stop(self):
    """ Stops recording from the buffer """
    self.playing = False

  def callback(self, indata, frames, time, status):
    """ callback function to give to the sounddevice """
    self.write(indata.copy(order="C"))

  def read(self, numBytes: int or None=None) -> bytes:
    """
    A stream player may read from this to get a sample of the audio
    NOTE: This must return bytes, not a bytearray because the encoder silently fails if you pass anything but bytes
    :param numBytes: The number of bytes to read. Note: If the number of bytes requested is not a multiple of byte width * channels, data will be malformed
    :return: A bytes object containing the oldest requested bytes from the buffer
    """
    if not self.playing: # If a read is requested but we're paused, play to avoid deadlock
      self.play()
    #print("Reading data!", numBytes, len(self.buffer))
    if type(numBytes) == int and numBytes < 0:
      numBytes = None
    toRet = bytearray() # Buffer to put desired bytes into
    while True:
      try:
        toRet.append(self.buffer.popleft())
        if numBytes and len(toRet) >= numBytes:
          return bytes(toRet)
      except IndexError:
        if not numBytes:
          return bytes(toRet)
        else: # If we don't have the requisite number of bytes, wait for more to be written
          #print("Out of bytes and waiting!")
          self.event.clear() # This will likely be set originally, so clear it to indicate we are waiting for more bytes
          self.event.wait()

  def write(self, data):
    """
    Writes binary int16 data to the buffer. Buffer is FIFO. Does not write if not playing
    :param data: The binary data to extend the buffer by.
    """
    #print("Writing data!", len(data), len(self.buffer))
    # Arguments are:
    #   data: Binary PCM fragment to change sample rate of
    #   width: byte width - We set our dtype in recording to int16 because discord expects PCM_16. 16 bits = 2 bytes
    #   channels: How many channels per frame. Discord expects stereo = 2 and our audio device has 2, so it's good
    #   input rate: Our audio device records at 44.1 kHz
    #   output rate: discord expects 48 kHz
    #   stream data: ratecv maintains some state between calls to this, so we record this data for it.
    data, self.rateData = audioop.ratecv(data, 2, 2, 44100, 48000, self.rateData)
    if self.playing: # Note, we do the audioop.ratecv regardless to update rateData
      self.buffer.extend(data)
      self.event.set()


settings.newSetting(
  {
    "id": "botToken",
    "hidden": True
  },
  {
    "id": "gamePlaying",
    "type": dict,
    "default": {"name": "We playin DnD Bois!", "type": 0}
  },
  {
    "id": "voiceChannel",
    "hidden": True
  },
  {
    "id": "commandChar",
    "default": "^",
    "verify": lambda x: len(x) == 1
  },
)


class MyClient(discord.Client):
  def __init__(self, audioFile: MockFile, recordStream, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.audioFile = audioFile
    self.recordStream = recordStream
    self.channel: discord.Channel = None # Voice channel that we are to connect to
    self.vc: discord.VoiceClient = None # Voice Client object of the currently connected channel
    self.player: discord.voice_client.StreamPlayer = None # Audio stream player

  async def updateChannel(self, channel: discord.Channel):
    if type(channel) == str:
      channel = self.get_channel(channel)
      if not channel: # Indicates the channel no longer exists, or we have no permissions
        return log.error("Channel no longer exists to join")
    else: # If we aren't updating from string, change our saved string
      settings["voiceChannel"] = channel.id
      saveSettings()
    self.channel = channel
    if self.vc and self.vc.channel != channel:
      await self.vc.move_to(channel)
    else:
      await self.createVoiceClient()

  async def on_ready(self):
    log.info('Logged on as {0}!'.format(self.user))
    if not discord.opus.is_loaded():
      discord.opus.load_opus('libopus-0.dll')
    if settings["voiceChannel"]: # If we have a saved voice channel, connect immediately
      log.info("Connecting to stored voice channel")
      await self.updateChannel(settings["voiceChannel"])
    else:
      log.info("No voice channel saved, type '{}initialize' while connected to a voice channel".format(settings["commandChar"]))

    await self.changeGame(**settings["gamePlaying"])

  async def on_message(self, message):
    if message.content.startswith(settings["commandChar"]):
      if message.content[1:] == "initialize":
        if message.author.voice_channel:
          log.info("Set new voice channel for future use:"+message.author.voice_channel.id)
          await self.send_message(message.channel, "New Voice Channel Set!")
          await self.updateChannel(message.author.voice_channel)
        else:
          log.info("Tried setting new voice channel, but user was not connected to one")
          await self.send_message(message.channel, "You must be connected to a voice channel to initialize!")
      elif message.content[1:] == "connect":
        await self.createVoiceClient()
      elif message.content[1:] == "disconnect":
        await self.disconnectVoiceClient()
      elif message.content[1:] == "pause":
        self.pause()
      elif message.content[1:] == "set game":
        log.info("Setting new presence")
        await self.send_message(message.channel, "Waiting for new game title")
        newName = await self.wait_for_message(timeout=10, author=message.author)
        newName = newName.content if newName else settings["gamePlaying"]["name"]
        settings["gamePlaying"] = {"name": newName, "type": 0}
        saveSettings()
        await self.changeGame(**settings["gamePlaying"])

  async def changeGame(self, name=None, type=0):
    await self.change_presence(game=discord.Game(name=name, type=type) if name else None)


  async def createVoiceClient(self):
    if not self.vc or not self.vc.is_connected():
      log.debug("Creating new voice client!")
      log.debug("Awaiting voice channel")
      self.vc = await self.join_voice_channel(self.channel)
      log.debug("Voice channel acquired, making player")
      self.player = self.vc.create_stream_player(self.audioFile)
      self.player.start()
      log.debug("Starting player!")

  async def disconnectVoiceClient(self):
    if self.vc and self.vc.is_connected():
      log.info("Disconnecting voice client")
      await self.vc.disconnect()
      self.audioFile.stop() # Stop recording audio, so it's crisp when we read again

  def pause(self):
    if self.vc and self.vc.is_connected() and self.player:
      log.info("Pausing/Resuming Self")
      if self.player.is_playing():
        self.player.pause()
        self.audioFile.stop()
      else:
        self.player.resume() # Should automatically start audioFile when we first read

def start():
  print(discord.version_info)

  # Load settings
  loadInitial()
  if not settings["botToken"]:
    print("Bot token not found! Please make a bot, and paste the token below")
    settings["botToken"] = input("> ")
    saveSettings()

  cableName, cableInputChannels = "CABLE Output (VB-Audio Virtual Cable)", 2

  log.debug("Making input stream")
  log.debug("Searching for cable with name '{}' and input channels #{}".format(cableName, cableInputChannels))
  mockFile = MockFile()  # Make our mock file buffer. It will be ignoring input until specifically told to play
  for deviceNum, device_info in enumerate(sd.query_devices()):
    if device_info["name"] == cableName and device_info["max_input_channels"] == cableInputChannels:
      break
  else: # If we do not break - e.g. we did not find the audio cable
    string = "VB Audio Cable Not Found! Did you install the drivers correctly?"
    log.error(string)
    raise RuntimeError(string)

  stream = sd.InputStream(samplerate=int(device_info['default_samplerate']), device=deviceNum,
                          channels=2, callback=mockFile.callback, dtype="int16")
  stream.start()  # Begin recording to the mock file. Note: This cannot be called in any thread but the main python thread. Otherwise the underlying library errors
  log.info("Started cable input stream")


  client = MyClient(mockFile, stream)

  def run():
    asyncio.set_event_loop(asyncio.new_event_loop())
    client.run(settings["botToken"])

  thread = threading.Thread(target=run, daemon=True)
  thread.start()

  return client, thread # Return these for use with other parts of the program