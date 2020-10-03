## TODO

1. Implement hiding
2. Remove option to save to different profile (for now)
3. Change app icon
4. Remove unused resource icons
5. Change Int Validator to check for only positive or zero integers
6. When refreshing data, need to change the "Selected Plugins" title on the Apply Changes page.
7. Move the MergeWizard.txt file to the MW subdirectory in the profile. (don't delete the folder when removing backups)
8. Reduce creating so many icons. Optimize this.
9. Change the way setting changes are propagated.
   - SettingDialog returns list of changes.
     - Here we should just update the subset of data that is affected (Future effort.)
   - User gets option to refresh.
   - Refresh notice and changes sent to each page in turn.
