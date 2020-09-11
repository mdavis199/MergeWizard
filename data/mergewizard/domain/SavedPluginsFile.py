import os
import json
from PyQt5.QtCore import qWarning as qWarn
from mergewizard.domain.Context import Context


class SavedPluginsFile:
    def __init__(self, context: Context):
        super().__init__()
        self.__context = context
        self.__filepath = self.__context.organizer.profilePath() + "/mergewizard.txt"

    def read(self):
        if os.path.exists(self.__filepath):
            try:
                with open(self.__filepath, "r", encoding="utf8") as f:
                    return json.load(f)
            except (OSError, ValueError) as ex:
                qWarn(self.tr("Failed to read MergeWizard file: {}").format(ex.strerror()))
                return []

    def write(self):
        pluginNames = self.__context.pluginModel.selectedPluginNames()
        """
        if not pluginNames and os.path.exists(self.__filepath):
            try:
                os.remove(self.__filepath)
            except OSError as ex:
                qWarn(self.tr("Failed to remove MergeWizard file: {}").format(ex.strerror()))
            return
        """
        if pluginNames:
            try:
                with open(self.__filepath, "w", encoding="utf8") as f:
                    json.dump(pluginNames, f)
            except (OSError, ValueError) as ex:
                qWarn(self.tr("Failed to write MergeWizard file: {}").format(ex.strerror()))
