## Purpose

The primary purpose of this plugin is to automate repetitive user actions
when creating or modifying a merge, such as ordering the plugins and ensuring
that all required masters are also selected. The hope is that MergeWizard
would need very little, if any, knowledge of game specifics or of MO's file
structure or processes. MO would do all the heavy lifting.

When creating a new game by following a Modding guide, there's typically a section
where you create perhaps a couple dozen merges back-to-back. This might entail:

1. Copying the current profile
2. Switching to the new profile.
3. Activating the mods that contain plugins you want to merge.
4. Enabling the plugins you want to merge.
5. Activating mods for the masters of the plugins (and their masters).
6. Activating those plugins.
7. Reordering the plugins.
8. Creating the merge.
9. Possibly hiding the plugins that were merged.
10. Switching back to the main profile.
11. ... and repeat.

Ideally, I would want to launch MergeWizard once from a base profile, and create
all the merge profiles with all the correct plugins/mods (and zMerge configurations) in one go. No jumping back-and-forth between profiles.

### Issues

MO has interfaces available to enable/disable plugins/mods. Doing so programmatically
from MergeWizard for the current profile is straight-forward. But there doesn't appear to be
interfaces for creating or working with any profile other than the current profile.

### Ways to work around this:

#### For creating a new profile.

MergeWizard can create a new folder in MO's profile directory and copy to it all files
(one-level deep) from the current profile. **But**, when exiting MergeWizard, the user
will need to use "Manage Profiles" from MO, for MO to see the new profile. _After MergeWizard
is working, I can ask the MO team if they could add an interface that updates the profile list._

#### For creating the plugin/mod list for a different profile.

We have two options:

##### Option 1.

1. Perform all actions in current profile
2. Tell MO to sync its files.
3. Copy results to other profile.
4. Reset plugin/mod states (programmatically) to before the changes
5. Tell MO to sync its files

There is a lot of room for error. But MO handles its own files and states.

##### Option 2.

1. Read the `modlist.txt` and `plugins.txt` files from the current profile.
2. Programmatically edit the files to reflect the changes we want.
3. Save the files to the other profile

MO is not involved with determining plugin selection and order.
Requires MergeWizard to have knowledge of MO files and game requirements.
The problem is when enabling or disabling a mod, plugins that were
previously hidden may become available. Just naively editing an existing
file would not allow for those newly visible plugins.
