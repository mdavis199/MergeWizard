from typing import Set
from os import path
from glob import glob
from PyQt5.QtCore import QThread, pyqtSignal
from mergewizard.domain.merge import MergeFile
from mergewizard.domain.MOLog import moWarn


class MergeFileReader(QThread):

    progress = pyqtSignal(int)
    result = pyqtSignal(list)

    def __init__(self, modDir: str):
        super().__init__()
        self.modDir = modDir
        self._stopped = False

    def stop(self):
        self._stopped = True

    # TODO: Do we limit loading merges only from "enabled" mods?

    def run(self) -> None:
        merges: Set[MergeFile] = set()
        files = glob(self.modDir + "/*/*/merge.json")
        self._total = len(files)
        self._count = 0
        self._progress = 0

        for file in files:
            if self._stopped:
                return
            self.emitProgress()
            try:
                merge = self.loadMergeFromFile(file)
                merge.mergePath = file
                merge.modName = path.basename(path.dirname(path.dirname(file)))
                merges.add(merge)
            except OSError as ex:
                moWarn('Failed to open merge file "{}": {}'.format(file, ex.strerror))
            except ValueError as ex:
                moWarn('Failed to read merge file "{}": {}'.format(file, ex))
        self.result.emit(list(merges))

    def loadMergeFromFile(self, filepath) -> MergeFile:
        with open(filepath, "r", encoding="utf8") as f:
            merge = MergeFile.fromJSON(f.read())
            return merge

    def emitProgress(self):
        # QThread.usleep(1)
        self._count = self._count + 1
        v = int(self._count * 100 / self._total)
        if v != self._progress:
            self._progress = v
            self.progress.emit(v)

