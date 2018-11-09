
import threading
import collections
import audioop

import queue
import sys
import sounddevice as sd
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)

class MockFile:
  def __init__(self):
    self.buffer = collections.deque(bytearray())
    self.event = threading.Event()
    self.rateData = None
    self.i = 0
    self.hasRead = False

  def read(self, numBytes=None):
    if not self.hasRead:
      self.buffer.clear()
      self.hasRead = True
    print("Reading data!", numBytes)
    if type(numBytes) == int and numBytes < 0:
      numBytes = None
    toRet = bytearray()
    added = 0
    while True:
      try:
        toRet.append(self.buffer.popleft())
        added += 1
        if numBytes and added >= numBytes:
          return bytes(toRet)
      except IndexError:
        if not numBytes and len(toRet) > 0:
          return bytes(toRet)
        else: # If we don't have the requisite number of bytes, wait for more to be written
          print("Out of bytes and waiting!")
          self.event.wait()
          self.event.clear()

  def write(self, data):
    self.i += 1
    print("Writing data!", len(data), self.i, len(self.buffer))
    data, self.rateData = audioop.ratecv(data, 2, 2, 44100, 48000, self.rateData)
    self.buffer.extend(data)
    self.event.set()

mockFile = MockFile()

def callback(indata, frames, time, status):
  #print("Calling back callback?")
  if status:
    print(status, file=sys.stderr)
  mockFile.write(indata.copy(order="C"))


buffer = bytearray()

"""
print("Opening input stream")
with sd.InputStream(samplerate=44100, device=18,
                    channels=2, callback=callback, dtype="int16"):
    print('#' * 80)
    print('press Ctrl+C to stop the recording')
    print('#' * 80)
    while True:
        #file.write(q.get())
        data = mockFile.read()
        print("Type: ", type(data))
        print(len(data))
"""






import discord
import asyncio
import threading
import audioop

import sys
import sounddevice as sd
import numpy as np
assert np
import threading
import queue
import collections
import io

print(discord.version_info)

"""
print("Testing audio device?")
device_info = sd.query_devices(18, 'input')
# soundfile expects an int, sounddevice provides a float:
samplerate = int(device_info['default_samplerate'])
mockFile.buffer.clear()
test = sd.InputStream(samplerate=samplerate, device=18,
                                   channels=2, callback=callback, dtype="int16")
print(dir(test))
test.start()
input()
"""

print("Making input stream")
device_info = sd.query_devices(18, 'input')
# soundfile expects an int, sounddevice provides a float:
samplerate = int(device_info['default_samplerate'])
stream = sd.InputStream(samplerate=samplerate, device=18,
                                   channels=2, callback=callback, dtype="int16")
stream.start()
print("Started stream")

"""
import wave, time
time.sleep(5)
stream.stop()
with wave.open("newTest.wav", mode="wb") as newFile:
  newFile.setnchannels(2)
  newFile.setsampwidth(2)
  newFile.setframerate(48000)
  newFile.writeframes(mockFile.read())
sys.exit(0)
"""


class MyClient(discord.Client):
  async def on_ready(self):
    print('Logged on as {0}!'.format(self.user))
    print("Is opus loaded?", discord.opus.is_loaded())
    if not discord.opus.is_loaded():
      discord.opus.load_opus('libopus-0.dll')

  async def on_message(self, message):
    print(dir(message))
    print(dir(message.author))
    print(dir(message.author.voice_channel))
    print(message.author.voice_channel.type)
    print(type(message.author.voice_channel))
    print('Message from {0.author}: {0.content}'.format(message))
    if "test" in message.content:
      await self.send_message(message.channel, "Test!")
    if "play" in message.content:


      print("Acquiring Voice Client!")
      vc = await self.join_voice_channel(message.author.voice_channel)
      print("Voice client acquired!")
      player = vc.create_ffmpeg_player('test.wav', after=lambda: print('done'))
      print("Created player!")
      player.start()
      print("Playing")

    if "stop" in message.content:
      print("Logging out")
      await self.logout()
      sys.exit()

    if message.content == "m":
      print("Starting content streaming!")

      print("Mock buffer size:", len(mockFile.buffer))
      mockFile.buffer.clear()
      print("Mock buffer size:", len(mockFile.buffer))
      print("Samples:", samplerate)
      print("Device:", device_info)
      print("Awaiting voice channel")
      vc = await self.join_voice_channel(message.author.voice_channel)
      print("Starting player")
      vc.encoder_options(sample_rate=48000)
      self.player = vc.create_stream_player(mockFile, after=lambda: stream.close())
      self.player.run()

    if message.content == "s":
      stream.stop()
      self.player.stop()


client = MyClient()

def run():
  asyncio.set_event_loop(asyncio.new_event_loop())
  client.run('NotMyActualKey')

thread = threading.Thread(target=run, daemon=True)
thread.start()
while not input():
  pass