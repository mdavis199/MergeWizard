from PyQt5.QtCore import pyqtSignal, Qt, QPoint
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QWidget, QListWidget, QListWidgetItem, QAction, QMenu

from mergewizard.constants import Icon
from mergewizard.models.PluginFilterModel import Filter


class PluginFilterBox(QListWidget):

    # Emitted when a filter changes. Give the
    # changed Filter enum and its checked status
    filterChanged = pyqtSignal(Filter, bool)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        defaultFlags = Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

        item = QListWidgetItem(self.tr("Inactive Plugins"))
        item.setIcon(QIcon(Icon.INACTIVE))
        item.setToolTip(self.tr("Plugins that are not active in the current profile."))
        item.setData(Qt.UserRole, Filter.Inactive)
        item.setData(Qt.UserRole + 1, 0)
        item.setFlags(defaultFlags)
        item.setCheckState(Qt.Unchecked)
        self.addItem(item)

        item = QListWidgetItem(self.tr("Missing Plugins"))
        item.setIcon(QIcon(Icon.MISSING))
        item.setToolTip(self.tr("Plugins that were not found or may be in deactivated mods."))
        item.setData(Qt.UserRole, Filter.Missing)
        item.setData(Qt.UserRole + 1, 1)
        item.setFlags(defaultFlags)
        item.setCheckState(Qt.Unchecked)
        self.addItem(item)

        item = QListWidgetItem(self.tr("Plugin Masters"))
        item.setIcon(QIcon(Icon.MASTER))
        item.setToolTip(self.tr("Plugins tagged as a master library."))
        item.setData(Qt.UserRole, Filter.Masters)
        item.setData(Qt.UserRole + 1, 2)
        item.setFlags(defaultFlags)
        item.setCheckState(Qt.Unchecked)
        self.addItem(item)

        item = QListWidgetItem(self.tr("Plugin Merges"))
        item.setIcon(QIcon(Icon.MERGE))
        item.setToolTip(self.tr("Plugins that were created by a merge."))
        item.setData(Qt.UserRole, Filter.Merges)
        item.setData(Qt.UserRole + 1, 3)
        item.setFlags(defaultFlags)
        item.setCheckState(Qt.Unchecked)
        self.addItem(item)

        item = QListWidgetItem(self.tr("Merged Plugins"))
        item.setIcon(QIcon(Icon.MERGED))
        item.setToolTip(self.tr("Plugins that were consumed by a merge."))
        item.setData(Qt.UserRole, Filter.Merged)
        item.setData(Qt.UserRole + 1, 4)
        item.setFlags(defaultFlags)
        item.setCheckState(Qt.Unchecked)
        self.addItem(item)

        item = QListWidgetItem(self.tr("Required Plugins"))
        item.setIcon(QIcon(Icon.SELECTED_AS_MASTER))
        item.setToolTip(self.tr("Plugins required by selected plugins."))
        item.setData(Qt.UserRole, Filter.SelectedAsMaster)
        item.setData(Qt.UserRole + 1, 5)
        item.setFlags(defaultFlags)
        item.setCheckState(Qt.Unchecked)
        self.addItem(item)

        item = QListWidgetItem(self.tr("Selected Plugins"))
        item.setIcon(QIcon(Icon.SELECTED))
        item.setToolTip(self.tr("Plugins to be included in the current merge."))
        item.setData(Qt.UserRole, Filter.Selected)
        item.setData(Qt.UserRole + 1, 6)
        item.setFlags(defaultFlags)
        item.setCheckState(Qt.Unchecked)
        self.addItem(item)

        self.setUniformItemSizes(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFixedHeight(self.sizeHintForRow(0) * self.count() + 2 * self.frameWidth())

        enableAll = QAction(self.tr("Enable All"), self)
        enableAll.setShortcut(QKeySequence.SelectAll)
        enableAll.setShortcutContext(Qt.WidgetShortcut)
        enableAll.triggered.connect(lambda: self.enableAll())

        enableNone = QAction(self.tr("Enable None"), self)
        enableNone.setShortcut(Qt.CTRL + Qt.Key_N)
        enableNone.setShortcutContext(Qt.WidgetShortcut)
        enableNone.triggered.connect(lambda: self.enableNone())

        self.addActions([enableAll, enableNone])
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.itemChanged.connect(self.onItemChanged)

    def onItemChanged(self, item: QListWidgetItem):
        self.filterChanged.emit(item.data(Qt.UserRole), item.checkState() == Qt.Checked)

    def enableAll(self):
        for i in range(self.count()):
            self.item(i).setCheckState(Qt.Checked)

    def enableNone(self):
        for i in range(self.count()):
            self.item(i).setCheckState(Qt.Unchecked)

    def enableFilters(self, filter_: Filter, enable: bool = True):
        for i in range(self.count()):
            if filter_ & self.item(i).data(Qt.UserRole):
                isChecked = self.item(i).checkState() == Qt.Checked
                if isChecked != enable:
                    self.item(i).setCheckState(Qt.Checked if enable else Qt.Unchecked)

    def showContextMenu(self, pos: QPoint):
        menu = QMenu()
        menu.addActions(self.actions())
        menu.exec(self.mapToGlobal(pos))

