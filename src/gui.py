import sys
from PyQt5.QtWidgets import *
from ui.MainWindow import Ui_MainWindow
import os, sounddevice as sd, soundfile as sf
from settings import gui as guiSettings, save, loadInitial

guiSettings.newSetting(
  {
    "id": "soundboardDirectory",
    "default": "",
    "hidden": True,
    "verify": lambda x: not x or os.path.isdir(x)
  },
)
loadInitial()

class MainWindow(QMainWindow, Ui_MainWindow):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.setupUi(self)

    # The current directory we look for music in
    self.soundDirectory = None
    # Each element is three-list of (file name, display name, resource)
    # Resource may either be a file name (or a file name in tmp or appdata for converted) or a numpy array
    # representing the sound
    self.soundButtons = []

    self.pauseButton.clicked.connect(lambda: print("Pausing!"))
    self.soundsFolderButton.clicked.connect(self.chooseSoundFolder)

    if "soundboardDirectory" in guiSettings:
      self.chooseSoundFolder(guiSettings["soundboardDirectory"])

  def chooseSoundFolder(self, directory=None):
    if not directory: # If a directory is not passed in as argument
      directory = QFileDialog.getExistingDirectory(self, "Select Soundboard Directory")
      guiSettings["soundboardDirectory"] = directory
      save()
    if directory:
      soundButton: QAbstractButton
      for soundButton in self.soundButtons:
        soundButton.deleteLater()
      self.soundDirectory = directory # For future use
      for root, dirs, files in os.walk(directory):
        dirs.clear() # Do not recurse into subdirs
        i = 0
        j = 0
        for file in files:
          if file.endswith(".wav"):
            button = QPushButton(self.soundsAreaContent)
            button.setText(file)
            print(file)
            button.clicked.connect(lambda *, test=file: self.playSound(os.path.join(root, test)))
            self.soundButtons.append(button)
            self.soundsAreaLayout.addWidget(button, i, j)
            j += 1
            if j > 3:
              i += 1
              j = 0

  def playSound(self, path):
    print("Playing sound!", path)
    try:
      data, fs = sf.read(os.path.normpath(path), dtype='float32')
      num = int(1*fs)
      for i in range(num):
        data[i] *= i/num

      num = int(1 * fs)
      for i in range(num):
        data[-i] *= i / num

      sd.play(data, fs)
      status = sd.wait()
    except Exception as e:
      print(e, type(e))


class App(QApplication):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.mainWindow = MainWindow()
    self.mainWindow.show()

def run():
  app = App(sys.argv)
  sys.exit(app.exec_())

if __name__ == "__main__":
  run()