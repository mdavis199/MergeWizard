from PyQt5.QtCore import qInfo, qWarning, qDebug, qCritical


def moInfo(msg: str):
    qInfo("[mw] " + msg)


def moWarn(msg: str):
    qWarning("[mw] " + msg)


def moDebug(msg: str):
    qDebug("[mw] " + msg)


def moError(msg: str):
    qCritical("[mw] " + msg)


def moTime(time: float, msg: str):
    qDebug("[mw] [{:.9f}] [{:.9f}] {}".format(time, 0, msg))


def moPerf(start: float, stop: float, msg: str):
    qDebug("[mw] [{:.9f}] [{:.9f}] {}".format(stop, stop - start, msg))
