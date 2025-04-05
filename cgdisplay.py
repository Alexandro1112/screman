import time
import Quartz  # noqa F401
import ctypes
import abc
import objc
from typing import Dict

__all__ = ['DisplayCallbackDelegate', ]


class _MonitorPanelLoader:

    """
        ... _MonitorPanelLoader load private framework MonitorPanel and init require class in global variable.
    """
    _globals = {}  # define globals dict before loading, it requires if framework fails to load.

    def __init__(self):
        objc.loadBundle(
            'MonitorPanel',
            bundle_path=objc.pathForFramework('/System/Library/PrivateFrameworks/MonitorPanel.framework'),
            module_globals=globals(),
        )

    def passAttributes(self) -> Dict:
        """ Not necessary function, but intuitive understood, if bundle isn't loading.
        .. versionadded:: 0.0.1"""
        if self._globals != globals():
            return globals()
        return self._globals


# create define exceptions and error classes


class QErrorNoneAvailable(NotImplementedError):
    pass

class kCGErrorTypes(IOError):  # noqa
    """
        Universal type for associations error codes added.
       .. versionadded:: 0.0.1
    """
    def __init__(self, n):
        pass


class CGDisplayDelegate:
    def __init__(self, display: Quartz.CGMainDisplayID() = 0) -> None:

        for k, v in globals().items():
            setattr(self, k, v)

        self.display = Quartz.CGMainDisplayID() or display  # define main display reference in abc class.
        self._mp_display = None
        self.status: kCGErrorTypes = kCGErrorTypes(0)

    def __abs__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def hideCursor(self):
        pass

    @abc.abstractmethod
    def moveTo(self, x, y):
        pass

    @abc.abstractmethod
    def setDisplayMode(self, modeIndex):
        pass

    @abc.abstractmethod
    def setTransfer(self):
        pass

    @abc.abstractmethod
    def setPalette(self):
        pass

    @abc.abstractmethod
    def setRotation(self, angle):
        pass

    @abc.abstractmethod
    def defaultMode(self):
        pass

    @abc.abstractmethod
    def setDisplayBrightness(self, value):
        pass

    @abc.abstractmethod
    def displayRotation(self):
        pass

    @abc.abstractmethod
    def vendorNumber(self):
        pass

    @abc.abstractmethod
    def setMirror(self):
        pass


class DisplayCallbackDelegate(CGDisplayDelegate):

    """
        ... DisplayCallbackDelegate can interact with
            display setting between external and internal displays.
            Inherit from CGDisplayDelegate, class facilitates interaction with display settings.

    """

    _kCGErrorSuccess: kCGErrorTypes = 0
    _kCGErrorFailure: kCGErrorTypes = 1000
    _kCGErrorIllegalArgument: kCGErrorTypes = 1001
    _kCGErrorNoneAvailable: kCGErrorTypes = 1011
    _kDisplayVendorIDUnknown = 1970170734  # defined in IOGraphicsTypes.h

    def hideCursor(self) -> _kCGErrorSuccess:
        """ Hides the mouse cursor, and increments the hide cursor count.
            .. versionadded:: 0.0.1 """
        hide = Quartz.CGDisplayHideCursor(self.display)
        return hide

    def moveTo(self, x, y) -> _kCGErrorSuccess:
        """ Moves the mouse cursor to a specified point
        relative to the display origin (the upper left corner of the display).
            .. versionadded:: 0.0.1
        """
        status = Quartz.CGDisplayMoveCursorToPoint(
            self.display,
            Quartz.CGRect(x, y)
        )
        if status == self._kCGErrorSuccess:
            return
        return status

    def setDisplayMode(self, modeIndex) -> _kCGErrorSuccess:
        """ Switches a display to a different mode.
            .. versionadded:: 0.0.1 """
        modes = Quartz.CGDisplayAvailableModes(self.display)[modeIndex]
        if modeIndex <= 0 or modeIndex >= len(modes):
            return self._kCGErrorIllegalArgument

        status = Quartz.CGDisplaySwitchToMode(
            self.display,
            modes

        )
        if status == self._kCGErrorSuccess:
            return
        return status

    def setTransfer(self) -> _kCGErrorSuccess:
        """ Sets the byte values in the 8-bit RGB gamma tables for a display.
            .. versionadded:: 0.0.1 """
        def _tables():
            table_size = Quartz.kCGDisplayEnabledFlag
            red_table = (ctypes.c_ubyte * table_size)()
            green_table = (ctypes.c_ubyte * table_size)()
            blue_table = (ctypes.c_ubyte * table_size)()
            # Create rgb range and pass for 3 last arguments color values

            for rgb in range(table_size):
                red_table[rgb] = rgb
                green_table[rgb] = rgb
                blue_table[rgb] = rgb
                return red_table, green_table, blue_table

        self.status = Quartz.CGSetDisplayTransferByByteTable(
            self.display,
            len((ctypes.c_ubyte * Quartz.kCGDisplayEnabledFlag)()),
            *_tables()


        )
        time.sleep(0.02)
        # make delay between executing function, it needs if function is called for a continuous times.

        if self.status == self._kCGErrorSuccess:
            return
        return self.status

    def setPalette(self) -> _kCGErrorSuccess:
        """Sets the palette for a display.
            .. versionadded:: 0.0.1
        """

        self.status = Quartz.CGDisplaySetPalette(
            self.display,
            None
        )

        if self.status == self._kCGErrorNoneAvailable:
            raise QErrorNoneAvailable(
                f'Sorry, {self.setPalette.__name__!r}(:_:) currently not supported by this OS version.')

        elif self.status == self._kCGErrorSuccess:
            return

    def setRotation(self, angle) -> _kCGErrorSuccess:
        """Rotate display at determine angle multiple to 90.
            .. versionadded:: 0.0.1
        """

        _isLoad = _MonitorPanelLoader().passAttributes()
        if _isLoad:
            self._mp_display = _isLoad['MPDisplay'].alloc().initWithCGSDisplayID_(self.display)
            return self._mp_display

        _isCan = bool(self._mp_display.canChangeOrientation())
        if _isCan:
            self.status = self._mp_display.setOrientation_(angle)
            if self.status == self._kCGErrorSuccess:
                return
            elif not angle % 90 == 0:
                return self._kCGErrorIllegalArgument
            return self.status  # real unknown status

    def defaultMode(self):
        """Create desc with summary values of init display.
            .. versionadded:: 0.0.1 """
        pass

    def setDisplayBrightness(self, value) -> _kCGErrorSuccess:
        """regulating brightness of screen to value
            .. versionadded:: 0.0.1
        """
        _controller = Quartz.IKMonitorBrightnessController.alloc().init()
        try:
            self.status = _controller.setBrightnessOnAllDisplays_(value)
        except ValueError:
            return self._kCGErrorIllegalArgument
        finally:
            return self._kCGErrorSuccess

    def displayRotation(self) -> _kCGErrorSuccess:
        """
        Returns the rotation angle of a display in degrees.
            .. versionadded:: 0.0.1
        """
        angle = Quartz.CGDisplayRotation(self.display)
        return int(angle)

    def vendorNumber(self):
        """
        Returns the vendor number of the specified display's monitor.A vendor number for the monitor associated with
         the specified display, or a constant to indicate an exception.

        .. versionadded:: 0.0.1
        """
        _v_number = Quartz.CGDisplayVendorNumber(self.display)
        if hex(_v_number) == 0xFFFFFFFF:  # If there is no monitor associated with the display
            return None
        elif _v_number == self._kDisplayVendorIDUnknown:  # If I/O Kit cannot identify the monitor,
            # kDisplayVendorIDUnknown is returned
            return None
        return _v_number

    def setMirror(self):
        """Changes the configuration of a mirroring set.
        .. versionadded:: 0.0.1 """
        err, config = Quartz.CGBeginDisplayConfiguration(None)
        Quartz.CGConfigureDisplayMirrorOfDisplay(config, self.display, Quartz.kCGNullDirectDisplay)
        options = Quartz.kCGConfigureForSession & Quartz.kCGConfigureForAppOnly

        self.status = Quartz.CGCompleteDisplayConfiguration(config, options)
        if self.status == self._kCGErrorSuccess:
            return
        elif self.status == self._kCGErrorIllegalArgument:
            return None
        return self.status







