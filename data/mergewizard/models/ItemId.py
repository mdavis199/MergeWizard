from enum import IntEnum
from PyQt5 import QtCore


INVALID_ID = 0xFFFFFFFFFFFFFFFF
INDEX_MASK = 0x00000000FFFFFFFF
PARENT_MASK = 0xFFFFFFFF00000000
ROWMASK = 0x000000000000FFFF
COLMASK = 0x00000000FFFF0000
COLSHIFT = 16
PARENTSHIFT = 32


class Depth(IntEnum):
    Invalid = -1
    D0 = 0
    D1 = 1
    D2 = 2


def idFor(row, col, parentId):
    return ((row & ROWMASK) | (col << COLSHIFT & COLMASK) | (parentId << PARENTSHIFT)) & INVALID_ID


def idForIndex(idx: QtCore.QModelIndex):
    return INVALID_ID if not idx.isValid() else idFor(idx.row(), idx.column(), idx.internalId())


def isValid(id):
    return id & INDEX_MASK != INDEX_MASK


def column(id):
    return -1 if not isValid(id) else (id & COLMASK) >> COLSHIFT


def row(id):
    return -1 if not isValid(id) else (id & ROWMASK)


def parentId(id):
    return ((id & PARENT_MASK) >> PARENTSHIFT) | PARENT_MASK


def depth(idx: QtCore.QModelIndex):
    if not idx.isValid():
        return Depth.Invalid
    if not isValid(idx.internalId()):
        return Depth.D0
    if not isValid(parentId(idx.internalId())):
        return Depth.D1
    return Depth.D2


def asStr(id):
    if isinstance(id, int):
        return "id {} I:[row: {} col: {}] P:[row: {} col:{}]".format(
            hexStr(id), row(id), column(id), row(parentId(id)), column(parentId(id))
        )
    if isinstance(id, QtCore.QModelIndex):
        return "idx: [dep: {} row: {} col: {}]  {}".format(depth(id), id.row(), id.column(), asStr(id.internalId()))


def hexStr(id):
    return "{0:#0{1}x}".format(id, 18)

