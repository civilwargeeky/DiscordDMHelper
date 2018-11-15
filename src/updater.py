import logging, sys
import json, os, subprocess
from shutil import copyfileobj
from urllib.error import URLError
from urllib.request import urlopen
from win32com.client import Dispatch

import settings

log = logging.getLogger(__name__)

def getSelfVersion():
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

join = os.path.join #Alias for time saving

#CONSTANTS
UPDATE_LINK = "https://api.github.com/repos/civilwargeeky/DiscordDMHelper/releases/latest"
UPDATE_FILE = settings.getFile("DiscordDMHelperUpdater.exe")

#Downloads a new program installer if the github version is different than ours
#Returns true on successful update (installer should be running), false otherwise
#If there is no internet, raises a RuntimeError stating so
def updateProgram():
  """
  Downloads a new program installer if the github version is newer than ours
  :return:
  """

  try:
    if os.path.exists(UPDATE_FILE):
      os.remove(UPDATE_FILE)
  except PermissionError:
    log.error("Cannot remove installer exe, must be open still")
    return False

  versionCurrent = getSelfVersion()
  if versionCurrent is None:
    log.error("Could not get version from executable file! Not updating.")
    return

  try:
    log.info("Beginning update check")
    with urlopen(UPDATE_LINK) as response:
      updateData = json.loads(response.read().decode("utf-8"))
      versionNew = updateData["tag_name"]
      log.debug("Good data received")
      log.debug(f"Most Recent: {versionNew} | Our Version: {versionCurrent}")
      # Convert them into 4-tuples of int instead of strings
      versionNew, versionCurrent = (tuple(map(int, string.split("."))) for string in (versionNew, versionCurrent))
      if versionNew == versionCurrent:
        log.info("We have the current latest release")
      else:
        if "-declineUpdate" in sys.argv: # Allow user to decline updating
          log.info("Update available but user declined update")
          return False
        for i in range(len(versionCurrent)):
          if versionCurrent[i] > versionNew[i]:
            log.info("We have a version more current than the latest release!")
            break
          elif versionCurrent[i] < versionNew[i]:
            try: #After this point, we want another exception handler that will stop the program with error, because the user expects a download to be happening
              log.info("Older version installed! Updating to version" + ".".join(map(str, versionNew)))
              fileData = updateData["assets"][0]
              webAddress = fileData["browser_download_url"]
              #                                used to be 'fileData["name"]'
              with urlopen(webAddress) as webFile, open(UPDATE_FILE, "wb") as file:
                log.debug(f"Downloading new file from {webAddress}")
                #Both file and webfile are automatically buffered, so this is fine to do
                copyfileobj(webFile, file)
              subprocess.Popen(UPDATE_FILE) #Call this file and then exit the program
              return True
            except IndexError: #No binary attached to release -- no assets (probably)
              #In future we might check updates before this one, to ensure we are somewhat updated
              log.error("No binary attached to most recent release!")
            except BaseException as e: #BaseException because return statement in finally stops anything from getting out
              log.error("Error in downloading new update!", exc_info=e)
            break
  except URLError:
    log.warning("Not connected to the internet!")
    raise RuntimeError("No internet")
  except Exception as e:
    #Log the error. We still want them to run the program if update was not successful
    log.error("Error in update!", exc_info=e)
    #If we did not return in the function, we did not update properly
  return False
