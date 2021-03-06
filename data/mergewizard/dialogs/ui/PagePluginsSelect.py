# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'G:\ModTools\ModOrganizer\plugins\data\mergewizard\build\ui\dialogs\PagePluginsSelect.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PagePluginsSelect(object):
    def setupUi(self, PagePluginsSelect):
        PagePluginsSelect.setObjectName("PagePluginsSelect")
        PagePluginsSelect.resize(990, 698)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(PagePluginsSelect)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.splitter = QtWidgets.QSplitter(PagePluginsSelect)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.pluginGroup = QtWidgets.QGroupBox(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pluginGroup.sizePolicy().hasHeightForWidth())
        self.pluginGroup.setSizePolicy(sizePolicy)
        self.pluginGroup.setObjectName("pluginGroup")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.pluginGroup)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.allPluginsSplitter = QtWidgets.QSplitter(self.pluginGroup)
        self.allPluginsSplitter.setOrientation(QtCore.Qt.Vertical)
        self.allPluginsSplitter.setObjectName("allPluginsSplitter")
        self.layoutWidget = QtWidgets.QWidget(self.allPluginsSplitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.allPluginsTopLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.allPluginsTopLayout.setContentsMargins(0, 0, 0, 0)
        self.allPluginsTopLayout.setObjectName("allPluginsTopLayout")
        self.pluginsList = PluginView(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pluginsList.sizePolicy().hasHeightForWidth())
        self.pluginsList.setSizePolicy(sizePolicy)
        self.pluginsList.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed)
        self.pluginsList.setDragEnabled(True)
        self.pluginsList.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.pluginsList.setDefaultDropAction(QtCore.Qt.IgnoreAction)
        self.pluginsList.setAlternatingRowColors(True)
        self.pluginsList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.pluginsList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.pluginsList.setSortingEnabled(True)
        self.pluginsList.setExpandsOnDoubleClick(False)
        self.pluginsList.setObjectName("pluginsList")
        self.pluginsList.header().setCascadingSectionResizes(True)
        self.pluginsList.header().setMinimumSectionSize(18)
        self.pluginsList.header().setStretchLastSection(True)
        self.allPluginsTopLayout.addWidget(self.pluginsList)
        self.pluginFilterWidget = PluginFilterBox(self.layoutWidget)
        self.pluginFilterWidget.setObjectName("pluginFilterWidget")
        self.allPluginsTopLayout.addWidget(self.pluginFilterWidget)
        self.filterEditLayout = QtWidgets.QHBoxLayout()
        self.filterEditLayout.setObjectName("filterEditLayout")
        self.toggleFilterButton = QtWidgets.QToolButton(self.layoutWidget)
        self.toggleFilterButton.setObjectName("toggleFilterButton")
        self.filterEditLayout.addWidget(self.toggleFilterButton)
        self.filterEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.filterEdit.setClearButtonEnabled(True)
        self.filterEdit.setObjectName("filterEdit")
        self.filterEditLayout.addWidget(self.filterEdit)
        self.filterCount = QtWidgets.QLabel(self.layoutWidget)
        self.filterCount.setObjectName("filterCount")
        self.filterEditLayout.addWidget(self.filterCount)
        self.allPluginsTopLayout.addLayout(self.filterEditLayout)
        self.allStacked = QtWidgets.QStackedWidget(self.allPluginsSplitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.allStacked.sizePolicy().hasHeightForWidth())
        self.allStacked.setSizePolicy(sizePolicy)
        self.allStacked.setObjectName("allStacked")
        self.pluginInfoWidget = PluginInfoWidget()
        self.pluginInfoWidget.setObjectName("pluginInfoWidget")
        self.allStacked.addWidget(self.pluginInfoWidget)
        self.mergeInfoWidget = MergeInfoWidget()
        self.mergeInfoWidget.setObjectName("mergeInfoWidget")
        self.allStacked.addWidget(self.mergeInfoWidget)
        self.verticalLayout_2.addWidget(self.allPluginsSplitter)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.togglePluginInfoButton = QtWidgets.QToolButton(self.pluginGroup)
        self.togglePluginInfoButton.setObjectName("togglePluginInfoButton")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.togglePluginInfoButton)
        self.toggleMergeInfoButton = QtWidgets.QToolButton(self.pluginGroup)
        self.toggleMergeInfoButton.setObjectName("toggleMergeInfoButton")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.toggleMergeInfoButton)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.pluginSelectionGroup = QtWidgets.QGroupBox(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pluginSelectionGroup.sizePolicy().hasHeightForWidth())
        self.pluginSelectionGroup.setSizePolicy(sizePolicy)
        self.pluginSelectionGroup.setObjectName("pluginSelectionGroup")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.pluginSelectionGroup)
        self.verticalLayout.setObjectName("verticalLayout")
        self.selectedPluginsSplitter = QtWidgets.QSplitter(self.pluginSelectionGroup)
        self.selectedPluginsSplitter.setOrientation(QtCore.Qt.Vertical)
        self.selectedPluginsSplitter.setObjectName("selectedPluginsSplitter")
        self.selectedPluginsList = PluginView(self.selectedPluginsSplitter)
        self.selectedPluginsList.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.EditKeyPressed)
        self.selectedPluginsList.setDragEnabled(True)
        self.selectedPluginsList.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.selectedPluginsList.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.selectedPluginsList.setAlternatingRowColors(True)
        self.selectedPluginsList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.selectedPluginsList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.selectedPluginsList.setExpandsOnDoubleClick(False)
        self.selectedPluginsList.setObjectName("selectedPluginsList")
        self.selectedPluginsList.header().setCascadingSectionResizes(True)
        self.selectedPluginsList.header().setMinimumSectionSize(18)
        self.selectedPluginsList.header().setStretchLastSection(False)
        self.selectedStacked = QtWidgets.QStackedWidget(self.selectedPluginsSplitter)
        self.selectedStacked.setObjectName("selectedStacked")
        self.bulkAddWidget = PluginTextWidget()
        self.bulkAddWidget.setObjectName("bulkAddWidget")
        self.selectedStacked.addWidget(self.bulkAddWidget)
        self.mergeSelectWidget = MergeSelectWidget()
        self.mergeSelectWidget.setObjectName("mergeSelectWidget")
        self.selectedStacked.addWidget(self.mergeSelectWidget)
        self.verticalLayout.addWidget(self.selectedPluginsSplitter)
        self.buttonLayout = QtWidgets.QFormLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.toggleBulkButton = QtWidgets.QToolButton(self.pluginSelectionGroup)
        self.toggleBulkButton.setObjectName("toggleBulkButton")
        self.buttonLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.toggleBulkButton)
        self.toggleMergeButton = QtWidgets.QToolButton(self.pluginSelectionGroup)
        self.toggleMergeButton.setObjectName("toggleMergeButton")
        self.buttonLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.toggleMergeButton)
        self.verticalLayout.addLayout(self.buttonLayout)
        self.verticalLayout_3.addWidget(self.splitter)

        self.retranslateUi(PagePluginsSelect)
        QtCore.QMetaObject.connectSlotsByName(PagePluginsSelect)
        PagePluginsSelect.setTabOrder(self.pluginsList, self.selectedPluginsList)
        PagePluginsSelect.setTabOrder(self.selectedPluginsList, self.toggleFilterButton)
        PagePluginsSelect.setTabOrder(self.toggleFilterButton, self.filterEdit)
        PagePluginsSelect.setTabOrder(self.filterEdit, self.togglePluginInfoButton)
        PagePluginsSelect.setTabOrder(self.togglePluginInfoButton, self.toggleMergeInfoButton)
        PagePluginsSelect.setTabOrder(self.toggleMergeInfoButton, self.toggleBulkButton)
        PagePluginsSelect.setTabOrder(self.toggleBulkButton, self.toggleMergeButton)

    def retranslateUi(self, PagePluginsSelect):
        _translate = QtCore.QCoreApplication.translate
        PagePluginsSelect.setWindowTitle(_translate("PagePluginsSelect", "WizardPage"))
        PagePluginsSelect.setTitle(_translate("PagePluginsSelect", "Plugin Selection"))
        PagePluginsSelect.setSubTitle(_translate("PagePluginsSelect", "Create an ordered list of plugins to include in the merge."))
        self.pluginGroup.setTitle(_translate("PagePluginsSelect", "Plugin List"))
        self.filterEdit.setPlaceholderText(_translate("PagePluginsSelect", "Filter plugins by name ..."))
        self.filterCount.setText(_translate("PagePluginsSelect", "Filtering: 0/0"))
        self.pluginSelectionGroup.setTitle(_translate("PagePluginsSelect", "Selected Plugins"))
from mergewizard.views.PluginView import PluginView
from mergewizard.widgets.MergeInfoWidget import MergeInfoWidget
from mergewizard.widgets.MergeSelectWidget import MergeSelectWidget
from mergewizard.widgets.PluginFilterBox import PluginFilterBox
from mergewizard.widgets.PluginInfoWidget import PluginInfoWidget
from mergewizard.widgets.PluginTextWidget import PluginTextWidget
