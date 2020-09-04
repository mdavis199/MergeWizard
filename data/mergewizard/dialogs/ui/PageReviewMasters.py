# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'G:\ModTools\ModOrganizer\plugins\data\mergewizard\build\ui\dialogs\PageReviewMasters.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PageReviewMasters(object):
    def setupUi(self, PageReviewMasters):
        PageReviewMasters.setObjectName("PageReviewMasters")
        PageReviewMasters.resize(610, 429)
        self.verticalLayout = QtWidgets.QVBoxLayout(PageReviewMasters)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalSplitter = QtWidgets.QSplitter(PageReviewMasters)
        self.verticalSplitter.setOrientation(QtCore.Qt.Vertical)
        self.verticalSplitter.setObjectName("verticalSplitter")
        self.topSplitter = QtWidgets.QSplitter(self.verticalSplitter)
        self.topSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.topSplitter.setObjectName("topSplitter")
        self.masterGroup = QtWidgets.QGroupBox(self.topSplitter)
        self.masterGroup.setObjectName("masterGroup")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.masterGroup)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.masterPlugins = PluginView(self.masterGroup)
        self.masterPlugins.setObjectName("masterPlugins")
        self.gridLayout_2.addWidget(self.masterPlugins, 0, 0, 1, 1)
        self.selectedGroup = QtWidgets.QGroupBox(self.topSplitter)
        self.selectedGroup.setObjectName("selectedGroup")
        self.gridLayout = QtWidgets.QGridLayout(self.selectedGroup)
        self.gridLayout.setObjectName("gridLayout")
        self.selectedPlugins = PluginView(self.selectedGroup)
        self.selectedPlugins.setObjectName("selectedPlugins")
        self.gridLayout.addWidget(self.selectedPlugins, 0, 0, 1, 1)
        self.actionWidget = ActionWidget(self.verticalSplitter)
        self.actionWidget.setObjectName("actionWidget")
        self.verticalLayout.addWidget(self.verticalSplitter)

        self.retranslateUi(PageReviewMasters)
        QtCore.QMetaObject.connectSlotsByName(PageReviewMasters)

    def retranslateUi(self, PageReviewMasters):
        _translate = QtCore.QCoreApplication.translate
        PageReviewMasters.setWindowTitle(_translate("PageReviewMasters", "WizardPage"))
        PageReviewMasters.setTitle(_translate("PageReviewMasters", "Apply Changes"))
        PageReviewMasters.setSubTitle(_translate("PageReviewMasters", "Apply changes to enable the selected and required plugins, to disable unselected plugins, to reorder selected plugins, and to remove unnecessary mods."))
        self.masterGroup.setTitle(_translate("PageReviewMasters", "Plugin Masters"))
        self.selectedGroup.setTitle(_translate("PageReviewMasters", "Selected Plugins"))
from mergewizard.views.PluginView import PluginView
from mergewizard.widgets.ActionWidget import ActionWidget
