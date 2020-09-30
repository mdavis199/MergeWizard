from mobase import IOrganizer
from mergewizard.domain.SettingsBase import SettingsBase, Validator
from mergewizard.constants import INTERNAL_PLUGIN_NAME, USER_SETTINGS, Setting as UserSetting

Validator = Validator
# These use static methods and can be shared among the settings.
DEFAULT_VALIDATOR = Validator.default()
BOOLEAN_VALIDATOR = Validator.boolean()
INT_VALIDATOR = Validator.integer()


class Settings(SettingsBase):
    def __init__(self, organizer: IOrganizer):
        super().__init__()
        self._organizer = organizer
        self._initializeUserSettings()

    # ----
    # ---- Public settings stored in MO's user interface
    # ----

    def loadUserSettings(self):
        for key in UserSetting:
            setting = self.setting(key)
            if setting:
                setting.value = self._getUserSetting(setting.name)

    def storeUserSettings(self):
        for key in UserSetting:
            setting = self.setting(key)
            if setting:
                self._setUserSetting(setting.name, setting.value)

    def _setUserSetting(self, name, value, pluginName=None):
        self._organizer.setPluginSetting(INTERNAL_PLUGIN_NAME if not pluginName else pluginName, name, value)

    def _getUserSetting(self, name, pluginName=None):
        return self._organizer.pluginSetting(INTERNAL_PLUGIN_NAME if not pluginName else pluginName, name)

    def _validateHidingMethod(self, x, default):
        values = ["mohidden", "optional", "disable"]
        if x is not None:
            return x
        x = self._getUserSetting("hide-type", "Merge Plugins Hide")
        if x:
            x = x.lower()
            return values.index(x) if x in values else default

    def _initializeUserSettings(self):

        # NOTE: This needs to be one-to-one with constants USER_SETTINGS
        VALIDATORS = [
            (UserSetting.ENABLE_HIDING_PLUGINS, BOOLEAN_VALIDATOR),
            (UserSetting.HIDING_METHOD, Validator.custom(self._validateHidingMethod)),
            (UserSetting.ENABLE_ZMERGE_INTEGRATION, BOOLEAN_VALIDATOR),
            (UserSetting.ZEDIT_FOLDER, Validator.folder("zedit.exe")),
            (UserSetting.ZEDIT_PROFILE, DEFAULT_VALIDATOR),
            (UserSetting.ENABLE_LOADING_ZMERGE, BOOLEAN_VALIDATOR),
            (UserSetting.EXCLUDE_INACTIVE_MODS, BOOLEAN_VALIDATOR),
            (UserSetting.USE_GAME_LOADORDER, BOOLEAN_VALIDATOR),
            (UserSetting.BUILD_MERGED_ARCHIVE, BOOLEAN_VALIDATOR),
            (UserSetting.MERGE_METHOD, Validator.range(0, 1)),
            (UserSetting.ARCHIVE_ACTION, Validator.range(0, 2)),
            (UserSetting.FACE_DATA, BOOLEAN_VALIDATOR),
            (UserSetting.VOICE_DATA, BOOLEAN_VALIDATOR),
            (UserSetting.BILLBOARD_DATA, BOOLEAN_VALIDATOR),
            (UserSetting.STRINGS_DATA, BOOLEAN_VALIDATOR),
            (UserSetting.TRANSLATIONS_DATA, BOOLEAN_VALIDATOR),
            (UserSetting.INI_FILES_DATA, BOOLEAN_VALIDATOR),
            (UserSetting.DIALOGS_DATA, BOOLEAN_VALIDATOR),
            (UserSetting.GENERAL_ASSETS, BOOLEAN_VALIDATOR),
            (UserSetting.MERGE_ORDER, Validator.range(0, 4)),
            (UserSetting.MODNAME_TEMPLATE, DEFAULT_VALIDATOR),
            (UserSetting.PROFILENAME_TEMPLATE, DEFAULT_VALIDATOR),
        ]

        assert len(UserSetting) == len(USER_SETTINGS) == len(VALIDATORS)
        for i in range(len(USER_SETTINGS)):
            self.add(USER_SETTINGS[i][0], USER_SETTINGS[i][1], USER_SETTINGS[i][3], VALIDATORS[i][1])

    # ----
    # ---- Semi-private settings stored in modorganizer.ini
    # ----
    # ---- These settings are typically used in only one class or file, so we
    # ---- do not use predefined keys to access them or store cached values.
    # ----

    def setInternal(self, name: str, value) -> None:
        # self.organizer.setPersistent(INTERNAL_PLUGIN_NAME, name, QVariant(value))
        self._organizer.setPersistent(INTERNAL_PLUGIN_NAME, name, value, True)

    def internal(self, name: str, default=None, validator=DEFAULT_VALIDATOR):
        return validator.validate(self._organizer.persistent(INTERNAL_PLUGIN_NAME, name), default)

