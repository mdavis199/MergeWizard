from PyQt5.QtCore import QObject, pyqtSignal, QDate, QTime
from mobase import IOrganizer
from mergewizard.domain.Settings import Settings, Validator, DEFAULT_VALIDATOR, BOOLEAN_VALIDATOR, INT_VALIDATOR
from mergewizard.domain.JSONObject import JSONObject
from mergewizard.domain.Profile import Profile
from mergewizard.domain.DataCache import DataCache
from mergewizard.models.MergeModel import MergeModel
from mergewizard.models.PluginModel import PluginModel
from mergewizard.domain.MOLog import moWarn

# ----
# ---- For convenience, we are reexporting validators for classes that use
# ---- internal settings.
# ----

Validator = Validator
DEFAULT_VALIDATOR = DEFAULT_VALIDATOR
BOOLEAN_VALIDATOR = BOOLEAN_VALIDATOR
INT_VALIDATOR = INT_VALIDATOR


class Context(QObject):
    """
    Context contains data and convenience methods passed between the different WizardPages
    """

    settingChanged = pyqtSignal(int)

    def __init__(self, organizer: IOrganizer):
        super().__init__()
        self.__settings: Settings = Settings(organizer)
        self.__dataCache: DataCache = DataCache(organizer)
        self.__profile: Profile = Profile(organizer)
        self.__profile.backupFiles()

    @property
    def organizer(self) -> IOrganizer:
        return self.__dataCache.organizer

    @property
    def settings(self) -> Settings:
        return self.__settings

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
    def profile(self) -> Profile:
        return self.__profile

    # ----
    # ---- Reading and writing the MergeWizard text file
    # ----

    class MWData(JSONObject):
        def __init__(self, loadedMod="", configuredDate="", configuredTime="", **kwargs):
            self.loadedMod = loadedMod
            self.configuredDate = configuredDate
            self.configuredTime = configuredTime
            for k, v in kwargs.items():
                setattr(self, k, v)

    def writeMergeWizardFile(self, profileName=None):
        if not self.profile.profileExists(profileName):
            return False
        data = self.MWData()
        data.loadedMod = self.mergeModel.currentMergeName()
        data.configuredDate = QDate.toString(QDate.currentDate(), "yyyy.MM.dd")
        data.configuredTime = QTime.toString(QTime.currentTime(), "hh:mm:ss ap t")
        try:
            with open(self.profile.mergeWizardFile(profileName), "w", encoding="utf8") as f:
                f.write(data.toJSON())
                return True
        except (OSError, ValueError, TypeError) as ex:
            moWarn(self.tr("Failed to write MergeWizard file: {}").format(ex.strerror()))
        return False

    def readMergeWizardFile(self, profileName=None):
        if self.profile.mergeWizardFileExists(profileName):
            file = self.profile.mergeWizardFile(profileName)
            try:
                with open(file, "r", encoding="utf8") as f:
                    return self.MWData.fromJSON(f.read())
            except OSError as ex:
                moWarn('Failed to open MergeWizard file "{}": {}'.format(file, ex.strerror))
            except ValueError as ex:
                moWarn('Failed to read MergeWizard file "{}": {}'.format(file, ex))
            except TypeError:
                moWarn('Failed to read MergeWizard file "{}": File has incorrect format'.format(file))
