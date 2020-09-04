from typing import Any
from mobase import IOrganizer
from mergewizard.models.MergeModel import MergeModel
from mergewizard.models.PluginModel import PluginModel
from mergewizard.constants import INTERNAL_PLUGIN_NAME


class Context:
    """
    Context contains data and convenience methods passed between the different WizardPages
    """

    def __init__(self):
        self.__mergeModel: MergeModel = None
        self.__pluginModel: PluginModel = None
        self.__organizer: IOrganizer = None

    def setMergeModel(self, mergeModel: MergeModel) -> None:
        self.__mergeModel = mergeModel

    def setPluginModel(self, pluginModel: PluginModel) -> None:
        self.__pluginModel = pluginModel

    def setOrganizer(self, organizer: IOrganizer) -> None:
        self.__organizer = organizer

    def mergeModel(self) -> MergeModel:
        return self.__mergeModel

    def pluginModel(self) -> PluginModel:
        return self.__pluginModel

    def organizer(self) -> IOrganizer:
        return self.__organizer

    def pluginName(self) -> str:
        return INTERNAL_PLUGIN_NAME

    # Semi-private settings stored in modorganizer.ini

    def setSetting(self, name: str, value: Any) -> None:
        self.organizer().setPersistent(INTERNAL_PLUGIN_NAME, name, value)

    def getSetting(self, name: str, default: Any) -> Any:
        return self.organizer().persistent(INTERNAL_PLUGIN_NAME, name, default)

    # Public settings stored in MO's user interface

    def setUserSetting(self, name: str, value: Any) -> Any:
        self.organizer().setPluginSetting(INTERNAL_PLUGIN_NAME, name, value)

    def getUserSetting(self, name: str, default: Any) -> Any:
        value = self.organizer().pluginSetting(INTERNAL_PLUGIN_NAME, name)
        return value if value is not None else default
