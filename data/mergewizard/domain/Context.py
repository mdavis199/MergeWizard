from typing import Any
from PyQt5.QtCore import QVariant
from mobase import IOrganizer
from mergewizard.domain.DataCache import DataCache
from mergewizard.models.MergeModel import MergeModel
from mergewizard.models.PluginModel import PluginModel
from mergewizard.constants import INTERNAL_PLUGIN_NAME

# NOTE: getSetting does not stick until MO closes and reopens.
# If this plugin sets a value in 'organizer.persistent', it will
# continue to pull the old value until MO relaunches.


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

    # Public settings stored in MO's user interface

    def setUserSetting(self, name: str, value: Any) -> Any:
        self.organizer.setPluginSetting(INTERNAL_PLUGIN_NAME, name, value)

    def getUserSetting(self, name: str, default: Any) -> Any:
        value = self.organizer.pluginSetting(INTERNAL_PLUGIN_NAME, name)
        return value if value is not None else default
