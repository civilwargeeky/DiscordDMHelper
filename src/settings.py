import json, logging, os

log = logging.getLogger(__name__)

SETTINGS_FILE = os.path.join(os.getenv('APPDATA'), "DiscordDMHelper", "_settings.json")
if not os.path.exists(os.path.dirname(SETTINGS_FILE)): # Make this directory if it doesn't exist already
  os.makedirs(os.path.dirname(SETTINGS_FILE))

def getFile(*args):
  return os.path.join(os.path.dirname(SETTINGS_FILE), *args)

class SettingsContainer(dict):
  """ Stores settings, but also information about those settings """

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.info = {}

  def newSetting(self, *args, **kwargs):
    if kwargs:
      return self._newSetting(kwargs)
    else:
      for arg in args:
        if not isinstance(arg, dict):
          raise TypeError("Tried to make a new setting list, but argument was type '{}' not 'dict'".format(type(arg)))
        self._newSetting(arg)

  def _newSetting(self, kwargs: dict):
    _required = ["id"]
    #First ensure all required exist
    for key in _required:
      if key not in kwargs:
        raise ValueError("Tried to make a new setting, but key '{}' was not present".format(key))

    _defaults = {
      "name": kwargs["id"],
      # The default value of this option. Originally set to the empty object for the given class
      "default": (kwargs["type"] if "type" in kwargs else str)(),
      # The class used to construct this type. Any time option set, must be of this value
      "type": str,
      # A value to display when the user does a hover over in a GUI
      "hovertext": None,
      # A function to call that returns true if the value is proper, false otherwise
      "verify": None,
      # True if the value should be hidden in a GUI environment
      "hidden": False,
    }

    # Then ensure defaults exist
    for key in _defaults:
      if key not in kwargs:
        kwargs[key] = _defaults[key]

    # Ensure we don't have duplicate keys
    if kwargs["id"] in self.info:
      raise ValueError("tried to make new setting for id '{}' but it already existed".format(kwargs["id"]))

    # Then add in info for this id
    self.info[kwargs["id"]] = kwargs

    # Set the actual value if not set already
    if kwargs["id"] not in self:
      self[kwargs["id"]] = kwargs["default"]

  def getInfo(self, id):
    return self.info[id]

  def __setitem__(self, key, value):
    if key in self.info:
      info = self.info[key]
      if not isinstance(value, info["type"]):
        raise TypeError("setting '{}' should be of type {}, but was of type {}".format(key, info["type"], type(value)))
      if callable(info["verify"]):
        if not info["verify"](value):
          raise ValueError("setting '{}' being set to '{}' failed verification test".format(key, value))
    super().__setitem__(key, value) # If it checks out, set this

# The objects for use
general, discord, gui = SettingsContainer(), SettingsContainer(), SettingsContainer()

_names = {
  "general": general,
  "discord": discord,
  "gui":     gui,
}

def save():
  """ Saves the current settings """
  log.info("Saving settings file")
  with open(SETTINGS_FILE, "w") as file:
    json.dump(_names, file)

_initialCache = {}

def load(initial=False):
  """ Loads the file into our variables in-place. If initial is True, will cache results, any future calls with initial use the cache """
  log.info("Loading settings file")
  try:
    if initial and _initialCache: # If we are initial and we already have cached load, don't go to file
      data = _initialCache
    else:
      with open(SETTINGS_FILE) as file:
        data = json.load(file)
        if initial: # Store this for later
          _initialCache.update(data)
  except FileNotFoundError:
    log.warning("No log file found to load! At '{}'".format(SETTINGS_FILE))
    return
  except json.JSONDecodeError:
    log.error("Settings file was corrupt! Cannot load settings")
    return
  else:
    for name in _names: # Make sure we update in place and don't make new values
      _names[name].clear()
      _names[name].update(data[name])
      
    # Legacy updating code for updating 1.2.2.0 to newer versions
    if "voiceChannel" in _names["discord"] and type(_names["discord"]["voiceChannel"]) == str:
      log.warning("Updating save file to newest version!")
      _names["discord"]["voiceChannel"] = int(_names["discord"]["voiceChannel"])
      save() # Save these changes

def loadInitial():
  return load(initial=True)