from typing import Any
from mobase import IOrganizer
from mergewizard.domain.DataCache import DataCache
from mergewizard.models.MergeModel import MergeModel
from mergewizard.models.PluginModel import PluginModel
from mergewizard.constants import INTERNAL_PLUGIN_NAME


class Context:
    """
    Context contains data and convenience methods passed between the different WizardPages
    """

    def __init__(self, organizer: IOrganizer):
        self.__dataCache: DataCache = DataCache(organizer)

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

    # Semi-private settings stored in modorganizer.ini

    def setSetting(self, name: str, value: Any) -> None:
        self.organizer.setPersistent(INTERNAL_PLUGIN_NAME, name, value)

    def getSetting(self, name: str, default: Any) -> Any:
        return self.organizer.persistent(INTERNAL_PLUGIN_NAME, name, default)

    # Public settings stored in MO's user interface

    def setUserSetting(self, name: str, value: Any) -> Any:
        self.organizer.setPluginSetting(INTERNAL_PLUGIN_NAME, name, value)

    def getUserSetting(self, name: str, default: Any) -> Any:
        value = self.organizer.pluginSetting(INTERNAL_PLUGIN_NAME, name)
        return value if value is not None else default
