# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'G:\ModTools\ModOrganizer\plugins\data\mergewizard\build\ui\widgets\MergeInfoWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MergeInfoWidget(object):
    def setupUi(self, MergeInfoWidget):
        MergeInfoWidget.setObjectName("MergeInfoWidget")
        MergeInfoWidget.resize(857, 480)
        self.verticalLayout = QtWidgets.QVBoxLayout(MergeInfoWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(MergeInfoWidget)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.infoView = QtWidgets.QTreeView(self.groupBox)
        self.infoView.setUniformRowHeights(True)
        self.infoView.setObjectName("infoView")
        self.gridLayout.addWidget(self.infoView, 0, 0, 1, 2)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(MergeInfoWidget)
        QtCore.QMetaObject.connectSlotsByName(MergeInfoWidget)

    def retranslateUi(self, MergeInfoWidget):
        _translate = QtCore.QCoreApplication.translate
        MergeInfoWidget.setWindowTitle(_translate("MergeInfoWidget", "Form"))
        self.groupBox.setTitle(_translate("MergeInfoWidget", "Merge Info"))
