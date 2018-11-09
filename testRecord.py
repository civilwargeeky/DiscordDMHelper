"""Create a recording with arbitrary duration.

PySoundFile (https://github.com/bastibe/PySoundFile/) has to be installed!

"""
import argparse
import tempfile
import queue
import sys


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
parser.add_argument(
    '-c', '--channels', type=int, default=2, help='number of input channels')
parser.add_argument(
    'filename', nargs='?', metavar='FILENAME',
    help='audio file to store recording to')
parser.add_argument(
    '-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
args = parser.parse_args()


class MockFile:
    def __init__(self):
        self.q = queue.Queue()
        self.toTell = 0

    def read(self):
        return self.q.get()

    def write(self, data):
        self.q.put(data)
        self.toTell += len(data)

    def seek(self, offset, whence):
        print("Seeking to", offset, whence)
        self.toTell = offset

    def tell(self):
        print("Telling")
        return 0

yes = MockFile()

try:
    import sounddevice as sd
    import soundfile as sf
    import numpy  # Make sure NumPy is loaded before it is used in the callback
    assert numpy  # avoid "imported but unused" message (W0611)


    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        # soundfile expects an int, sounddevice provides a float:
        args.samplerate = int(device_info['default_samplerate'])
        print("Sample Rate: ", args.samplerate)
    if args.filename is None:
        args.filename = tempfile.mktemp(prefix='delme_rec_unlimited_',
                                        suffix='.wav', dir='')

    print(args.channels)
    print(device_info)
    input()
    q = queue.Queue()

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.put(indata.copy(order="C"))

    print("Starting input stream...")

    stuff = None
    import audioop

    buffer = bytearray()

    # Make sure the file is opened before recording anything:
    with open("testtest.wav", "wb") as testFile:
        print("Opening input stream")
        with sd.InputStream(samplerate=args.samplerate, device=args.device,
                            channels=args.channels, callback=callback, dtype="int16"):
            print('#' * 80)
            print('press Ctrl+C to stop the recording')
            print('#' * 80)
            while True:
                #file.write(q.get())
                data = q.get()
                print("Type: ", type(data), "\nShape:", data.shape)
                test, stuff = audioop.ratecv(data, 2, args.channels, args.samplerate, 48000, stuff)
                print(len(test))
                print(stuff)
                buffer.extend(test)
                while not yes.q.empty():
                    got = yes.read()
                    print(type(got), len(got), yes.q.empty())
                    testFile.write(got)

except KeyboardInterrupt:
    print('\nRecording finished: ' + repr(args.filename))
    print("Writing file of size:", len(buffer))
    import wave
    with wave.open(args.filename, mode="wb") as newFile:
      newFile.setnchannels(2)
      newFile.setsampwidth(2)
      newFile.setframerate(48000)
      newFile.writeframes(buffer)
    parser.exit(0)


except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))