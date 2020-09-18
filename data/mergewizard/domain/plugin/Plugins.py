from __future__ import annotations
from typing import Optional, Union, Tuple, List
from collections.abc import Mapping
from mergewizard.thirdparty.sortedcontainers import SortedDict
from mergewizard.domain.plugin import Plugin
from mergewizard.domain.plugin.Relationships import Relationships, Requirements, Dependents
from mergewizard.domain.plugin.MergeRelationships import MergeRelationships


class Plugins(Mapping):
    def __init__(self):
        self.__plugins: SortedDict[str, Plugin] = SortedDict(lambda x: x.lower())
        self.__relationships: Relationships = Relationships()
        self.__mergeRelationships: MergeRelationships = MergeRelationships()

    def __len__(self):
        return self.__plugins.__len__()

    def __iter__(self):
        return self.__plugins.__iter__()

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.__plugins.peekitem(key)[1]
        return self.__plugins.__getitem__(key.lower())

    def __contains__(self, key):
        return self.__plugins.__contains__(key.lower())

    def __eq__(self, other):
        return self.__plugins.__eq__(other)

    def __ne__(self, other):
        return self.__plugins.__ne__(other)

    def keys(self):
        return self.__plugins.keys()

    def items(self):
        return self.__plugins.items()

    def values(self):
        return self.__plugins.values()

    # -----------------------------------------------------------------------

    def add(self, plugin: Plugin) -> None:
        self.__plugins[plugin.key] = plugin

    def get(self, name: str, isMOPlugin: Optional[bool] = None) -> Plugin:
        """
        Returns the plugin with the specified name.

        The plugin is created if it does not already exist. The name is case-insensitive.
        The *isMOPlugin* parameter is used only if the plugin does not exist. If this
        value is False, the plugin is initialized as a "non_MO and missing" plugin. Otherwise,
        the plugin is initialized as a plugin MO knows about and not missing.
        """

        return self.__plugins.setdefault(name.lower(), Plugin(name, isMOPlugin))

    def remove(self, name: str) -> List[Plugins]:
        """ Removes all associations for the plugin and removes the plugin from plugins list.

        Returns a list of changed plugins whose associations were changed
        """

        if name in self.__plugins:
            changed = self.__relationships.removePlugin(self.get(name))
            del self.__plugins[name]
            return changed
        return []

    def clear(self) -> None:
        self.__relationships.clear()
        self.__plugins.clear()

    def index(self, name: str) -> int:
        """ Returns the index of the key or -1 if the key is not in the list

        The purpose is to allow calling a model's *aboutToBeRemoved()* method
        with the index of the key.
        """
        key = name.lower()
        return -1 if key not in self.__plugins else self.__plugins.index(key)

    def insertionIndex(self, name: str) -> int:
        """ Returns the index where the key would be inserted. Returns -1
        if key already exists in dictionary.

        The purpose is to allow calling a model's *aboutToBeInserted()* method
        with the index of where the insertion would be. """

        key = name.lower()
        idx = self.__plugins.bisect_key_right(key)
        if idx > 0 and self.__plugins.peekitem(idx - 1)[0] == key:
            return -1
        return idx

    # ----
    # ---- Methods related to plugin Relationships
    # ----

    def addRequirement(self, plugin, requiredPlugin) -> List[Plugin]:
        """ Creates a direct association between *plugin* and its *requiredPlugin*.
        """

        return self.__relationships.addRequirement(plugin, requiredPlugin)

    def associations(self, plugin: Union[str, Plugin]) -> Tuple[Requirements, Dependents]:
        """ Returns a tuple containing:
        1. associations that this *plugin* requires
        2. associations that require (depend on) this *plugin*

        * The DependentsOf element is a reverse mapping of the RequirementsFor.
        * An Association is simply a plugin and a bool indicating if the association is
          direct or indirect.

        If the plugin does not exist, a missing/non-MO plugin is created for it
        """

        if isinstance(plugin, str):
            return self.__relationships.get(self.get(plugin, False))
        else:
            return self.__relationships.get(plugin)

    def removeAssociations(self, plugin: Union[str, Plugin]) -> List[Plugin]:
        """ Removes all associations related to the plugin.
        Returns a list of plugins that were changed.

        If the plugin does not exist, a missing/non-MO plugin is created for it
        """

        if isinstance(plugin, str):
            return self.__relationships.removePlugin(self.get(plugin))
        else:
            return self.__relationships.removePlugin(plugin)

    def requirements(self, plugin: Union[str, Plugin]) -> Requirements:
        return self.associations(plugin)[0]

    def dependents(self, plugin: Union[str, Plugin]) -> Dependents:
        return self.associations(plugin)[1]

    # ----
    # ---- Methods relation to merge relationships
    # ----

    def addMergeRelationship(self, merge: Plugin, plugin: Plugin) -> List[Plugin]:
        """
        """
        return self.__mergeRelationships.addMerge(merge, plugin)

    def mergeAssociations(self, plugin: Union[str, Plugin]):
        if isinstance(plugin, str):
            return self.__mergeRelationships.get(self.get(plugin, False))
        else:
            return self.__mergeRelationships.get(plugin)

    def pluginsForMerge(self, merge: Plugin) -> List[Plugin]:
        return self.__mergeRelationships.pluginsFor(merge)

    def mergesForPlugin(self, plugin: Plugin) -> List[Plugin]:
        return self.__mergeRelationships.mergedFor(plugin)

    # -------------------------------------------------------------------
    def relationships(self):
        """ FOR DEBUG PURPOSES ONLY """
        return self.__relationships
