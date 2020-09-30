from typing import Any, Callable
from os import path
from PyQt5.QtCore import QObject, pyqtSignal


class Validator:
    """ These are made for user settings where you always want
    a good value, even when you've loaded a bad value.

    Instead of returning "is or is not valid", these return a default
    value if it cannot make the given value work.
    """

    def __init__(self):
        self._validate = None

    def validate(self, x, default):
        try:
            return x if not self._validate else self._validate(x, default)
        except ValueError:
            return default

    @staticmethod
    def _booleanValidator(x, default):
        if isinstance(x, str):
            x = x.lower()
            if x == "true":
                return True
            if x == "false":
                return False
        return x if isinstance(x, bool) else default

    @staticmethod
    def _intValidator(x, default):
        return int(x) if x is not None else default

    def _rangeValidator(self, x, default):
        if x is None:
            return default
        x = int(x)
        if x >= self._min and x <= self._max:
            return x
        return default

    def _stringListValidator(self, x, default):
        if x is None:
            return default
        x = str(x)
        if x:
            x = x.lower()
            if x in self._values:
                return x
        return default

    def _folderValidator(self, x, default):
        if x is None:
            return default
        if not path.isdir(x):
            return default
        if not self._allowSymlinks and path.islink(x):
            return default
        if self._fileOrFolder and not path.exists(x + "/" + self._fileOrFolder):
            return default
        return x

    def _fileValidator(self, x, default):
        if x is None:
            return default
        if not path.isFile(x):
            return default
        if not self._allowSymlinks and path.islink(x):
            return default
        return x

    @classmethod
    def default(cls):  # This is just for consistency.
        return cls()

    @classmethod
    def boolean(cls):
        c = cls()
        c._validate = Validator._booleanValidator
        return c

    @classmethod
    def integer(cls):
        c = cls()
        c._validate = Validator._intValidator
        return c

    @classmethod
    def range(cls, lo, hi):
        c = cls()
        c._min = lo
        c._max = hi
        c._validate = c._rangeValidator
        return c

    @classmethod
    def stringList(cls, values):
        c = cls()
        c._values = values
        c._validate = c._stringListValidator
        return c

    @classmethod
    def folder(cls, fileOrFolder=None, allowSymlinks=False):
        c = cls()
        c._fileOrFolder = fileOrFolder
        c._allowSymlinks = allowSymlinks
        c.validate = c._folderValidator
        return c

    @classmethod
    def file(cls, allowSymlinks=False):
        c = cls()
        c._allowSymlinks = False
        c.validate = c._fileValidator
        return c

    @classmethod
    def custom(cls, validator: Callable[[Any, Any], Any], **kwargs):
        c = cls()
        c.validate = validator
        for k, v in kwargs.items():
            setattr(c, k, v)
        return c


class SettingItem(QObject):
    settingChanged = pyqtSignal(int)

    def __init__(self, key, name="", default=None, validator=Validator()):
        super().__init__()
        self._key, self._default, self._validator = key, default, validator
        self._name = str(name) if name else str(key)
        self._value = default

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return self.key == other.key

    def __str__(self):
        return "{}. {}: [{}] [{}]".format(int(self.key), self.name, self.default, self.value)

    @property
    def key(self):
        return self._key

    @property
    def name(self):
        return self._name

    @property
    def default(self):
        return self._default

    @property
    def validator(self):
        return self._validator

    @validator.setter
    def validator(self, value):
        self._validator = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        newValue = self.validator.validate(value, self.default)
        if self._value != newValue:
            self._value = newValue
            self.settingChanged.emit(self.key)


class SettingsBase(QObject):
    """ After the settings have been initialized using `add(...)`, access setting values like a list

    s = Settings()
    s.add(key, name, default, validator)
    v = s[key]
    s[key] = v

    """

    settingChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._settings = {}

    def __getitem__(self, key):
        return self._settings[key].value

    def __setitem__(self, key, value):
        self._settings[key].value = value

    def __delitem__(self, key):
        setting = self._settings.get(key)
        if setting:
            setting.settingChanged.disconnect(self.settingChanged)
            del self._settings[key]

    def __len__(self):
        return len(self._settings)

    def __iter__(self):
        return self._settings.__iter__()

    def __str__(self):
        r = ""
        for s in self._settings.values():
            r += str(s) + "\n"
        return r

    def contains(self, key):
        return self._settings.contains(key)

    def clear(self):
        return self._settings.clear()

    def add(self, key, name="", default=None, validator=None, value=None):
        settings = SettingItem(key, name, default, validator)
        self._settings[key] = settings
        return settings

    def value(self, key):
        return self._settings.get(key)

    def setting(self, key):
        return self._settings.get(key, None)

