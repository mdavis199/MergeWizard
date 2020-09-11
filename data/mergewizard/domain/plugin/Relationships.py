from typing import List, Set, Union, Dict, Tuple
from bisect import bisect
from collections.abc import Sequence
from mergewizard.domain.plugin.Plugin import Plugin

# TODO: Consider generalizing Associations/Relationships


class Association:
    """ An Association describes whether a plugin has a direct or indirect
    connection to another plugin """

    def __init__(self, plugin: Plugin, direct: bool):
        self._plugin: Plugin = plugin
        self._direct: bool = direct

    def __hash__(self):
        return hash(self.plugin)

    def __eq__(self, other: Union[str, Plugin, "Association"]):
        if isinstance(other, str):
            return self.key == other
        if isinstance(other, Plugin):
            return self.key == other.key
        return self is other or self.key == other.key

    def __lt__(self, other: [Plugin, "Association"]):
        if isinstance(self, Plugin):
            return self.plugin.priority_lt(other)
        return self.plugin.priority_lt(other.plugin)

    def __repr__(self) -> str:
        return "    {}: {}".format("D" if self.direct else "I", self.plugin.pluginName)

    @property
    def key(self) -> str:
        return self.plugin.key

    @property
    def plugin(self) -> Plugin:
        return self._plugin

    @property
    def direct(self) -> bool:
        return self._direct

    @direct.setter
    def direct(self, value) -> None:
        self._direct = value


class Associations(Sequence):
    """ Associations is a managed list of plugins associated with a given plugin.

       *  The contained list of associations is kept sorted by the plugins' priorities.
       *  No plugin is added twice.
       *  If trying to add a plugin that is already in the list:
            - if direct/indirect relationships are the same, no change is made.
            - if the new association is indirect, no change is made
            - if the new association is direct, the association is updated.

    NOTE: The associations are sorted by priority because it makes sorting them
    in the Model Views much easier.
    """

    # ===========================================================

    def __init__(self):
        self.__associations: List[Association] = []

    def __repr__(self) -> str:
        return "\n".join([item.__repr__() for item in self.__associations])

    def __getitem__(self, n: int) -> Association:
        return self.__associations[n]

    def __len__(self) -> int:
        return len(self.__associations)

    def addPlugin(self, plugin: Plugin, direct: bool) -> bool:
        """ Adds plugin to associations list. If the association already exists,
        the existing association *may* be updated.

        Returns True if the association was either added or updated.
        """
        association = Association(plugin, direct)
        idx = bisect(self.__associations, association)
        if idx > 0 and self.__associations[idx - 1].plugin == plugin:
            if direct and not self.__associations[idx - 1].direct:
                self.__associations[idx - 1].direct = True
                return True
            else:
                return False
        self.__associations.insert(idx, association)
        return True

    def removePlugin(self, plugin: Plugin) -> bool:
        """ Removes a plugin from the list of associations.

        Returns True if the plugin was found and removed. """

        idx = next((i for i in range(len(self.__associations)) if self.__associations[i].plugin == plugin), -1,)
        if idx >= 0:
            del self.__associations[idx]
            return True
        return False

    def removeAllIndirect(self) -> bool:
        """ Removes all indirect associations from the list.

        Returns True if any association was removed.
        """
        oldLen = len(self.__associations)
        self.__associations[:] = [r for r in self.__associations if r.direct]
        return len(self.__associations) != oldLen

    def hasPlugin(self, plugin: Plugin) -> bool:
        """ Tests if the plugin is in the list of associations. """
        return self.index(plugin) >= 0

    def associationhipType(self, plugin: Plugin) -> Union[None, bool]:
        """ Returns True if the association is Direct, False if it is Indirect and None
        if there is not association with the plugin """

        idx = self.index(plugin)
        if idx < 0:
            return None
        return self.__associations[idx].direct


Requirements = Associations
Dependents = Associations


class Relationships:
    """
    Relationships represents all the associations between plugins.

    For each plugin, it includes a mapping to the all plugins it requires (Requirements) and
    a mapping to all plugins that require it (Dependents).
    """

    def __init__(self) -> None:
        self.__relations: Dict[Plugin, Tuple[Requirements, Dependents]] = {}

    def get(self, plugin: Plugin):
        return self.__relations.setdefault(plugin, (Associations(), Associations()))

    def clear(self) -> None:
        self.__relations.clear()

    def requirementsFor(self, plugin: Plugin):
        """ Plugins that the specified plugin requires """
        return self.get(plugin)[0]

    def dependentsOf(self, plugin: Plugin):
        """ Plugins that require the specified plugin """
        return self.get(plugin)[1]

    def addRequirement(self, plugin: Plugin, requiredPlugin: Plugin, direct: bool = True) -> List[Plugin]:
        """ Recursively adds the associations between the two plugins.

        Returns a list of plugins with changed relationships to make it easier
        for the PluginModel to emit dataChanged signals.
        """

        changed = set()
        self.__addRequirementsRecursively(plugin, requiredPlugin, direct, changed)
        return list(changed)

    def __addRequirementsRecursively(
        self, plugin: Plugin, requiredPlugin: Plugin, direct: bool, changed: Set[Plugin]
    ) -> None:
        if plugin == requiredPlugin:
            return

        # add mapping and reverse mapping
        if self.requirementsFor(plugin).addPlugin(requiredPlugin, direct):
            changed.add(plugin)
            if self.dependentsOf(requiredPlugin).addPlugin(plugin, direct):
                changed.add(requiredPlugin)

        # all the requirements of requiredPlugin are indirect requirements of this plugin
        for requirement in self.requirementsFor(requiredPlugin):
            self.__addRequirementsRecursively(plugin, requirement.plugin, False, changed)

        # all dependents of plugin are indirect dependents of requiredPlugin
        for dependent in self.dependentsOf(plugin):
            self.__addRequirementsRecursively(dependent.plugin, requiredPlugin, False, changed)

    def removePlugin(self, plugin: Plugin) -> List[Plugin]:
        """ Removes all plugin associations that refer to *plugin*

        This is a bit tricky.  We also have to remove indirect associations that
        resulted from adding *plugin*, which is impossible to discern.

        The approach:
        1. Remove all associations refering to plugin.
        2. For all plugins that changed, remove all indirect associations
        3. Re-add the direct requirements for the changed plugins to recreate the associations
           maps.

        Returns a list of changed Plugins to make it easier for the PluginModel to emit
        changedData signals.
        """

        relations = self.__relations.pop(plugin, None)
        if not relations:
            return []

        changed = set()
        for item in relations[0]:
            changed.add(item.plugin)
            self.dependentsOf(item.plugin).removePlugin(plugin)
            self.dependentsOf(item.plugin).removeAllIndirect()

        for item in relations[1]:
            changed.add(item.plugin)
            self.requirementsFor(item.plugin).removePlugin(plugin)
            self.requirementsFor(item.plugin).removeAllIndirect()

        if changed:
            for changedPlugin in changed:
                for item in self.requirementsFor(changedPlugin):
                    self.addRequirement(changedPlugin, item.plugin, True)
            changed.add(plugin)
        return list(changed)

    def __repr__(self) -> str:
        result = []
        for p in self.__relations:
            result.append("{}: [{} | {}]".format(p.pluginName, len(self.requirementsFor(p)), len(self.dependentsOf(p))))

            result.append("  Requirements:")
            result.append("{}".format(self.__relations[p][0]))
            result.append("  Dependents: ")
            result.append("{}".format(self.__relations[p][1]))
        return "\n".join(result)
