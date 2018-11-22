import sys
from PyQt5.QtWidgets import *
from ui.MainWindow import Ui_MainWindow
import os, sounddevice as sd, soundfile as sf
from settings import gui, save, loadInitial

class MainWindow(QMainWindow, Ui_MainWindow):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.setupUi(self)

    self.soundDirectory = None
    self.soundButtons = []

    self.pauseButton.clicked.connect(lambda: print("Pausing!"))
    self.soundsFolderButton.clicked.connect(self.chooseSoundFolder)

    loadInitial()
    if "directory" in gui:
      self.chooseSoundFolder(gui["directory"])

  def chooseSoundFolder(self, directory=None):
    if not directory:
      directory = QFileDialog.getExistingDirectory(self, "Select Soundboard Directory")
      gui["directory"] = directory
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
    data, fs = sf.read(os.path.normpath(path), dtype='float32')
    sd.play(data, fs)
    status = sd.wait()


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