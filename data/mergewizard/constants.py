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
    INFO = ":/mergewizard/icon_info"
    SETTINGS = ":/mergewizard/icon_settings"

    # shown in action panel
    ERROR = ":/mergewizard/icon_error"

    # shown in settings dialog
    FOLDER = ":/mergewizard/icon_folder"


"""
These are keys used by the application to access user-facing
settings stored by MO.
"""


class Setting(IntEnum):
    ENABLE_HIDING_PLUGINS = 0
    HIDING_METHOD = auto()
    EXCLUDE_INACTIVE_MODS = auto()
    ZEDIT_FOLDER = auto()
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
    ("_enableHidingPlugins", "enable-plugin-hiding", "", True),
    ("_hidingMethod", "hide-method", "", "mohidden"),
    ("_excludeInactiveMods", "exclude-deactivated-mods", "", False),
    ("_zEditFolder", "zedit-folder", "", ""),
    ("_modNameTemplate", "mod-name-template", "", ""),
    ("_profileNameTemplate", "profile-name-template", "", ""),
]
