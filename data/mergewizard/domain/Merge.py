from typing import List
from mergewizard.domain.JSONObject import JSONObject


class PluginFileDesc(JSONObject):
    def __init__(self, filename: str, dataFolder: str, hash: str = "", **kwargs):
        self.filename, self.dataFolder, self.hash = filename, dataFolder, hash
        for k, v in kwargs.items():
            setattr(self, k, v)


class Merge(JSONObject):
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
        name,
        filename: str = "",
        method="Clobber",
        loadOrder: List[str] = [],
        archiveAction: str = "Extract",
        buildMergedArchive: bool = False,
        useGameLoadOrder: bool = True,
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
        self.__mergePath: str = ""
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

    def setMergePath(self, path: str):
        self.__mergePath = path

    def mergePath(self):
        return self.__mergePath
