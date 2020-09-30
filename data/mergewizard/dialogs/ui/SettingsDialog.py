# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'G:\ModTools\ModOrganizer\plugins\data\mergewizard\build\ui\dialogs\SettingsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        SettingsDialog.setObjectName("SettingsDialog")
        SettingsDialog.resize(514, 601)
        self.gridLayout = QtWidgets.QGridLayout(SettingsDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(SettingsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(SettingsDialog)
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setObjectName("tabWidget")
        self.generalTab = QtWidgets.QWidget()
        self.generalTab.setObjectName("generalTab")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.generalTab)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.enableHiding = QtWidgets.QGroupBox(self.generalTab)
        self.enableHiding.setCheckable(True)
        self.enableHiding.setObjectName("enableHiding")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.enableHiding)
        self.verticalLayout_9.setContentsMargins(25, -1, -1, -1)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.hide = QtWidgets.QRadioButton(self.enableHiding)
        self.hide.setChecked(True)
        self.hide.setObjectName("hide")
        self.hidePluginsGroup = QtWidgets.QButtonGroup(SettingsDialog)
        self.hidePluginsGroup.setObjectName("hidePluginsGroup")
        self.hidePluginsGroup.addButton(self.hide)
        self.verticalLayout_9.addWidget(self.hide)
        self.move = QtWidgets.QRadioButton(self.enableHiding)
        self.move.setObjectName("move")
        self.hidePluginsGroup.addButton(self.move)
        self.verticalLayout_9.addWidget(self.move)
        self.disable = QtWidgets.QRadioButton(self.enableHiding)
        self.disable.setObjectName("disable")
        self.hidePluginsGroup.addButton(self.disable)
        self.verticalLayout_9.addWidget(self.disable)
        self.verticalLayout_6.addWidget(self.enableHiding)
        self.enableZMerge = QtWidgets.QGroupBox(self.generalTab)
        self.enableZMerge.setCheckable(True)
        self.enableZMerge.setObjectName("enableZMerge")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.enableZMerge)
        self.verticalLayout_8.setContentsMargins(25, -1, -1, -1)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.zeditPathGroup = QtWidgets.QGroupBox(self.enableZMerge)
        self.zeditPathGroup.setObjectName("zeditPathGroup")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.zeditPathGroup)
        self.horizontalLayout_4.setContentsMargins(9, -1, -1, -1)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.zeditPathEdit = QtWidgets.QLineEdit(self.zeditPathGroup)
        self.zeditPathEdit.setObjectName("zeditPathEdit")
        self.horizontalLayout_4.addWidget(self.zeditPathEdit)
        self.zeditPathButton = QtWidgets.QToolButton(self.zeditPathGroup)
        self.zeditPathButton.setObjectName("zeditPathButton")
        self.horizontalLayout_4.addWidget(self.zeditPathButton)
        self.zeditPathError = QtWidgets.QLabel(self.zeditPathGroup)
        self.zeditPathError.setMinimumSize(QtCore.QSize(16, 16))
        self.zeditPathError.setMaximumSize(QtCore.QSize(16, 16))
        self.zeditPathError.setText("")
        self.zeditPathError.setObjectName("zeditPathError")
        self.horizontalLayout_4.addWidget(self.zeditPathError)
        self.verticalLayout_8.addWidget(self.zeditPathGroup)
        self.profileGroup = QtWidgets.QGroupBox(self.enableZMerge)
        self.profileGroup.setObjectName("profileGroup")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.profileGroup)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.zeditProfile = QtWidgets.QComboBox(self.profileGroup)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.zeditProfile.sizePolicy().hasHeightForWidth())
        self.zeditProfile.setSizePolicy(sizePolicy)
        self.zeditProfile.setObjectName("zeditProfile")
        self.horizontalLayout_2.addWidget(self.zeditProfile)
        self.zeditProfileError = QtWidgets.QLabel(self.profileGroup)
        self.zeditProfileError.setMinimumSize(QtCore.QSize(16, 16))
        self.zeditProfileError.setMaximumSize(QtCore.QSize(16, 16))
        self.zeditProfileError.setText("")
        self.zeditProfileError.setObjectName("zeditProfileError")
        self.horizontalLayout_2.addWidget(self.zeditProfileError)
        self.verticalLayout_8.addWidget(self.profileGroup)
        self.verticalLayout_6.addWidget(self.enableZMerge)
        self.enableLoadingZMerge = QtWidgets.QGroupBox(self.generalTab)
        self.enableLoadingZMerge.setCheckable(True)
        self.enableLoadingZMerge.setObjectName("enableLoadingZMerge")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.enableLoadingZMerge)
        self.horizontalLayout_7.setContentsMargins(25, -1, -1, -1)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.excludeInactiveMods = QtWidgets.QCheckBox(self.enableLoadingZMerge)
        self.excludeInactiveMods.setObjectName("excludeInactiveMods")
        self.horizontalLayout_7.addWidget(self.excludeInactiveMods)
        self.verticalLayout_6.addWidget(self.enableLoadingZMerge)
        self.groupBox = QtWidgets.QGroupBox(self.generalTab)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.textEdit = QtWidgets.QTextEdit(self.groupBox)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 238))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 238))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 238))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        self.textEdit.setPalette(palette)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_2.addWidget(self.textEdit)
        self.verticalLayout_6.addWidget(self.groupBox)
        self.tabWidget.addTab(self.generalTab, "")
        self.defaultsTab = QtWidgets.QWidget()
        self.defaultsTab.setObjectName("defaultsTab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.defaultsTab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.generalOptions = QtWidgets.QGroupBox(self.defaultsTab)
        self.generalOptions.setObjectName("generalOptions")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.generalOptions)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.useGameLoadOrder = QtWidgets.QCheckBox(self.generalOptions)
        self.useGameLoadOrder.setObjectName("useGameLoadOrder")
        self.verticalLayout_5.addWidget(self.useGameLoadOrder)
        self.buildMergedArchive = QtWidgets.QCheckBox(self.generalOptions)
        self.buildMergedArchive.setObjectName("buildMergedArchive")
        self.verticalLayout_5.addWidget(self.buildMergedArchive)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem)
        self.horizontalLayout.addWidget(self.generalOptions)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.mergeMethod = QtWidgets.QGroupBox(self.defaultsTab)
        self.mergeMethod.setObjectName("mergeMethod")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.mergeMethod)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.clobber = QtWidgets.QRadioButton(self.mergeMethod)
        self.clobber.setChecked(True)
        self.clobber.setObjectName("clobber")
        self.mergeMethodGroup = QtWidgets.QButtonGroup(SettingsDialog)
        self.mergeMethodGroup.setObjectName("mergeMethodGroup")
        self.mergeMethodGroup.addButton(self.clobber)
        self.horizontalLayout_3.addWidget(self.clobber)
        self.clean = QtWidgets.QRadioButton(self.mergeMethod)
        self.clean.setObjectName("clean")
        self.mergeMethodGroup.addButton(self.clean)
        self.horizontalLayout_3.addWidget(self.clean)
        self.verticalLayout_3.addWidget(self.mergeMethod)
        self.archiveAction = QtWidgets.QGroupBox(self.defaultsTab)
        self.archiveAction.setObjectName("archiveAction")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.archiveAction)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.extract = QtWidgets.QRadioButton(self.archiveAction)
        self.extract.setChecked(True)
        self.extract.setObjectName("extract")
        self.archiveActionGroup = QtWidgets.QButtonGroup(SettingsDialog)
        self.archiveActionGroup.setObjectName("archiveActionGroup")
        self.archiveActionGroup.addButton(self.extract)
        self.horizontalLayout_5.addWidget(self.extract)
        self.copy = QtWidgets.QRadioButton(self.archiveAction)
        self.copy.setObjectName("copy")
        self.archiveActionGroup.addButton(self.copy)
        self.horizontalLayout_5.addWidget(self.copy)
        self.ignore = QtWidgets.QRadioButton(self.archiveAction)
        self.ignore.setObjectName("ignore")
        self.archiveActionGroup.addButton(self.ignore)
        self.horizontalLayout_5.addWidget(self.ignore)
        self.verticalLayout_3.addWidget(self.archiveAction)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.assetHandling = QtWidgets.QGroupBox(self.defaultsTab)
        self.assetHandling.setObjectName("assetHandling")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.assetHandling)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.faceData = QtWidgets.QCheckBox(self.assetHandling)
        self.faceData.setChecked(True)
        self.faceData.setObjectName("faceData")
        self.verticalLayout_4.addWidget(self.faceData)
        self.voiceData = QtWidgets.QCheckBox(self.assetHandling)
        self.voiceData.setChecked(True)
        self.voiceData.setObjectName("voiceData")
        self.verticalLayout_4.addWidget(self.voiceData)
        self.billboardData = QtWidgets.QCheckBox(self.assetHandling)
        self.billboardData.setChecked(True)
        self.billboardData.setObjectName("billboardData")
        self.verticalLayout_4.addWidget(self.billboardData)
        self.stringFiles = QtWidgets.QCheckBox(self.assetHandling)
        self.stringFiles.setChecked(True)
        self.stringFiles.setObjectName("stringFiles")
        self.verticalLayout_4.addWidget(self.stringFiles)
        self.horizontalLayout_6.addLayout(self.verticalLayout_4)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.translations = QtWidgets.QCheckBox(self.assetHandling)
        self.translations.setChecked(True)
        self.translations.setObjectName("translations")
        self.verticalLayout_7.addWidget(self.translations)
        self.iniFiles = QtWidgets.QCheckBox(self.assetHandling)
        self.iniFiles.setChecked(True)
        self.iniFiles.setObjectName("iniFiles")
        self.verticalLayout_7.addWidget(self.iniFiles)
        self.dialogViews = QtWidgets.QCheckBox(self.assetHandling)
        self.dialogViews.setChecked(True)
        self.dialogViews.setObjectName("dialogViews")
        self.verticalLayout_7.addWidget(self.dialogViews)
        self.generalAssets = QtWidgets.QCheckBox(self.assetHandling)
        self.generalAssets.setObjectName("generalAssets")
        self.verticalLayout_7.addWidget(self.generalAssets)
        self.horizontalLayout_6.addLayout(self.verticalLayout_7)
        self.verticalLayout.addWidget(self.assetHandling)
        self.groupBox_5 = QtWidgets.QGroupBox(self.defaultsTab)
        self.groupBox_5.setObjectName("groupBox_5")
        self.formLayout_5 = QtWidgets.QFormLayout(self.groupBox_5)
        self.formLayout_5.setContentsMargins(9, -1, -1, -1)
        self.formLayout_5.setObjectName("formLayout_5")
        self.sort = QtWidgets.QRadioButton(self.groupBox_5)
        self.sort.setChecked(True)
        self.sort.setObjectName("sort")
        self.savingMergesGroup = QtWidgets.QButtonGroup(SettingsDialog)
        self.savingMergesGroup.setObjectName("savingMergesGroup")
        self.savingMergesGroup.addButton(self.sort)
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.sort)
        self.prependNew = QtWidgets.QRadioButton(self.groupBox_5)
        self.prependNew.setObjectName("prependNew")
        self.savingMergesGroup.addButton(self.prependNew)
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.prependNew)
        self.appendNew = QtWidgets.QRadioButton(self.groupBox_5)
        self.appendNew.setObjectName("appendNew")
        self.savingMergesGroup.addButton(self.appendNew)
        self.formLayout_5.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.appendNew)
        self.prependChanged = QtWidgets.QRadioButton(self.groupBox_5)
        self.prependChanged.setObjectName("prependChanged")
        self.savingMergesGroup.addButton(self.prependChanged)
        self.formLayout_5.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.prependChanged)
        self.appendChanged = QtWidgets.QRadioButton(self.groupBox_5)
        self.appendChanged.setObjectName("appendChanged")
        self.savingMergesGroup.addButton(self.appendChanged)
        self.formLayout_5.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.appendChanged)
        self.verticalLayout.addWidget(self.groupBox_5)
        self.groupBox_4 = QtWidgets.QGroupBox(self.defaultsTab)
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_2.setContentsMargins(9, -1, -1, -1)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_10 = QtWidgets.QLabel(self.groupBox_4)
        self.label_10.setObjectName("label_10")
        self.gridLayout_2.addWidget(self.label_10, 0, 0, 1, 1)
        self.profileNameTemplate = QtWidgets.QLineEdit(self.groupBox_4)
        self.profileNameTemplate.setText("")
        self.profileNameTemplate.setPlaceholderText("")
        self.profileNameTemplate.setObjectName("profileNameTemplate")
        self.gridLayout_2.addWidget(self.profileNameTemplate, 0, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.groupBox_4)
        self.label_11.setObjectName("label_11")
        self.gridLayout_2.addWidget(self.label_11, 1, 0, 1, 1)
        self.modNameTemplate = QtWidgets.QLineEdit(self.groupBox_4)
        self.modNameTemplate.setText("")
        self.modNameTemplate.setPlaceholderText("")
        self.modNameTemplate.setObjectName("modNameTemplate")
        self.gridLayout_2.addWidget(self.modNameTemplate, 1, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.groupBox_4)
        self.label_12.setWordWrap(False)
        self.label_12.setObjectName("label_12")
        self.gridLayout_2.addWidget(self.label_12, 2, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_4)
        self.tabWidget.addTab(self.defaultsTab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(SettingsDialog)
        self.tabWidget.setCurrentIndex(0)
        self.buttonBox.accepted.connect(SettingsDialog.accept)
        self.buttonBox.rejected.connect(SettingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SettingsDialog)

    def retranslateUi(self, SettingsDialog):
        _translate = QtCore.QCoreApplication.translate
        SettingsDialog.setWindowTitle(_translate("SettingsDialog", "Dialog"))
        self.enableHiding.setToolTip(_translate("SettingsDialog", "These options implement some of the features of Deorder\'s excellent plugin: \"Merge Plugins Hide\""))
        self.enableHiding.setTitle(_translate("SettingsDialog", "Enable Hiding Plugins"))
        self.hide.setToolTip(_translate("SettingsDialog", "Renames the plugin by appending the extension \'.mohidden\'."))
        self.hide.setText(_translate("SettingsDialog", "Hide plugin"))
        self.move.setToolTip(_translate("SettingsDialog", "Moves the plugin to the \'optional\' folder."))
        self.move.setText(_translate("SettingsDialog", "Move to \"Optional\" folder"))
        self.disable.setToolTip(_translate("SettingsDialog", "Disables the plugin."))
        self.disable.setText(_translate("SettingsDialog", "Disable plugin"))
        self.enableZMerge.setTitle(_translate("SettingsDialog", "Enable zMerge Integration"))
        self.zeditPathGroup.setTitle(_translate("SettingsDialog", "zEdit Installation Directory"))
        self.zeditPathEdit.setToolTip(_translate("SettingsDialog", "This directory contains zEdit\'s \'profiles\' folder."))
        self.zeditPathButton.setText(_translate("SettingsDialog", "..."))
        self.zeditPathError.setToolTip(_translate("SettingsDialog", "Path does not include \"zedit.exe\"."))
        self.profileGroup.setTitle(_translate("SettingsDialog", "zEdit Profile"))
        self.zeditProfileError.setToolTip(_translate("SettingsDialog", "Path does not include \"zedit.exe\"."))
        self.enableLoadingZMerge.setToolTip(_translate("SettingsDialog", "Incorporate info from \"merge.json\" files located in mod folders."))
        self.enableLoadingZMerge.setTitle(_translate("SettingsDialog", "Enable Loading zMerge JSON Files"))
        self.excludeInactiveMods.setToolTip(_translate("SettingsDialog", "Excludes loading zMerge files from deactivated mods."))
        self.excludeInactiveMods.setText(_translate("SettingsDialog", "Do not import file information from deactivated mods."))
        self.textEdit.setHtml(_translate("SettingsDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Enable zMerge Integration</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">When this option is enabled, the zEdit profile will be scanned for configured merges. This will detect plugins that have been selected for a merge even if the merged plugin has not been built. This option will also enable editing and creating zEdit merge configurations from within MergeWizard.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This option will not detect built merges whose configurations were deleted from the profile.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Enable Loading zMerge JSON Files</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">When this option is enabled, merge details are loaded from &quot;merge.json&quot; files located in mod folders.  </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This option will not detect merges that are configured but not built. </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">You may want to enable this option if you have merges that were deleted from zEdit\'s profile.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">If both options are enabled:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The information in the profile may differ from the information in the mod folder if the merge was changed but not yet rebuilt.  MergeWizard gives priority to the configuration in the profile.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.generalTab), _translate("SettingsDialog", "General"))
        self.generalOptions.setTitle(_translate("SettingsDialog", "General"))
        self.useGameLoadOrder.setText(_translate("SettingsDialog", "Use Game Load Order"))
        self.buildMergedArchive.setText(_translate("SettingsDialog", "Build Merged Archive"))
        self.mergeMethod.setTitle(_translate("SettingsDialog", "Merge Method"))
        self.clobber.setText(_translate("SettingsDialog", "Clobber"))
        self.clean.setText(_translate("SettingsDialog", "Clean"))
        self.archiveAction.setTitle(_translate("SettingsDialog", "Archive Action"))
        self.extract.setText(_translate("SettingsDialog", "Extract"))
        self.copy.setText(_translate("SettingsDialog", "Copy"))
        self.ignore.setText(_translate("SettingsDialog", "Ignore"))
        self.assetHandling.setTitle(_translate("SettingsDialog", "Asset Handling"))
        self.faceData.setText(_translate("SettingsDialog", "Handle Face Data"))
        self.voiceData.setText(_translate("SettingsDialog", "Handle Voice Data"))
        self.billboardData.setText(_translate("SettingsDialog", "Hande Billboard"))
        self.stringFiles.setText(_translate("SettingsDialog", "Handle String Files"))
        self.translations.setText(_translate("SettingsDialog", "Handle Translations"))
        self.iniFiles.setText(_translate("SettingsDialog", "Handle Ini Files"))
        self.dialogViews.setText(_translate("SettingsDialog", "Handle Dialog Views"))
        self.generalAssets.setText(_translate("SettingsDialog", "Copy General Assets"))
        self.groupBox_5.setTitle(_translate("SettingsDialog", "Saving Merges"))
        self.sort.setToolTip(_translate("SettingsDialog", "When saving changes to zMerge configuration, sort the merges by mod name."))
        self.sort.setText(_translate("SettingsDialog", "Sort merges by mod name"))
        self.prependNew.setToolTip(_translate("SettingsDialog", "When adding or editing a merge, place the merge first in zMerge\'s configuration."))
        self.prependNew.setText(_translate("SettingsDialog", "Place new mods at front of list"))
        self.appendNew.setToolTip(_translate("SettingsDialog", "When adding or editing a merge, place the merge last in zMerge\'s configuration."))
        self.appendNew.setText(_translate("SettingsDialog", "Place new mods at end of list"))
        self.prependChanged.setText(_translate("SettingsDialog", "Place new and changed mods at front of list"))
        self.appendChanged.setText(_translate("SettingsDialog", "Place new and changed mods at end of list"))
        self.groupBox_4.setTitle(_translate("SettingsDialog", "Name Templates for New Merges"))
        self.label_10.setText(_translate("SettingsDialog", "Profile Name"))
        self.profileNameTemplate.setToolTip(_translate("SettingsDialog", "For new merges, attempt to derive the plugin name from the profile name."))
        self.label_11.setText(_translate("SettingsDialog", "Mod Name"))
        self.modNameTemplate.setToolTip(_translate("SettingsDialog", "For new merges, attempt to derive the mod name from the plugin name. "))
        self.label_12.setText(_translate("SettingsDialog", "$ is a placeholder for the basename of the generated plugin."))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.defaultsTab), _translate("SettingsDialog", "Defaults for New Merges"))
