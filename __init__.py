
import Quartz
from .cgdisplay import _DisplayCallbackDelegate, kCGErrorTypes


class DisplayCallbackDelegate(_DisplayCallbackDelegate):
    def __init__(self, display=Quartz.CGMainDisplayID()):
        super().__init__(display)

    def hideCursor(self):
        return self._hideCursor()

    def pressKey(self, key):
        return self._pressKey(key)

    def moveTo(self, x, y):
        return self._moveTo(x, y)

    def setDisplayMode(self, modeIndex):
        return self._setDisplayMode(modeIndex)

    def setTransfer(self):
        return self._setTransfer()

    def setPalette(self):
        return self._setPalette()

    def setRotation(self, angle):
        return self._setRotation(angle)

    def defaultMode(self):
        return self._defaultMode()

    def setDisplayBrightness(self, value):
        return self._setDisplayBrightness(value)

    def displayRotation(self):
        return self._displayRotation()

    def vendorNumber(self):
        return self._vendorNumber()

    def setMirror(self):
        return self._setMirror()

    def getGamma(self):
        return self._getGamma()

    def setGamma(self, red, blue, green):
        return self._setGamma(red, blue, green)

    def modeRetain(self):
        return self._modeRetain()

    def isDisplay(self):
        return self._isDisplay()

    def bestDisplayMode(self):
        return self._bestDisplayMode()

    def switchTrueTone(self):
        return self._switchTrueTone()

    def getWindowsOnDisplay(self, index=None):
        return self._getWindowsOnDisplay(index)

    def displayProperties(self):
        return self._displayProperties()

del _DisplayCallbackDelegate
__all__ = [DisplayCallbackDelegate, ]
