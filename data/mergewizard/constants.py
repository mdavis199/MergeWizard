# key used set/get persistent plugin settings from MO
INTERNAL_PLUGIN_NAME = "MergeWizard"


class Icon:
    # Used by the window
    MERGEWIZARD = ":/mergewizard/icon_mergewizard"

    # used in plugin views
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


class Setting:
    LOAD_ZMERGE = "Load zMerge files"
    SAVE_PLUGIN_LIST = "Save selected plugins list"

