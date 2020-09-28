from typing import List
from os import path
from mergewizard.domain.JSONObject import JSONObject

# REFER: https://github.com/z-edit/zedit/blob/baf117802822f9649568f42f4deebd0a1f21ab22/src/javascripts/Services/merge/mergeService.js#L82
# for defaults.


class PluginFileDesc(JSONObject):
    def __init__(self, filename: str, dataFolder: str, **kwargs):
        self.filename, self.dataFolder, self.hash = filename, dataFolder, hash
        for k, v in kwargs.items():
            setattr(self, k, v)

        # TODO: is this always true?
        self.__modName = path.basename(path.dirname(self.dataFolder))

    @property
    def modName(self):
        return self.__modName

    @modName.setter
    def modName(self, value):
        self.__modName = value


class MergeFile(JSONObject):

    METHOD_VALUES = ["Clobber", "Clean"]

    ARCHIVEACTION_VALUES = ["Extract", "Copy", "Ignore"]

    def __hash__(self):
        return self.__hash

    def __eq__(self, other):
        return self.__key == other.__key

    def __lt__(self, other):
        return self.__key < other.__key

    def __gt__(self, other):
        return self.__key > other.__key

    def __le__(self, other):
        return self.__key <= other.__key

    def __ge__(self, other):
        return self.__key >= other.__key

    def __init__(
        self,
        name: str = "",
        filename: str = "",
        method="Clobber",
        loadOrder: List[str] = [],
        archiveAction: str = "Extract",
        buildMergedArchive: bool = False,
        useGameLoadOrder: bool = False,
        handleFaceData: bool = True,
        handleVoiceData: bool = True,
        handleBillboards: bool = True,
        handleStringFiles: bool = True,
        handleTranslations: bool = True,
        handleIniFiles: bool = True,
        handleDialogViews: bool = True,
        copyGeneralAssets: bool = False,
        dateBuilt: str = "",
        plugins: List[PluginFileDesc] = [],
        **kwargs
    ):
        self.__key = name.lower()
        self.__hash = hash(self.__key)
        self.__mergePath: str = ""  # full path to the json file
        self.__modIsActive: bool = False
        self.name: str = name
        self.filename: str = filename
        self.method: str = method
        self.loadOrder: str = loadOrder
        self.archiveAction: bool = archiveAction
        self.buildMergedArchive: bool = buildMergedArchive
        self.useGameLoadOrder: bool = useGameLoadOrder
        self.handleFaceData: bool = handleFaceData
        self.handleVoiceData: bool = handleVoiceData
        self.handleBillboards: bool = handleBillboards
        self.handleStringFiles: bool = handleStringFiles
        self.handleTranslations: bool = handleTranslations
        self.handleIniFiles: bool = handleIniFiles
        self.handleDialogViews: bool = handleDialogViews
        self.copyGeneralAssets: bool = copyGeneralAssets
        self.dateBuilt: str = dateBuilt
        self.plugins: List[PluginFileDesc] = []
        if plugins:
            if isinstance(plugins[0], dict):
                for p in plugins:
                    self.plugins.append(PluginFileDesc(**p))
            else:
                self.plugins = plugins
        for k, v in kwargs.items():
            setattr(self, k, v)

    def key(self):
        return self.__key

    # ----------------------------------
    # full path of the merge.json file
    # ----------------------------------

    @property
    def mergePath(self):
        return self.__mergePath

    @mergePath.setter
    def mergePath(self, value):
        self.__mergePath = value

    @property
    def modName(self):
        return self.__modName

    @modName.setter
    def modName(self, value):
        self.__modName = value

    @property
    def modIsActive(self):
        return self.__modIsActive

    @modIsActive.setter
    def modIsActive(self, value: bool):
        self.__modIsActive = value


class Merges(JSONObject):
    def __init__(self, mergeList):
        self.merges = []
        self._profilePath = ""
        self._profileName = ""
        for m in mergeList:
            self.merges.append(MergeFile(**m))

    @property
    def profilePath(self):
        return self._profilePath

    @profilePath.setter
    def profilePath(self, path):
        self._profilePath = path

    @property
    def profileName(self):
        return self._profileName

    @profileName.setter
    def profileName(self, value):
        self._profileName = value
