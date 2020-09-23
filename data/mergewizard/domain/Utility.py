import os, shutil


def copyFiles(src, dst, names=None):
    """ Copy files from src directory to dst directory. Subfolders are ignored.
    If names is provided, copies only files matching those names. Symlinks are not
    copies """
    if not os.path.isdir(src) or not os.path.isdir(dst):
        raise ValueError("copyDir arguments must be directories")

    for item in os.listdir(src):
        if not names or item in names:
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if not os.path.isdir(s):
                shutil.copy2(s, d, False)
