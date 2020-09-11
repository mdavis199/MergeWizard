from typing import Set, List, Callable
from glob import glob
from PyQt5.QtCore import qWarning
from mergewizard.domain.merge import Merge


class MergeFileReader:
    @staticmethod
    def loadMergeFromFile(filepath):
        with open(filepath, "r", encoding="utf8") as f:
            merge = Merge.fromJSON(f.read())
            return merge

    # TODO: we need to limit this to the mods that MO is aware of, not every recursive
    # folder in the Mods Folder.  Do we limit it to only "enabled" mods?
    @staticmethod
    def loadMerges(modDir: str, progress_callback: Callable[[], int] = None) -> List[Merge]:
        merges: Set[Merge] = set()
        files = glob(modDir + "/**/merge.json", recursive=True)
        count = 0
        for file in files:
            count = count + 1
            if progress_callback:
                progress_callback.emit(count * 100 / len(files))
            try:
                merge = MergeFileReader.loadMergeFromFile(file)
                merge.setMergePath(file)
                merges.add(merge)
            except OSError as ex:
                qWarning('Failed to open merge file "{}": {}'.format(file, ex.strerror))
            except ValueError as ex:
                qWarning('Failed to read merge file "{}": {}'.format(file, ex))
        return list(merges)
