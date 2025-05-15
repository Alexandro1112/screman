import Quartz
from .cgdisplay import _DisplayCallbackDelegate, kCGErrorTypes
from .cgdisplaystream import DisplayStreamDelegate
from .helpers import getbounds, createbounds

class DisplayCallbackDelegate(_DisplayCallbackDelegate):
    def __init__(self, display=Quartz.CGMainDisplayID(), builtin=True):
        super().__init__(display, builtin)

    def hideCursor(self):
        return self._hideCursor()

    def pressKey(self, key):
        return self._pressKey(key)

    def moveTo(self, x, y):
        return self._moveTo(x, y)

    def setDisplayMode(self, modeIndex):
        return self._setDisplayMode(modeIndex)

    def setTransfer(self, tableNum):
        return self._setTransfer(tableNum)

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

    def getWindowsOnDisplay(self, w_number=None):
        return self._getWindowsOnDisplay(w_number)

    def displayProperties(self):
        return self._displayProperties()

    def displayColorSetting(self):
        return self._displayColorSetting()

    def isActiveNow(self):
        return self._isActiveNow()

    def getDisplayBrightness(self):
        return self._getDisplayBrightness()


del _DisplayCallbackDelegate
__all__ = [DisplayCallbackDelegate, DisplayStreamDelegate, getbounds, createbounds]
