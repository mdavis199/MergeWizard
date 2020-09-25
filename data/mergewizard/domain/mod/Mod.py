from typing import List


"""
The only reason we need this is so we can restore MO's state after setting
up a merge on a different profile.

It simply retains a list of the mods, priority and their active/inactive state

MergeWizard is not changing the priority of any mod, but does change the active state.
"""


class Mod:
    def __init__(self, name: str, priority: int, active: bool):
        self._name = name
        self._priority = priority
        self._active = active

    @property
    def name(self):
        return self._name

    @property
    def priority(self):
        return self._priority

    @property
    def active(self):
        return self._active
