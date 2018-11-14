import zipfile, urllib.request as request, sys, io, os, shutil

OUTPUT_DIR = "audioCable"

url = sys.argv[1]


with open("version.txt") as file:
  info = file.read().strip()
  
version = tuple(list(map(int, info.split("."))) + [0])

if url == "post":
  if False:
    print("Deleting all extra files")
    for dir in ("audioCable", "build", "dist"):
      shutil.rmtree(dir)
  
else:
  print("Updating version file!")
  with open("version.txt") as file:
    # Makes a 4-tuple of version ints
    version = tuple(list(map(int, file.read().strip().split(".")))+[0])
  
  fileNameIn = "file_version_info_template.py"
  fileNameOut = "file_version_info.py"
  
  with open(fileNameIn) as fileIn, open(fileNameOut, "w") as fileOut:
    fileOut.write(fileIn.read().format(repr(version), ".".join(map(str, version))))

  buffer = io.BytesIO()

  try:
    print("Downloading zip file from", url)
    with request.urlopen(url) as file:
      buffer.write(file.read())
  except:
    print("Could not get new files from internet")
  else:
    try:
      print("Making directory")
      os.mkdir(OUTPUT_DIR)
    except FileExistsError:
      print("Except it already existed, so remove all files first")
      shutil.rmtree(OUTPUT_DIR)
      os.mkdir(OUTPUT_DIR)

  print("Extracting files to", OUTPUT_DIR)
  zip = zipfile.ZipFile(buffer)
  zip.extractall(OUTPUT_DIR)