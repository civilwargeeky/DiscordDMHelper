import zipfile, urllib.request as request, sys, io, os, shutil, time

CABLE_DIR = "audioCable"
CABLE_URL = "https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack43.zip"
EXE_VERSION_FILE_TEMPLATE = "file_version_info_template.py"
EXE_VERSION_FILE = "file_version_info.py"

### STEP 0: Delete files from building if asked ###
if "clean" in sys.argv:
  print("Deleting all extra files")
  for dir in ("audioCable", "build", "dist"):
    shutil.rmtree(dir)
  for file in (EXE_VERSION_FILE,):
    os.remove(file)
  sys.exit(0)

### STEP 1: Update our version and put it into our exe version file ###
with open("version.txt") as file:
  info = file.read().strip()
  print("Loaded", info)

version = tuple(list(map(int, info.split("."))))

print("Updating version file!")
with open("version.txt") as file:
  # Makes a 4-tuple of version ints
  version = tuple(list(map(int, file.read().strip().split("."))))
oldVersion = version[:]

# Update the current version if requested
if "major" in sys.argv:
  version = tuple([version[0]+1, 0, 0, 0])
elif "minor" in sys.argv:
  version = tuple([version[0], version[1]+1, 0, 0])
elif "revision" in sys.argv:
  version = tuple([version[0], version[1], version[2]+1, 0])
else: # This is for like bugfixes and stuff
  version = tuple([version[0], version[1], version[2], version[3]+1])

if version != oldVersion: # If our version updated, update version file
  print("Updating version file to", ".".join(map(str, version)))
  with open("version.txt", "w") as file:
    file.write(".".join(map(str, version)))

# Update our executable version file
with open(EXE_VERSION_FILE_TEMPLATE) as fileIn, open(EXE_VERSION_FILE, "w") as fileOut:
  fileOut.write(fileIn.read().format(repr(version), ".".join(map(str, version))))

  
### STEP 2: Download the audio cable files if necessary
  
buffer = io.BytesIO()

try:
  print("Downloading zip file from", CABLE_URL)
  with request.urlopen(CABLE_URL) as file:
    buffer.write(file.read())
except:
  print("Could not get new files from internet")
else:
  try:
    print("Making directory")
    os.mkdir(CABLE_DIR)
  except FileExistsError:
    print("Except it already existed, so remove all files first")
    shutil.rmtree(CABLE_DIR)
    os.mkdir(CABLE_DIR)

print("Extracting files to", CABLE_DIR)
zip = zipfile.ZipFile(buffer)
zip.extractall(CABLE_DIR)

### STEP 3: Run the installer ###
print(">>> Building Executable")
os.system("pyinstaller _build.spec")

### STEP 4: Run the installer compiler ###
print(">>> Making installer")
os.system('"C:\Program Files (x86)\Inno Setup 5\Compil32.exe" /cc _build.iss')
print(">>> Making installer complete")

time.sleep(1)