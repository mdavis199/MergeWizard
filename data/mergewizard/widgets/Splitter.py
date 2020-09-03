from PyQt5.QtWidgets import QSplitter, QFrame, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

# REFER: https://stackoverflow.com/questions/2545577

# Note: if the splitter is above a GroupBox with text, the gripper will appear slightly
# off center, because Qt measures the distance to the top of the text, not the top of the box
# outline


class Splitter:

    # index 0 handle is always hidden,
    # index 1 handle is between two widgets
    @staticmethod
    def decorate(splitter: QSplitter, index: int = 1):

        gripLength = 35
        gripWidth = 1  # may need to be 1 or 2 depending on theme
        gripSpacing = 0
        grips = 3

        splitter.setOpaqueResize(False)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(7)
        handle = splitter.handle(index)
        orientation = splitter.orientation()
        layout = QHBoxLayout(handle)
        layout.setSpacing(gripSpacing)
        layout.setContentsMargins(0, 0, 0, 0)

        if orientation == Qt.Horizontal:
            for i in range(grips):
                line = QFrame(handle)
                line.setMinimumSize(gripWidth, gripLength)
                line.setMaximumSize(gripWidth, gripLength)
                line.setLineWidth(gripWidth)
                line.setFrameShape(line.StyledPanel)
                line.setStyleSheet("border: 1px solid lightgray;")
                layout.addWidget(line)
        else:
            # center the vertical grip by adding spacers before and after
            layout.addStretch()
            vBox = QVBoxLayout()

            for i in range(grips):
                line = QFrame(handle)
                line.setMinimumSize(gripLength, gripWidth)
                line.setMaximumSize(gripLength, gripWidth)
                line.setFrameShape(line.StyledPanel)
                line.setStyleSheet("border: 1px solid lightgray;")
                vBox.addWidget(line)
            layout.addLayout(vBox)
            layout.addStretch()
