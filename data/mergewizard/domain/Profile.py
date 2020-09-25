from typing import List
from PyQt5.QtCore import pyqtSignal, QObject, QDir, QFileInfo, QFile
from mobase import IOrganizer
from mergewizard.domain.MOLog import moWarn, moDebug

# TODO: make this either Qt- or python-centric, instead of this odd mix.


class Profile(QObject):
    MERGEWIZARD_FILE = "mergewizard.txt"
    PROFILE_DIR = "mergewizard"
    PROFILE_FILES = ["modlist.txt", "plugins.txt", "loadorder.txt"]

    profileCreated = pyqtSignal(str)

    def __init__(self, organizer: IOrganizer):
        super().__init__()
        self._organizer = organizer
        self._gameName = self._organizer.managedGame().gameName()
        self._currentProfileName = self._organizer.profileName()
        self._currentProfilePath = self._organizer.profile().absolutePath()
        self._profilesFolder = QFileInfo(self._currentProfilePath).dir().absolutePath()

    def currentProfileName(self):
        return self._currentProfileName

    def currentProfilePath(self):
        return self._currentProfilePath

    def profilesFolder(self):
        return self._profilesFolder

    def profilePath(self, name=None):
        return self.currentProfilePath() if not name else self._profilesFolder + "/" + name

    def backupPath(self, name=None):
        return self.profilePath(name) + "/" + self.PROFILE_DIR

    def mergeWizardFile(self, name=None):
        return self.profilePath(name) + "/" + self.MERGEWIZARD_FILE

    def mergeWizardFileExists(self, name=None):
        return QFile.exists(self.mergeWizardFile(name))

    def profileExists(self, name):
        return True if not name else QFile.exists(self.profilePath(name))

    def backupPathExists(self, name):
        return QFile.exists(self.backupPath(name))

    def isCurrentProfile(self, name: str) -> bool:
        return name.lower() == self._currentProfileName.lower()

    def allProfiles(self) -> List[str]:
        profiles = []
        infos = QDir(self.profilesFolder(), "", QDir.IgnoreCase, QDir.NoDotAndDotDot | QDir.Dirs).entryInfoList()
        for info in infos:
            profiles.append(info.baseName())
        return profiles

    def createProfile(self, name):
        if self.profileExists(name):
            return True

        # TODO: need to fix up the name before creating the directory
        # Refer to https://github.com/ModOrganizer2/modorganizer-uibase/blob/13963ed37276ede1fb052b838f8b7828d0f8d2f5/src/utility.cpp#L612
        # Refer to https://github.com/ModOrganizer2/modorganizer/blob/9945beabf160c68852a8bdac07de255f04fd6886/src/profile.cpp#L80

        profilesDir = QDir(self.profilesFolder())
        if not profilesDir.mkdir(name):
            moWarn(self.tr("Failed to create profile folder: {}").format(profilesDir.absoluteFilesPath(name)))
            return False
        self.profileCreated.emit(name)

        # copy all files (one level) from current profile to new profile
        return self.copyFiles(self.profilePath(), self.profilePath(name))

    def backupFiles(self, profileName=None):
        if self.createBackupFolder(profileName):
            return self.copyFiles(self.profilePath(profileName), self.backupPath(profileName), self.PROFILE_FILES, True)
        return False

    def createBackupFolder(self, profileName: str):
        """ Create a backup folder in the profile. The profile must exist """
        profileDir = QDir(self.profilePath(profileName))
        if not profileDir.exists():
            raise ValueError("Attempted to create backup folder in non-existant profile: {}".format(profileName))
        if profileDir.exists(self.PROFILE_DIR):
            return True
        if not profileDir.mkdir(self.PROFILE_DIR):
            moWarn("Failed to create backup directory in profile: {}".format(profileName))
            return False
        return True

    def restoreBackup(self, profileName: str):
        if not self.backupPathExists(profileName):
            moWarn("Cannot restore files from backup. Backup does not exist for profile: {}".format(profileName))
            return False
        return self.copyFiles(self.backupPath(profileName), self.profilePath(profileName), self.PROFILE_FILES, True)

    def copyFilesToProfile(self, profile):
        return self.copyFiles(self.profilePath(), self.profilePath(profile), self.PROFILE_FILES, True)

    def copyFiles(self, src, dst, names=None, overwrite=True):
        """ Copy files from src directory to dst directory. Subfolders are ignored.
        If names is provided, copies only files matching those names. Symlinks are not
        copied """
        moDebug("Copying files from {} to {}. Names: {}".format(src, dst, names))
        srcDir = QDir(src, "", QDir.IgnoreCase, QDir.Files | QDir.NoSymLinks)
        dstDir = QDir(dst)

        if not srcDir.exists() or not dstDir.exists():
            moWarn("Failed to copy files with non-existant directories")
            return False

        success = True
        if names:
            srcDir.setNameFilters(names)
        fileNames = srcDir.entryList()
        for name in fileNames:
            if dstDir.exists(name):
                if not overwrite:
                    continue
                dstDir.remove(name)
            success = QFile.copy(srcDir.filePath(name), dstDir.filePath(name))
            if not success:
                moWarn('Failed to copy "{}" from "{}" to "{}"'.format(name, src, dst))
        return success

    def removeBackup(self, profileName, names=None):
        backupdir = self.backupPath(profileName)
        if not self.backupPathExists(backupdir):
            return True
        for file in self.PROFILE_FILES:
            QFile(backupdir + "/" + file).remove()

    def removeFailedProfile(self, profile):
        """ THIS IS ONLY FOR PROFILES CREATED BY MERGEWIZARD """
        if not self.profileExists(profile):
            return True
        return QDir(self.profilePath(profile)).removeRecursively()
