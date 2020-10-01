from enum import IntFlag, auto
from typing import List, Union
import json
from PyQt5.QtCore import QDir, QFile, QFileInfo, QStandardPaths, qDebug
from mergewizard.domain.merge.MergeFile import Merges

# REFER: https://github.com/z-edit/xelib/blob/master/src/js/setup.js
class GameMode(IntFlag):
    FalloutNV = 0
    Fallout3 = 1
    Oblivion = 2
    Skyrim = 3
    SkyrimSE = 4
    Fallout4 = 5


# Need to check these
MOGameToGameMode = [
    ("Skyrim", GameMode.Skyrim),
    ("SkyrimSE", GameMode.SkyrimSE),
    ("SkyrimVR", GameMode.SkyrimSE),  # REFER: https://github.com/z-edit/zEdit/issues/95
    # ("Enderal", GameMode.SkyrimSE), # Would this work?
    ("Fallout3", GameMode.Fallout3),
    ("Fallout4", GameMode.Fallout4),
    # ("Fallout4VR", GameMode.Fallout4),
    ("FalloutNV", GameMode.FalloutNV),
    ("Oblivion", GameMode.Oblivion),
]

qWarning = print


class ZEditConfig:

    # in user's Roaming Folder
    RELATIVE_ZEDIT_PROFILES_FILE = "../zEdit/profiles.json"

    # in zEdit's installation folder
    RELATIVE_PROFILE_DIR = "profiles"

    @staticmethod
    def loadProfile(shortGameName, profileName, zEditInstallFolder) -> Merges:
        zEditProfileDir = QDir(zEditInstallFolder + "/" + ZEditConfig.RELATIVE_PROFILE_DIR)
        if not zEditProfileDir.exists():
            qDebug("Profiles path does not exist: {}".format(zEditProfileDir.absolutePath()))
            return

        profiles = ZEditConfig.parseProfileList(shortGameName)
        for name in profiles:
            if name == profileName:
                relName = name + "/merges.json"
                if not zEditProfileDir.exists(relName):
                    qDebug('Profile "{}" does not have a "merges.json" file.'.format(name))
                    return
                try:
                    filePath = zEditProfileDir.absoluteFilePath(relName)
                    with open(filePath) as f:
                        m = Merges(json.load(f))
                        m.profileName = name
                        m.profilePath = filePath
                        return m
                except ValueError as ex:
                    qWarning('Invalid file "{}": {}'.format(filePath, str(ex)))
        qDebug('Profile "{}" was not found'.format(profileName))

    @staticmethod
    def getProfiles(shortGameName, zEditInstallFolder) -> List[Merges]:
        """ This returns the content of each profiles 'merges.json' """

        result = []
        zEditProfileDir = QDir(zEditInstallFolder + "/" + ZEditConfig.RELATIVE_PROFILE_DIR)
        if not zEditProfileDir.exists():
            qDebug("Profiles path does not exist: {}".format(zEditProfileDir.absolutePath()))
            return result

        profiles = ZEditConfig.parseProfileList(shortGameName)
        for name in profiles:
            relName = name + "/merges.json"
            if not zEditProfileDir.exists(relName):
                continue
            try:
                filePath = zEditProfileDir.absoluteFilePath(relName)
                with open(filePath) as f:
                    m = Merges(json.load(f))
                    m.profileName = name
                    m.profilePath = filePath
                    result.append(m)
            except ValueError as ex:
                qWarning('Invalid file "{}": {}'.format(filePath, str(ex)))
        return result

    @staticmethod
    def parseProfileList(shortGameName: str):
        # the profile list is stored in Roaming/zEdit/profiles.json
        result = []
        gameMode = ZEditConfig.getZEditGameMode(shortGameName)
        if gameMode is None:
            qWarning("Game type is not supported by zMerge.")
            return result

        appData = QDir(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation))
        profilesPath = appData.absoluteFilePath(ZEditConfig.RELATIVE_ZEDIT_PROFILES_FILE)
        if not appData.exists(ZEditConfig.RELATIVE_ZEDIT_PROFILES_FILE):
            qDebug('"{}" does not exist'.format(profilesPath))
            return result

        try:
            file = open(profilesPath, "r", encoding="utf8")
            profiles = json.load(file)
            for profile in profiles:
                if profile["gameMode"] == gameMode:
                    result.append(profile["name"])

        except OSError:
            qWarning('Failed to read "profiles.json".')
            return []
        except (TypeError, ValueError):
            qWarning('"profiles.json" has unknown file structure.')
        return result

    @staticmethod
    def getZEditGameMode(shortGameName: str) -> Union[GameMode, None]:
        idx = next((i for i in range(len(MOGameToGameMode)) if MOGameToGameMode[i][0] == shortGameName), -1)
        if idx >= 0:
            return MOGameToGameMode[idx][1]

    @staticmethod
    def isGameValid(shortGameName: str):
        return ZEditConfig.getZEditGameMode(shortGameName) is not None

