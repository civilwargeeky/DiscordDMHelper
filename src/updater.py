import sys
from win32com.client import Dispatch

def getVersion():
  """ Returns the version info of the current executable, or None if the information is unavailable """
  if getattr(sys, 'frozen', False):
    # https://stackoverflow.com/a/2310098/10024365
    ver_parser = Dispatch('Scripting.FileSystemObject')
    info = ver_parser.GetFileVersion(sys.executable)

    if info == 'No Version Information Available':
        return None
    return info
  return None

"""
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the pyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    application_path = sys._MEIPASS
"""