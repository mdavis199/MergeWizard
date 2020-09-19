from typing import Any, Union, List
from os import path
from PyQt5.QtCore import QVariant, QObject, pyqtSignal
from mobase import IOrganizer
from mergewizard.domain.DataCache import DataCache
from mergewizard.models.MergeModel import MergeModel
from mergewizard.models.PluginModel import PluginModel
from mergewizard.constants import INTERNAL_PLUGIN_NAME, Setting


# NOTE: Must be a one-to-one mapping with constants.Setting enumeration.


class Context(QObject):
    """
    Context contains data and convenience methods passed between the different WizardPages
    """

    settingChanged = pyqtSignal(int)

    def __init__(self, organizer: IOrganizer):
        super().__init__()
        self.__dataCache: DataCache = DataCache(organizer)
        self._enableHidingPlugins = False
        self._hidingMethod = ""
        self._zMergeFolder = ""
        self._modNameTemplate = ""
        self._profileNameTemplate = ""

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
    def enableHidingPlugins(self) -> bool:
        return self._enableHidingPlugins

    @property
    def hidingMethod(self) -> str:
        return self._hidingMethod

    @property
    def zMergeFolder(self) -> str:
        return self._zMergeFolder

    @property
    def modNameTemplate(self) -> str:
        return self._modNameTemplate

    @property
    def profileNameTemplate(self) -> str:
        return self._profileNameTemplate

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

    # NOTE: This must have a one-to-one mapping with constants.Setting enum
    Settings = [
        ("_enableHidingPlugins", "enable-hiding"),
        ("_hidingMethod", "hide-type"),
        ("_zMergeFolder", "zedit-folder"),
        ("_modNameTemplate", "mod-name-template"),
        ("_profileNameTemplate", "profile-name-template"),
    ]

    def setUserSetting(self, setting: Union[Setting, str], value: Any, pluginName=None) -> Any:
        key = self.Settings[setting][1] if isinstance(setting, Setting) else setting
        self.organizer.setPluginSetting(INTERNAL_PLUGIN_NAME if not pluginName else pluginName, key, value)

    def getUserSetting(self, setting: Union[Setting, str], default=None, pluginName=None) -> Any:
        key = self.Settings[setting][1] if isinstance(setting, Setting) else setting
        value = self.organizer.pluginSetting(INTERNAL_PLUGIN_NAME if not pluginName else pluginName, key)
        return value if value is not None else default

    # ----

    def loadUserSetting(self, setting: Setting = None):
        if setting is None:
            for s in Setting:
                self.loadUserSetting(s)
            return
        attr = self.Settings[setting][0]
        setattr(self, attr, self.validateUserSetting(setting, self.getUserSetting(setting)))

    def validateUserSetting(self, setting: Setting, value: Any) -> Any:
        if setting == Setting.ENABLE_HIDING_PLUGINS:
            if isinstance(value, bool):
                return value
            return True
        if setting == Setting.ZMERGE_FOLDER:
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
        # if name is a list, value must be a list of the same size
        if isinstance(setting, list):
            for i in range(len(setting)):
                self.storeUserSetting[setting[i], value[i]]
            return

        v = self.validateUserSetting(setting, value)
        attr = self.Settings[setting][0]
        if v != getattr(self, attr):
            key = self.Settings[setting][1]
            self.setUserSetting(key, v)
            setattr(self, attr, v)
            self.settingChanged.emit(setting)

