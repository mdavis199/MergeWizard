from enum import IntEnum, auto

# key used set/get persistent plugin settings from MO
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

    # loading zMerge files
    ENABLE_LOADING_ZMERGE = auto()
    EXCLUDE_INACTIVE_MODS = auto()

    # zMerge integration
    ENABLE_ZMERGE_INTEGRATION = auto()
    ZEDIT_FOLDER = auto()
    MERGE_ORDER = auto()
    MODNAME_TEMPLATE = auto()
    PROFILENAME_TEMPLATE = auto()


"""
These is the settings information passed to MO when the plugin starts and
that allows our user-facing settings to be stored and retrieved by MO.
There must be a one-to-one mapping with the Setting enum above.
"""


# list of context's attribute, mo-name, tooltip and default value
# NOTE: our tooltips are provided on the UI.  Can consider adding here if we
# include translation methods.
USER_SETTINGS = [
    # hiding plugins
    ("_enableHidingPlugins", "enable-plugin-hiding", "", True),
    ("_hidingMethod", "hide-method", "", "mohidden"),
    # loading zMerge files
    ("_enableLoadingMergeFiles", "enable-loading-merge-files", "", True),
    ("_excludeInactiveMods", "exclude-deactivated-mods", "", True),
    # zMerge integration
    ("_enableZMergeIntegration", "enable-zMerge", "", True),
    ("_zEditFolder", "zedit-folder", "", ""),
    ("_mergeOrder", "saving-merge_files", "", "sort"),
    ("_modNameTemplate", "mod-name-template", "", ""),
    ("_profileNameTemplate", "profile-name-template", "", ""),
]
