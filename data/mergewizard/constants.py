from enum import IntEnum, auto

# key used set/get plugin settings from MO
INTERNAL_PLUGIN_NAME = "MergeWizard"


class Icon:
    # Used by the window
    MERGEWIZARD = ":/mergewizard/icon_mergewizard"

    # used mainly in plugin views
    INACTIVE = ":/mergewizard/icon_inactive"
    MISSING = ":/mergewizard/icon_missing"
    MASTER = ":/mergewizard/icon_master"
    MERGE = ":/mergewizard/icon_merge"
    MERGED = ":/mergewizard/icon_mergable"
    MERGED_FROM_SELECTED = ":/mergewizard/icon_hollow_mergable"

    SELECTED = ":/mergewizard/icon_selected"
    SELECTED_AS_MASTER = ":/mergewizard/icon_selected_as_master"

    # shown in the info panel
    INFO_NOT_SELECTED = ":/mergewizard/icon_hollow_square_gray"
    INFO_SELECTED = ":/mergewizard/icon_filled_square_green"
    INFO_SELECTED_AS_MASTER = ":/mergewizard/icon_filled_square_purple"
    INFO_MISSING = ":/mergewizard/icon_hollow_square_red"
    INFO_MISSING_SELECTED = ":/mergewizard/icon_filled_square_red"

    # tool buttons
    FILTER = ":/mergewizard/icon_filter"
    EDIT = ":/mergewizard/icon_create"
    INFO = ":/mergewizard/icon_share"
    SETTINGS = ":/mergewizard/icon_settings"

    # log view in the action panel
    LOG_INFO = ":/mergewizard/icon_dot_blue"
    LOG_WARN = ":/mergewizard/icon_dot_yellow"
    LOG_ERROR = ":/mergewizard/icon_dot_red"
    LOG_SUCCESS = ":/mergewizard/icon_dot_green"
    LOG_DEBUG = ":/mergewizard/icon_dot_gray"

    # shown in the zmerge configuration page
    SAVE = ":/mergewizard/icon_save"
    LAUNCH = ":/mergewizard/icon_launch"

    # shown in settings dialog
    FOLDER = ":/mergewizard/icon_folder"
    ERROR = ":/mergewizard/icon_error"


"""
These are keys used by the application to access user-facing
settings stored by MO.
"""


class Setting(IntEnum):
    # hiding plugins
    ENABLE_HIDING_PLUGINS = 0
    HIDING_METHOD = auto()

    # zMerge integration
    ENABLE_ZMERGE_INTEGRATION = auto()
    ZEDIT_FOLDER = auto()
    ZEDIT_PROFILE = auto()

    # loading zMerge files
    ENABLE_LOADING_ZMERGE = auto()
    EXCLUDE_INACTIVE_MODS = auto()

    # Defaults
    USE_GAME_LOADORDER = auto()
    BUILD_MERGED_ARCHIVE = auto()
    MERGE_METHOD = auto()
    ARCHIVE_ACTION = auto()

    # asset handling
    FACE_DATA = auto()
    VOICE_DATA = auto()
    BILLBOARD_DATA = auto()
    STRINGS_DATA = auto()
    TRANSLATIONS_DATA = auto()
    INI_FILES_DATA = auto()
    DIALOGS_DATA = auto()
    GENERAL_ASSETS = auto()

    # MW - zMerge defaults
    MERGE_ORDER = auto()
    MODNAME_TEMPLATE = auto()
    PROFILENAME_TEMPLATE = auto()


"""
This is the settings information passed to MO when the plugin starts and
that allows our user-facing settings to be stored and retrieved by MO.

Each item is a tuple of (Setting, user-friendly name, tooltip, default-value)

NOTE: The tooltips are provided by the GUI. Could add tooltips here if we
include translation methods.
"""


USER_SETTINGS = [
    (Setting.ENABLE_HIDING_PLUGINS, "enable_hiding_plugins", "", True),
    (Setting.HIDING_METHOD, "hiding-method", "", 0),
    (Setting.ENABLE_ZMERGE_INTEGRATION, "enable-zMerge", "", True),
    (Setting.ZEDIT_FOLDER, "zedit-folder", "", ""),
    (Setting.ZEDIT_PROFILE, "zedit-profile", "", ""),
    (Setting.ENABLE_LOADING_ZMERGE, "enable-loading-merge-files", "", True),
    (Setting.EXCLUDE_INACTIVE_MODS, "exclude-deactivated-mods", "", True),
    (Setting.USE_GAME_LOADORDER, "use-game-loadorder", "", False),
    (Setting.BUILD_MERGED_ARCHIVE, "build_merged_archive", "", False),
    (Setting.MERGE_METHOD, "merge-method", "", 0),
    (Setting.ARCHIVE_ACTION, "archive-action", "", 0),
    (Setting.FACE_DATA, "handle-face-data", "", True),
    (Setting.VOICE_DATA, "handle-voice-data", "", True),
    (Setting.BILLBOARD_DATA, "handle-billboards", "", True),
    (Setting.STRINGS_DATA, "handle-stringfiles", "", True),
    (Setting.TRANSLATIONS_DATA, "handle-translations", "", True),
    (Setting.INI_FILES_DATA, "handle-ini-files", "", True),
    (Setting.DIALOGS_DATA, "handle-dialog-views", "", True),
    (Setting.GENERAL_ASSETS, "copy-general-assets", "", False),
    (Setting.MERGE_ORDER, "merge_order", "", 0),
    (Setting.MODNAME_TEMPLATE, "mod-name-template", "", ""),
    (Setting.PROFILENAME_TEMPLATE, "profile-name-template", "", ""),
]
