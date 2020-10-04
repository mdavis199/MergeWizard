# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'G:\ModTools\ModOrganizer\plugins\data\mergewizard\build\ui\dialogs\PageZMerge.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PageZMerge(object):
    def setupUi(self, PageZMerge):
        PageZMerge.setObjectName("PageZMerge")
        PageZMerge.resize(1048, 692)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(PageZMerge)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.splitter = QtWidgets.QSplitter(PageZMerge)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.zMergeBox = QtWidgets.QGroupBox(self.splitter)
        self.zMergeBox.setObjectName("zMergeBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.zMergeBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.zMergeConfigView = QtWidgets.QTreeView(self.zMergeBox)
        self.zMergeConfigView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.zMergeConfigView.setUniformRowHeights(True)
        self.zMergeConfigView.setObjectName("zMergeConfigView")
        self.zMergeConfigView.header().setMinimumSectionSize(1)
        self.zMergeConfigView.header().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.zMergeConfigView)
        self.originalBox = QtWidgets.QGroupBox(self.splitter)
        self.originalBox.setObjectName("originalBox")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.originalBox)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.originalConfigView = QtWidgets.QTreeView(self.originalBox)
        self.originalConfigView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.originalConfigView.setUniformRowHeights(True)
        self.originalConfigView.setObjectName("originalConfigView")
        self.originalConfigView.header().setMinimumSectionSize(1)
        self.originalConfigView.header().setStretchLastSection(False)
        self.verticalLayout_9.addWidget(self.originalConfigView)
        self.horizontalLayout_2.addWidget(self.splitter)
        self.options = QtWidgets.QWidget(PageZMerge)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.options.sizePolicy().hasHeightForWidth())
        self.options.setSizePolicy(sizePolicy)
        self.options.setMaximumSize(QtCore.QSize(300, 16777215))
        self.options.setObjectName("options")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.options)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(15)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.generalOptions = QtWidgets.QGroupBox(self.options)
        self.generalOptions.setObjectName("generalOptions")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.generalOptions)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.useGameLoadOrder = QtWidgets.QCheckBox(self.generalOptions)
        self.useGameLoadOrder.setObjectName("useGameLoadOrder")
        self.verticalLayout_5.addWidget(self.useGameLoadOrder)
        self.buildMergedArchive = QtWidgets.QCheckBox(self.generalOptions)
        self.buildMergedArchive.setObjectName("buildMergedArchive")
        self.verticalLayout_5.addWidget(self.buildMergedArchive)
        self.verticalLayout_3.addWidget(self.generalOptions)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mergeMethod = QtWidgets.QGroupBox(self.options)
        self.mergeMethod.setObjectName("mergeMethod")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.mergeMethod)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.clobber = QtWidgets.QRadioButton(self.mergeMethod)
        self.clobber.setChecked(True)
        self.clobber.setObjectName("clobber")
        self.methodGroup = QtWidgets.QButtonGroup(PageZMerge)
        self.methodGroup.setObjectName("methodGroup")
        self.methodGroup.addButton(self.clobber)
        self.verticalLayout_8.addWidget(self.clobber)
        self.clean = QtWidgets.QRadioButton(self.mergeMethod)
        self.clean.setObjectName("clean")
        self.methodGroup.addButton(self.clean)
        self.verticalLayout_8.addWidget(self.clean)
        self.horizontalLayout.addWidget(self.mergeMethod)
        self.archiveAction = QtWidgets.QGroupBox(self.options)
        self.archiveAction.setObjectName("archiveAction")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.archiveAction)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.extract = QtWidgets.QRadioButton(self.archiveAction)
        self.extract.setChecked(True)
        self.extract.setObjectName("extract")
        self.archiveGroup = QtWidgets.QButtonGroup(PageZMerge)
        self.archiveGroup.setObjectName("archiveGroup")
        self.archiveGroup.addButton(self.extract)
        self.verticalLayout_6.addWidget(self.extract)
        self.copy = QtWidgets.QRadioButton(self.archiveAction)
        self.copy.setObjectName("copy")
        self.archiveGroup.addButton(self.copy)
        self.verticalLayout_6.addWidget(self.copy)
        self.ignore = QtWidgets.QRadioButton(self.archiveAction)
        self.ignore.setObjectName("ignore")
        self.archiveGroup.addButton(self.ignore)
        self.verticalLayout_6.addWidget(self.ignore)
        self.horizontalLayout.addWidget(self.archiveAction)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.assetHandling = QtWidgets.QGroupBox(self.options)
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
        self.verticalLayout_3.addWidget(self.assetHandling)
        self.groupBox_2 = QtWidgets.QGroupBox(self.options)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.moProfileLabel = QtWidgets.QLabel(self.groupBox_2)
        self.moProfileLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.moProfileLabel.setObjectName("moProfileLabel")
        self.gridLayout.addWidget(self.moProfileLabel, 1, 0, 1, 1)
        self.moProfile = QtWidgets.QLineEdit(self.groupBox_2)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        self.moProfile.setPalette(palette)
        self.moProfile.setReadOnly(True)
        self.moProfile.setObjectName("moProfile")
        self.gridLayout.addWidget(self.moProfile, 1, 1, 1, 1)
        self.clearplaceholder = QtWidgets.QLabel(self.groupBox_2)
        self.clearplaceholder.setMinimumSize(QtCore.QSize(18, 18))
        self.clearplaceholder.setMaximumSize(QtCore.QSize(18, 18))
        self.clearplaceholder.setObjectName("clearplaceholder")
        self.gridLayout.addWidget(self.clearplaceholder, 1, 2, 1, 1)
        self.modNameLabel = QtWidgets.QLabel(self.groupBox_2)
        self.modNameLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.modNameLabel.setObjectName("modNameLabel")
        self.gridLayout.addWidget(self.modNameLabel, 2, 0, 1, 1)
        self.modName = QtWidgets.QComboBox(self.groupBox_2)
        self.modName.setObjectName("modName")
        self.gridLayout.addWidget(self.modName, 2, 1, 1, 1)
        self.modNameError = QtWidgets.QLabel(self.groupBox_2)
        self.modNameError.setMinimumSize(QtCore.QSize(18, 18))
        self.modNameError.setMaximumSize(QtCore.QSize(18, 18))
        self.modNameError.setObjectName("modNameError")
        self.gridLayout.addWidget(self.modNameError, 2, 2, 1, 1)
        self.pluginNameLabel = QtWidgets.QLabel(self.groupBox_2)
        self.pluginNameLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.pluginNameLabel.setObjectName("pluginNameLabel")
        self.gridLayout.addWidget(self.pluginNameLabel, 3, 0, 1, 1)
        self.pluginName = QtWidgets.QLineEdit(self.groupBox_2)
        self.pluginName.setObjectName("pluginName")
        self.gridLayout.addWidget(self.pluginName, 3, 1, 1, 1)
        self.pluginNameError = QtWidgets.QLabel(self.groupBox_2)
        self.pluginNameError.setMinimumSize(QtCore.QSize(18, 18))
        self.pluginNameError.setMaximumSize(QtCore.QSize(18, 18))
        self.pluginNameError.setObjectName("pluginNameError")
        self.gridLayout.addWidget(self.pluginNameError, 3, 2, 1, 1)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        self.warningFrame = QtWidgets.QFrame(self.options)
        self.warningFrame.setStyleSheet("#warningFrame {border: 1px solid red; }")
        self.warningFrame.setFrameShape(QtWidgets.QFrame.Panel)
        self.warningFrame.setObjectName("warningFrame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.warningFrame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.warningIcon = QtWidgets.QLabel(self.warningFrame)
        self.warningIcon.setText("")
        self.warningIcon.setPixmap(QtGui.QPixmap("G:\\ModTools\\ModOrganizer\\plugins\\data\\mergewizard\\build\\ui\\dialogs\\../../resources/warning-red.svg"))
        self.warningIcon.setObjectName("warningIcon")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.warningIcon)
        self.warningLabel = QtWidgets.QLabel(self.warningFrame)
        self.warningLabel.setWordWrap(True)
        self.warningLabel.setObjectName("warningLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.warningLabel)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.verticalLayout_3.addWidget(self.warningFrame)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.frame = QtWidgets.QFrame(self.options)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setObjectName("frame")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.line_2 = QtWidgets.QFrame(self.frame)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_10.addWidget(self.line_2)
        self.toggleOriginal = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toggleOriginal.sizePolicy().hasHeightForWidth())
        self.toggleOriginal.setSizePolicy(sizePolicy)
        self.toggleOriginal.setCheckable(True)
        self.toggleOriginal.setObjectName("toggleOriginal")
        self.verticalLayout_10.addWidget(self.toggleOriginal)
        self.launchButton = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.launchButton.sizePolicy().hasHeightForWidth())
        self.launchButton.setSizePolicy(sizePolicy)
        self.launchButton.setObjectName("launchButton")
        self.verticalLayout_10.addWidget(self.launchButton)
        self.line = QtWidgets.QFrame(self.frame)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_10.addWidget(self.line)
        self.applyButton = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.applyButton.sizePolicy().hasHeightForWidth())
        self.applyButton.setSizePolicy(sizePolicy)
        self.applyButton.setObjectName("applyButton")
        self.verticalLayout_10.addWidget(self.applyButton)
        self.verticalLayout_3.addWidget(self.frame)
        self.horizontalLayout_2.addWidget(self.options)
        self.moProfileLabel.setBuddy(self.moProfile)
        self.modNameLabel.setBuddy(self.modName)
        self.pluginNameLabel.setBuddy(self.pluginName)

        self.retranslateUi(PageZMerge)
        QtCore.QMetaObject.connectSlotsByName(PageZMerge)
        PageZMerge.setTabOrder(self.zMergeConfigView, self.applyButton)
        PageZMerge.setTabOrder(self.applyButton, self.useGameLoadOrder)
        PageZMerge.setTabOrder(self.useGameLoadOrder, self.buildMergedArchive)
        PageZMerge.setTabOrder(self.buildMergedArchive, self.clobber)
        PageZMerge.setTabOrder(self.clobber, self.clean)
        PageZMerge.setTabOrder(self.clean, self.extract)
        PageZMerge.setTabOrder(self.extract, self.copy)
        PageZMerge.setTabOrder(self.copy, self.ignore)
        PageZMerge.setTabOrder(self.ignore, self.faceData)
        PageZMerge.setTabOrder(self.faceData, self.voiceData)
        PageZMerge.setTabOrder(self.voiceData, self.billboardData)
        PageZMerge.setTabOrder(self.billboardData, self.stringFiles)
        PageZMerge.setTabOrder(self.stringFiles, self.translations)
        PageZMerge.setTabOrder(self.translations, self.iniFiles)
        PageZMerge.setTabOrder(self.iniFiles, self.dialogViews)
        PageZMerge.setTabOrder(self.dialogViews, self.generalAssets)
        PageZMerge.setTabOrder(self.generalAssets, self.moProfile)
        PageZMerge.setTabOrder(self.moProfile, self.modName)
        PageZMerge.setTabOrder(self.modName, self.pluginName)

    def retranslateUi(self, PageZMerge):
        _translate = QtCore.QCoreApplication.translate
        PageZMerge.setWindowTitle(_translate("PageZMerge", "WizardPage"))
        PageZMerge.setTitle(_translate("PageZMerge", "zMerge Configuration"))
        PageZMerge.setSubTitle(_translate("PageZMerge", "Create or modify a zMerge configuration for the selected plugins."))
        self.zMergeBox.setTitle(_translate("PageZMerge", "Merge Configuration"))
        self.originalBox.setTitle(_translate("PageZMerge", "Original"))
        self.generalOptions.setTitle(_translate("PageZMerge", "General"))
        self.useGameLoadOrder.setText(_translate("PageZMerge", "Use Game Load Order"))
        self.buildMergedArchive.setText(_translate("PageZMerge", "Build Merged Archive"))
        self.mergeMethod.setTitle(_translate("PageZMerge", "Merge Method"))
        self.clobber.setText(_translate("PageZMerge", "Clobber"))
        self.clean.setText(_translate("PageZMerge", "Clean"))
        self.archiveAction.setTitle(_translate("PageZMerge", "Archive Action"))
        self.extract.setText(_translate("PageZMerge", "Extract"))
        self.copy.setText(_translate("PageZMerge", "Copy"))
        self.ignore.setText(_translate("PageZMerge", "Ignore"))
        self.assetHandling.setTitle(_translate("PageZMerge", "Asset Handling"))
        self.faceData.setText(_translate("PageZMerge", "Handle Face Data"))
        self.voiceData.setText(_translate("PageZMerge", "Handle Voice Data"))
        self.billboardData.setText(_translate("PageZMerge", "Hande Billboard"))
        self.stringFiles.setText(_translate("PageZMerge", "Handle String Files"))
        self.translations.setText(_translate("PageZMerge", "Handle Translations"))
        self.iniFiles.setText(_translate("PageZMerge", "Handle Ini Files"))
        self.dialogViews.setText(_translate("PageZMerge", "Handle Dialog Views"))
        self.generalAssets.setText(_translate("PageZMerge", "Copy General Assets"))
        self.groupBox_2.setTitle(_translate("PageZMerge", "Mod and Plugin Names"))
        self.moProfileLabel.setText(_translate("PageZMerge", "MO Profile:"))
        self.modNameLabel.setText(_translate("PageZMerge", "Mod Name:"))
        self.pluginNameLabel.setText(_translate("PageZMerge", "Plugin Name:"))
        self.warningLabel.setText(_translate("PageZMerge", "Please update the zEdit path and profile in settings."))
        self.toggleOriginal.setText(_translate("PageZMerge", "View Original"))
        self.launchButton.setText(_translate("PageZMerge", "Launch zMerge"))
        self.applyButton.setText(_translate("PageZMerge", "Save Changes"))
