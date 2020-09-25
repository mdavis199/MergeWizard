from typing import Any, Union, List
from os import path
from PyQt5.QtCore import QVariant, QObject, pyqtSignal
from mobase import IOrganizer
from mergewizard.domain.Profile import Profile
from mergewizard.domain.DataCache import DataCache
from mergewizard.models.MergeModel import MergeModel
from mergewizard.models.PluginModel import PluginModel
from mergewizard.constants import INTERNAL_PLUGIN_NAME, USER_SETTINGS, Setting


# NOTE: Must be a one-to-one mapping with constants.Setting enumeration.


class Context(QObject):
    """
    Context contains data and convenience methods passed between the different WizardPages
    """

    settingChanged = pyqtSignal(int)

    def __init__(self, organizer: IOrganizer):
        super().__init__()
        self.__dataCache: DataCache = DataCache(organizer)
        self.__profile: Profile = Profile(organizer)
        self._enableHidingPlugins = False
        self._hidingMethod = ""
        self._zEditFolder = ""
        self._modNameTemplate = ""
        self._profileNameTemplate = ""
        self._excludeInactiveMods = False
        self.__profile.backupFiles()

    @property
    def dataCache(self) -> DataCache:
        return self.__dataCache

    @property
    def mergeModel(self) -> MergeModel:
        return self.__dataCache.mergeModel

    @property
    def pluginModel(self) -> PluginModel:
        return self.__dataCache.pluginModel

    @property
    def organizer(self) -> IOrganizer:
        return self.__dataCache.organizer

    @property
    def profile(self) -> Profile:
        return self.__profile

    @property
    def enableHidingPlugins(self) -> bool:
        return self._enableHidingPlugins

    @property
    def hidingMethod(self) -> str:
        return self._hidingMethod

    @property
    def zEditFolder(self) -> str:
        return self._zEditFolder

    @property
    def modNameTemplate(self) -> str:
        return self._modNameTemplate

    @property
    def profileNameTemplate(self) -> str:
        return self._profileNameTemplate

    @property
    def excludeInactiveMods(self) -> str:
        return self._excludeInactiveMods

    # ----
    # ---- Semi-private settings stored in modorganizer.ini
    # ----

    def setSetting(self, name: str, value: Any) -> None:
        # self.organizer.setPersistent(INTERNAL_PLUGIN_NAME, name, QVariant(value))
        self.organizer.setPersistent(INTERNAL_PLUGIN_NAME, name, value, True)

    def getSetting(self, name: str, variantType: int, default: Any) -> QVariant:
        # TODO: This always seems to return a string
        # We going to handle just enough types here to get by
        variant = self.organizer.persistent(INTERNAL_PLUGIN_NAME, name)
        if not variant:
            return default
        try:
            if variantType == QVariant.Bool:
                if variant == "false" or (isinstance(variant, bool) and not variant):
                    return False
                if variant == "true" or (isinstance(variant, bool) and variant):
                    return True
                return default

            if variantType == QVariant.String:
                return variant

            if variantType == QVariant.Int:
                return int(variant)
        except ValueError:
            return default

    # ----
    # ---- Public settings stored in MO's user interface
    # ----

    """
    To add a new setting,
    1. add a key to the constants.Setting file
    3. add a tuple in the constants.USER_SETTINGS in the same order as in the constants setting file
    2. add a matching attribute and a property to the top of the class
    4. add a test in the validateUserSetting method below that provides default values
       when a test fails
    """

    # NOTE: This must have a one-to-one mapping with constants.Setting enum

    def settings(self, setting: Setting):
        if setting > len(Setting) - 1:
            raise ValueError("Invalid key for Settings")
        return USER_SETTINGS[setting]

    def settingAttr(self, setting: Setting):
        return self.settings(setting)[0]

    def settingValue(self, setting: Setting, default=None):
        return getattr(self, self.settingAttr(setting), default)

    def settingName(self, setting: Setting):
        return self.settings(setting)[1]

    # ----

    def setUserSetting(self, setting: Union[Setting, str], value: Any, pluginName=None) -> Any:
        key = self.settingName(setting) if isinstance(setting, Setting) else setting
        self.organizer.setPluginSetting(INTERNAL_PLUGIN_NAME if not pluginName else pluginName, key, value)

    def getUserSetting(self, setting: Union[Setting, str], default=None, pluginName=None) -> Any:
        key = self.settingName(setting) if isinstance(setting, Setting) else setting
        value = self.organizer.pluginSetting(INTERNAL_PLUGIN_NAME if not pluginName else pluginName, key)
        return value if value is not None else default

    # ----

    def loadUserSetting(self, setting: Setting = None):
        """ Fills in this class's attributes with MO settings """
        if setting is None:
            for s in Setting:
                self.loadUserSetting(s)
            return
        attr = self.settingAttr(setting)
        setattr(self, attr, self.validateUserSetting(setting, self.getUserSetting(setting)))

    def validateUserSetting(self, setting: Setting, value: Any) -> Any:
        """ Returns either the value, if it is valid for the setting, or a default"""
        if setting == Setting.ENABLE_HIDING_PLUGINS:
            if isinstance(value, bool):
                return value
            return True
        if setting == Setting.EXCLUDE_INACTIVE_MODS:
            if isinstance(value, bool):
                return value
            return False
        if setting == Setting.ZEDIT_FOLDER:
            if value and path.exists(value + "/zedit.exe"):
                return value
            return ""
        if setting == Setting.MODNAME_TEMPLATE:
            return value if value is not None else ""
        if setting == Setting.PROFILENAME_TEMPLATE:
            return value if value is not None else ""
        if setting == Setting.HIDING_METHOD:
            VALUES = ["mohidden", "optional", "disable"]
            if value:
                value = value.lower()
                if value in VALUES:
                    return value
            DEORDERS_PLUGIN = "Merge Plugins Hide"
            DEORDERS_KEY = "hide-type"
            value = self.getUserSetting(DEORDERS_KEY, None, DEORDERS_PLUGIN)
            if value:
                value = value.lower()
                if value in VALUES:
                    return value
            return "mohidden"

    def storeUserSetting(self, setting: Union[Setting, List[Setting]], value: Any) -> None:
        """ Stores the value with MO and emits a change signal if the value changed """
        if isinstance(setting, list):
            if not isinstance(value, list) or len(setting) != len(value):
                raise ValueError("Attempting to store a list of settings with different size value list")
            for i in range(len(setting)):
                self.storeUserSetting[setting[i], value[i]]
            return

        v = self.validateUserSetting(setting, value)
        attr = self.settingAttr(setting)

        if v != getattr(self, attr):
            key = self.settingName(setting)
            self.setUserSetting(key, v)
            setattr(self, attr, v)
            self.settingChanged.emit(setting)

