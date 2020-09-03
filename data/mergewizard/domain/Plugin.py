from __future__ import annotations  # python 3.8
from typing import List, Tuple


class Plugin:

    NOT_SELECTED = -1

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

    def __str__(self):
        return "{} -- [{}|{}]".format(self.pluginName, len(self.requires), len(self.requiredBy))

    def __init__(self, name: str, isMOPlugin=True):
        self.__key = name.lower()
        self.__hash = hash(self.__key)

        self.pluginName: str = name
        self.modName: str = ""
        self.modPath: str = ""
        self.isMOPlugin: bool = isMOPlugin
        self.isMissing: bool = not isMOPlugin
        self.isHidden: bool = False
        self.isInactive: bool = False
        self.isMaster: bool = False
        self.isMerge: bool = False
        self.isMerged: bool = False
        self.priority: int = -1
        self.mergedCount: int = 0
        self.pluginOrder: int = self.NOT_SELECTED
        self.masterOrder: int = self.NOT_SELECTED
        self.requires: List[Tuple(Plugin, bool)] = []  # recursive list of plugins this plugin requires
        self.requiredBy: List[Tuple(Plugin, bool)] = []  # recursive list of plugins requiring this plugin

    def key(self):
        return self.__key

    def isSelected(self):
        return self.pluginOrder != self.NOT_SELECTED

    def isSelectedAsMaster(self):
        return self.masterOrder != self.NOT_SELECTED

    def addMaster(self, plugin: Plugin, direct: bool):
        if self == plugin:
            return

        for i in range(len(self.requires)):
            if self.requires[i][0] == plugin:
                if direct and self.requires[i][1] != direct:
                    self.requires[i] = (plugin, direct)
                    plugin.__addMasterOf(self, direct)
                return
        self.requires.append((plugin, direct))
        plugin.__addMasterOf(self, direct)

    def __addMasterOf(self, plugin: Plugin, direct: bool):
        for i in range(len(self.requiredBy)):
            if self.requiredBy[i][0] == plugin:
                if direct and self.requiredBy[i][1] != direct:
                    self.requiredBy[i] = (plugin, direct)
                return
        self.requiredBy.append((plugin, direct))

    def sortRequired(self):
        self.requires = sorted(self.requires, key=lambda x: x[0].priority if x[0].priority >= 0 else len(self.requires))
        self.requiredBy = sorted(
            self.requiredBy, key=lambda x: x[0].priority if x[0].priority >= 0 else len(self.requiredBy)
        )

    # ------------------------------------------------
    # ---- Helpers
    # ------------------------------------------------
    @staticmethod
    def sortByPriority(plugins: List[Plugin]):
        return sorted(plugins, key=lambda x: x.priority if x.priority >= 0 else len(plugins))
