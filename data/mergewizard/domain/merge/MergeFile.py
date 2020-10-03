from typing import List
from enum import IntEnum
from os import path
from mergewizard.domain.JSONObject import JSONObject

"""
Some things to keep in mind:

There are one or two versions of a merge's configuration:
1.  One located in zMerge profile's "merges.json"
2.  One located in the mod's "merge.json"

The first will exist after zMerge (or MW) adds a configuration to the profile.
The second will exist after zMerge actually builds the merge.

If the merge was configured, but not built, the merge will exist in the profile
but not in the mod.

Someone might remove the merge from the profile after it is built. So, it
may exist in the mod but not in the profile.

The configuration may have been built then modified. So the one in the mod and
the one in the configuration may be different.

"""


class PluginDesc(JSONObject):
    class Compare(IntEnum):
        Same = 0
        Different = -1
        DifferentFolders = 1

    def __init__(self, filename: str, dataFolder: str, **kwargs):
        self.filename, self.dataFolder = filename, dataFolder
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

    def compare(self, other):
        if other is None or self.filename != other.filename:
            return self.Compare.Different
        if not path.samefile(self.dataFolder, other.dataFolder):
            return self.Compare.DifferentFolders
        return self.Compare.Same

    def sameName(self, other):
        return self.filename == other.filename

    def sameFolder(self, other):
        return path.samefile(self.dataFolder, other.dataFolder)


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
        plugins: List[PluginDesc] = [],
        **kwargs
    ):
        self.__key = name.lower()
        self.__hash = hash(self.__key)
        self.__mergePath: str = ""  # full path to the json file
        self.__modIsActive: bool = False
        self.__isNew: bool = False
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
        self.plugins: List[PluginDesc] = []
        if plugins:
            if isinstance(plugins[0], dict):
                for p in plugins:
                    self.plugins.append(PluginDesc(**p))
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
    def modIsActive(self):
        return self.__modIsActive

    @modIsActive.setter
    def modIsActive(self, value: bool):
        self.__modIsActive = value

    @property
    def isNew(self):
        return self.__isNew

    @isNew.setter
    def isNew(self, value):
        self.__isNew = value

    @property
    def modName(self):
        return self.name

    # ----------------------------------

    def compare(self, other) -> List[str]:
        """ Compares itself with another mergefile and returns a list
        of differing attributes.  Missing attributes and attributes that begin
         with '_' are ignored. """

        attrs = []
        for a in self.__dict__.items():
            if a[0].startswith("_"):
                continue
            elif not hasattr(other, a[0]):
                continue
            elif a[0] == "plugins":
                if not self.comparePlugins():
                    attrs.append("plugins")
            elif getattr(other, a[0]) != a[1]:
                attrs.append(a[0])

    def comparePlugins(self, other):
        if len(self.plugins != len(other.plugins)):
            return False
        for i in range(len(self.plugins)):
            return self.plugins[i].compare(other.plugins[i]) == PluginDesc.Compare.Same


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
