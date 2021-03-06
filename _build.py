import zipfile, urllib.request as request, sys, io, os, shutil, time
import requests, zipfile, tarfile, io

"""
This file builds the DiscordDMHelper project including actions such as
1) Updating our version file
2) Downloading any binary files that need to be packaged with the installer
3) Running pyinstaller (using commandline installed pyinstaller, ensure this is the correct version)
4) Packaging the executable into an installer using Inno Setup Compiler

It has several command line arguments which are specified below
  With no arguments it builds and increments the bugfix part of version (4th part of tuple)
  revision: builds and increments the revision part of version (3rd part of tuple)
  minor: builds and increments the minor part of version (2nd part of tuple)
  major: builds and increments the major part of version (1st part of tuple)
  specific [version]: builds and sets the version to [version] if given in the correct format
  clean: clears the build and dist folders and any other build artifacts before exiting
"""

CABLE_DIR  = "audioCable"
CABLE_URL  = "https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack43.zip"
INNO_SETUP = '"C:\Program Files (x86)\Inno Setup 5\Compil32.exe"'
EXE_VERSION_FILE_TEMPLATE = "file_version_info_template.py"
EXE_VERSION_FILE = "file_version_info.py"

def updateVersionFile(version):
  if isinstance(version, str):
    version = tuple(map(int, version.split(".")))

  print("Updating version file to", ".".join(map(str, version)))
  with open("version.txt", "w") as file:
    file.write(".".join(map(str, version)))

  # Update our executable version file
  with open(EXE_VERSION_FILE_TEMPLATE) as fileIn, open(EXE_VERSION_FILE, "w") as fileOut:
    fileOut.write(fileIn.read().format(repr(version), ".".join(map(str, version))))



startTime = time.time()

### STEP 0: Delete files from building if asked ###
if "clean" in sys.argv:
  print("Deleting all extra files")
  for dir in ("audioCable", "ffmpeg", "build", "dist"):
    try:
      shutil.rmtree(dir)
      print("Deleted:", dir)
    except FileNotFoundError:
      print("Not found:", dir)
  for file in (EXE_VERSION_FILE,):
    os.remove(file)
  sys.exit(0)

### STEP 1: Update our version and put it into our exe version file ###
with open("version.txt") as file:
  originalVersion = file.read().strip()
  print("Loaded", originalVersion)

version = tuple(list(map(int, originalVersion.split("."))))

print("Updating version file!")
with open("version.txt") as file:
  # Makes a 4-tuple of version ints
  version = tuple(list(map(int, file.read().strip().split("."))))
oldVersion = version[:]

# Update the current version if requested
if "specific" in sys.argv: # They can update it to a specific version but we have to verify it
  try:
    strVersion = sys.argv[sys.argv.index("specific")+1]
    version = tuple([int(part) for part in strVersion.split(".")])
    if len(version) != 4 or any(part < 0 for part in version):
      raise ValueError
  except IndexError:
    print("No version number found in specific building. Check command line arguments")
    raise RuntimeError("Improper Version")
  except ValueError:
    print("Version number was not a proper string in the format X.X.X.X")
    raise RuntimeError("Improper Version")
  
elif "major" in sys.argv:
  version = tuple([version[0]+1, 0, 0, 0])
elif "minor" in sys.argv:
  version = tuple([version[0], version[1]+1, 0, 0])
elif "revision" in sys.argv:
  version = tuple([version[0], version[1], version[2]+1, 0])
else: # This is for like bugfixes and stuff
  version = tuple([version[0], version[1], version[2], version[3]+1])

if version != oldVersion: # If our version updated, update version file
  updateVersionFile(version)
  
### STEP 2: Download the audio cable files if necessary
try:
  buffer = io.BytesIO()

  if not os.path.exists(CABLE_DIR):
    try:
      print("Downloading audio cable zip file from", CABLE_URL)
      with request.urlopen(CABLE_URL) as file:
        buffer.write(file.read())
      print("Extracting files to", CABLE_DIR)
      zip = zipfile.ZipFile(buffer)
      zip.extractall(CABLE_DIR)
    except:
      print("Could not get audio cable from the internet. Stopping build")
      raise RuntimeError("BUILD FAILED")
  else:
    print("Audio Cable Files already exist")

  ### STEP 3: Run the installer ###
  print(">>> Building Executable")
  if os.system("pyinstaller _build.spec"):
    raise OSError("os.system call failed")
  

  ### STEP 4: Run the installer compiler ###
  print(">>> Making installer")
  if os.system(INNO_SETUP+" /cc _build.iss"):
    raise OSError("os.system call failed")
  print(">>> Making installer complete")
except: # If anything goes wrong in building, put our version number back to what it was
  print("<<<>>> Error has occured! Stopping build process")
  updateVersionFile(originalVersion)
finally:
  print(">>> Build Time Elapsed:", time.time()-startTime)
  time.sleep(1)