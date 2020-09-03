import mobase

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon

from mergewizard.dialogs.Wizard import Wizard
from mergewizard.constants import INTERNAL_PLUGIN_NAME, Icon
import mergewizard.resources


class PluginTool(mobase.IPluginTool):

    DESCRIPTION = "Enable plugins and their masters using text entry"

    def __tr(self, str):
        return QCoreApplication.translate(INTERNAL_PLUGIN_NAME, str)

    def __init__(self):
        self.__organizer = None
        super().__init__()

    def init(self, organizer):
        self.__organizer = organizer
        return organizer is not None

    def isActive(self):
        return bool(self.__organizer.pluginSetting(INTERNAL_PLUGIN_NAME, "enabled"))

    def settings(self):
        return [mobase.PluginSetting("enabled", self.__tr("Enable this plugin"), True)]

    def display(self):
        wizard = Wizard(self.__organizer, self._parentWidget())
        wizard.exec()

    def icon(self):
        return QIcon(Icon.MERGEWIZARD)

    def version(self):
        return mobase.VersionInfo(1, 0, 0, mobase.ReleaseType.final)

    def description(self):
        return self.__tr(self.DESCRIPTION)

    def tooltip(self):
        return self.__tr(self.DESCRIPTION)

    def displayName(self):
        return self.__tr("MergeWizard")

    def name(self):
        return INTERNAL_PLUGIN_NAME

    def author(self):
        return "mdavis199"
