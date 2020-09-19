from typing import Any, Union, List
from os import path
from PyQt5.QtCore import QVariant, QObject, pyqtSignal, qInfo
from mobase import IOrganizer
from mergewizard.domain.DataCache import DataCache
from mergewizard.models.MergeModel import MergeModel
from mergewizard.models.PluginModel import PluginModel
from mergewizard.constants import INTERNAL_PLUGIN_NAME, Setting


# NOTE: getSetting does not stick until MO closes and reopens.
# If this plugin sets a value in 'organizer.persistent', it will
# continue to pull the old value until MO relaunches.


class Context(QObject):
    """
    Context contains data and convenience methods passed between the different WizardPages
    """

    settingChanged = pyqtSignal(str)

    DEORDERS_PLUGIN = "Merge Plugins Hide"

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

    def setUserSetting(self, name: str, value: Any, pluginName=None) -> Any:
        self.organizer.setPluginSetting(INTERNAL_PLUGIN_NAME if not pluginName else pluginName, name, value)

    def getUserSetting(self, name: str, default: Any, pluginName=None) -> Any:
        value = self.organizer.pluginSetting(INTERNAL_PLUGIN_NAME if not pluginName else pluginName, name)
        return value if value is not None else default

    def loadUserSetting(self, name: str = None):
        qInfo("context.loadUserSetting: {}".format(name))
        if not name:
            qInfo("Loading all user settings")
            for setting in Setting.__dict__:
                if not setting.startswith("_"):
                    self.loadUserSetting(Setting.__dict__[setting])
            return
        if name == Setting.ENABLE_HIDING_PLUGINS:
            self._enableHidingPlugins = self.validateUserSetting(name, self.getUserSetting(name, True))
            qInfo("set enableHidingPlugins: {}".format(self._enableHidingPlugins))
        if name == Setting.HIDING_METHOD:
            self._hidingMethod = self.validateUserSetting(
                name, self.getUserSetting(name, self.getUserSetting(name, None, self.DEORDERS_PLUGIN))
            )
        if name == Setting.ZMERGE_FOLDER:
            self._zMergeFolder = self.validateUserSetting(name, self.getUserSetting(name, ""))
        if name == Setting.MODNAME_TEMPLATE:
            self._modNameTemplate = self.validateUserSetting(name, self.getUserSetting(name, ""))
        if name == Setting.PROFILENAME_TEMPLATE:
            self._profileNameTemplate = self.validateUserSetting(name, self.getUserSetting(name, ""))

    def validateUserSetting(self, name: str, value: Any) -> Any:
        if name == Setting.ENABLE_HIDING_PLUGINS:
            if isinstance(value, bool):
                qInfo("{}: value {}".format(name, value))
                return value
            qInfo("{}: default: True".format(name))
            return True
        if name == Setting.HIDING_METHOD:
            VALUES = ["mohidden", "optional", "disable"]
            if value:
                value = value.lower()
                if value in VALUES:
                    return value
            return "mohidden"
        if name == Setting.ZMERGE_FOLDER:
            if value and path.exists(value + "/zedit.exe"):
                return value
            return ""
        if name == Setting.MODNAME_TEMPLATE:
            return value if value is not None else ""
        if name == Setting.PROFILENAME_TEMPLATE:
            return value if value is not None else ""

    def storeUserSetting(self, name: Union[str, List[str]], value: Any) -> None:
        # if name is a list, value must be a list of the same size
        if isinstance(name, list):
            for i in range(len(name)):
                self.storeUserSetting[name[i], value[i]]
            return

        v = self.validateUserSetting(name, value)
        if name == Setting.ENABLE_HIDING_PLUGINS:
            qInfo("Storing {} value: {}".format(name, value))
            if v != self.enableHidingPlugins:
                self.setUserSetting(name, v)
                self._enableHidingPlugins = v
                self.settingChanged.emit(name)
        if name == Setting.HIDING_METHOD:
            if v != self.enableHidingPlugins:
                self.setUserSetting(name, v)
                self._hidingMethod = v
                self.settingChanged.emit(name)
        if name == Setting.ZMERGE_FOLDER:
            if v != self.enableHidingPlugins:
                self.setUserSetting(name, v)
                self._zMergeFolder = v
                self.settingChanged.emit(name)
        if name == Setting.MODNAME_TEMPLATE:
            if v != self.enableHidingPlugins:
                self.setUserSetting(name, v)
                self._modNameTemplate = v
                self.settingChanged.emit(name)
        if name == Setting.PROFILENAME_TEMPLATE:
            if v != self.enableHidingPlugins:
                self.setUserSetting(name, v)
                self._profileNameTemplate = v
                self.settingChanged.emit(name)
