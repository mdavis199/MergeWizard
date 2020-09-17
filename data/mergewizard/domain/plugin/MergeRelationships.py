from typing import List, Tuple, Dict, Set, Union
from bisect import bisect
from collections.abc import Sequence
from mergewizard.domain.plugin import Plugin
from mergewizard.domain.merge import MergeFile


class Associations(Sequence):
    def __init__(self):
        self.__associations: List[Plugin] = []

    def __str__(self):
        return "\n".join([str(item) for item in self.__associations])

    def __getitem__(self, n: int) -> Plugin:
        return self.__associations[n]

    def __len__(self) -> int:
        return len(self.__associations)

    def addPlugin(self, plugin: Plugin) -> bool:
        idx = bisect(self.__associations, plugin)
        if idx > 0 and self.__associations[idx - 1] != plugin:
            self.__associations.insert(idx, plugin)
            return True
        return False

    def removePlugin(self, plugin: Plugin) -> bool:
        idx = next((i for i in range(len(self.__associations)) if self.__associations[i] == plugin), -1)
        if idx >= 0:
            del self.__associations[idx]
            return True
        return False

    def hasPlugin(self, plugin: Plugin) -> bool:
        return self.index(plugin) >= 0


PluginsFor = Associations  # Plugins merged by a specified plugin
MergesFor = Associations  # Plugins that merged the specified plugin (typically this on a list of one)


class MergeRelationships:
    def __init__(self) -> None:
        self.__relations: Dict[Plugin, Tuple[PluginsFor, MergesFor]] = {}

    def get(self, plugin: Plugin):
        return self.__relations.setdefault(plugin, (Associations(), Associations()))

    def clear(self) -> None:
        self.__relations.clear()

    def pluginsFor(self, merge: Plugin) -> Associations:
        return self.get(merge)[0]

    def mergesFor(self, plugin: Plugin) -> Associations:
        return self.get(plugin)[1]

    def addMerge(self, merge: Plugin, plugins: Union[List, Plugin]) -> List[Plugin]:
        if isinstance(plugins, Plugin):
            if self._addMerge(merge, plugins):
                return [merge, plugins]
            else:
                return []

        changed: List[Plugin] = []
        for plugin in plugins:
            if self._addMerge(merge, plugin):
                changed.append(plugin)
        if changed:
            changed.append(merge)
        return changed

    def _addMerge(self, merge: Plugin, plugin: Plugin) -> bool:
        if self.pluginsFor(merge).addPlugin(plugin):
            self.mergesFor(plugin).addPlugin(merge)
            return True
        return False

    def removeMerge(self, merge: Plugin) -> List[Plugin]:
        relations = self.__relations.pop(merge, None)
        if not relations:
            return []
        changed: Set = set()
        for plugin in relations[0]:
            changed.append(plugin)
            self.mergesFor(plugin).remove(merge)
        for plugin in relations[1]:
            changed.append(plugin)
            self.pluginsFor(plugin).remove(merge)
        changed.append(merge)
        return list(changed)

