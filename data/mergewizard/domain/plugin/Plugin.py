from typing import Optional
from mergewizard.domain.merge import MergeFile


class Plugin:

    NOT_SELECTED = -1

    @staticmethod
    def priority_sort(p):
        # 999999 is an arbitrarily large number used to insure that plugins with
        # no priority (i.e. -1) appear at the end of the list and sorted by key
        #
        # EX: plugins: list[Plugin]
        #     sortedPlugins = sorted(plugins, key=Plugin.priority_sort)
        return ((p.priority if p.priority >= 0 else 999999), p.key)

    # ----------------------------------------------------------------------

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

    def __repr__(self):
        # return "{} -- [{}|{}]".format(self.pluginName, len(self.requires()), len(self.requiredBy()))
        return self.pluginName

    def __init__(self, name: str, isMOPlugin: Optional[bool] = None):
        self.__key = name.lower()
        self.__hash = hash(self.__key)

        self.pluginName: str = name
        self.modName: str = ""
        self.modPath: str = ""
        self.isMOPlugin: bool = True if isMOPlugin else False
        self.isMissing: bool = False if isMOPlugin else True
        self.isHidden: bool = False
        self.isInactive: bool = False
        self.isMaster: bool = False
        self.isMerge: bool = False
        self.isMerged: bool = False
        self.priority: int = -1
        self.mergedCount: int = 0
        self.pluginOrder: int = Plugin.NOT_SELECTED
        self.masterOrder: int = Plugin.NOT_SELECTED
        self.mergeFile: MergeFile = None

    @property
    def key(self):
        return self.__key

    @property
    def isSelected(self):
        return self.pluginOrder != self.NOT_SELECTED

    @property
    def isSelectedAsMaster(self):
        return self.masterOrder != self.NOT_SELECTED

    def priority_lt(self, other):
        """ Provides a 'less-than' method that can be used to sort based on priority,
        with plugins having no priority (e.g. missing) placed at the bottom in
        alphabetical order """

        if self.priority < 0 and other.priority < 0:
            return self.__key < other.__key
        if self.priority >= 0 and other.priority >= 0:
            return self.priority < other.priority
        return self.priority >= 0
