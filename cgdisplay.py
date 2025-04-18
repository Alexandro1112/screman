import time
import Quartz # noqa F401
import ctypes
import abc
import objc


# create exceptions and error classes


class QErrorNoneAvailable(NotImplementedError):
    pass


class QErrorWrongArgument(ValueError):
    pass


class kCGErrorTypes(IOError):  # noqa
    """
        Universal type for associations error codes added.
       .. versionadded:: 0.0.1
    """
    def __init__(self, n):
        pass


class Helpers:
    @staticmethod
    def err_to_exception(err):
        query_exc = {
             0: '_kCGErrorSuccess',
             1000: '_kCGErrorFailure',
             1001: '_kCGErrorIllegalArgument',
             1011: '_kCGErrorNoneAvailable',
             1970170734: '_kDisplayVendorIDUnknown',
             1007: '_kCGErrorRangeCheck'


        }
        return query_exc[err]


class CGDisplayDelegate:
    def __init__(self, display: Quartz.CGMainDisplayID() = 0) -> None:
        self.display = display or Quartz.CGMainDisplayID()  # define main display reference in abc class.

        self._mp_display = None
        self.status: kCGErrorTypes = kCGErrorTypes(0)

    def __abs__(self):
        raise NotImplementedError

    def _load(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _hideCursor(self):
        pass

    @abc.abstractmethod
    def _moveTo(self, x, y):
        pass

    @abc.abstractmethod
    def _setDisplayMode(self, modeIndex):
        pass

    @abc.abstractmethod
    def _setTransfer(self):
        pass

    @abc.abstractmethod
    def _setPalette(self):
        pass

    @abc.abstractmethod
    def _setRotation(self, angle):
        pass

    @abc.abstractmethod
    def _defaultMode(self):
        pass

    @abc.abstractmethod
    def _setDisplayBrightness(self, value):
        pass

    @abc.abstractmethod
    def _displayRotation(self):
        pass

    @abc.abstractmethod
    def _vendorNumber(self):
        pass

    @abc.abstractmethod
    def _setMirror(self):
        pass

    @abc.abstractmethod
    def _getGamma(self):
        pass

    @abc.abstractmethod
    def _setGamma(self, red, blue, green):
        pass

    @abc.abstractmethod
    def _modeRetain(self):
        pass

    @abc.abstractmethod
    def _isDisplay(self, n):
        pass

    @abc.abstractmethod
    def _bestDisplayMode(self):
        pass


class _DisplayCallbackDelegate(CGDisplayDelegate):

    """
        ... DisplayCallbackDelegate can interact with
            display setting between external and internal displays.
            Inherit from CGDisplayDelegate, class facilitates interaction with display settings.

    """

    _kCGErrorSuccess: kCGErrorTypes = 0
    _kCGErrorFailure: kCGErrorTypes = 1000
    _kCGErrorIllegalArgument: kCGErrorTypes = 1001
    _kCGErrorNoneAvailable: kCGErrorTypes = 1011
    _kDisplayVendorIDUnknown: kCGErrorTypes = 1970170734  # defined in IOGraphicsTypes.h
    _kCGErrorRangeCheck: kCGErrorTypes = 1007
    _kDisplayModeNativeFlag = 33554432  # defined in bridge.bridgesupport and in IOGraphicsTypes.h

    def __int__(self):
        return self.display

    def __le__(self, other):
        return self.display >= 0

    def __lt__(self, other):
        return self.display <= 0

    def __repr__(self):
        return '<' + _DisplayCallbackDelegate.__name__.__repr__() + f' with display at {repr(self.display)} index>'

    def _hideCursor(self) -> _kCGErrorSuccess:
        """ Hides the mouse cursor, and increments the hide cursor count.
                Mac Catalyst 13.1+
                macOS 10.0+
            .. versionadded:: 0.0.1 """
        self.status = Quartz.CGDisplayHideCursor(self.display)
        time.sleep(0.05)
        # make delay between executing function, it needs if function is called for a continuous times.

        return self.status

    def _moveTo(self, x, y) -> _kCGErrorSuccess:
        """ Moves the mouse cursor to a specified point
        relative to the display origin (the upper left corner of the display).
                Mac Catalyst 13.1+
                macOS 10.0+
            .. versionadded:: 0.0.1
            ..versionupdate:: 0.0.3
        """
        w, h = Quartz.CGDisplayBounds(self.display).size
        if x >= w or y >= h:
            return self._kCGErrorIllegalArgument

        self.status = Quartz.CGDisplayMoveCursorToPoint(
            self.display,
            Quartz.CGRect(x, y)
        )
        if self.status == self._kCGErrorSuccess:
            return
        return self.status

    def _setDisplayMode(self, modeIndex) -> _kCGErrorSuccess:
        """ Switches a display to a different mode.
        In an update 0.0.3 I prefer use a MPDisplay for switches modes, because it sets the modes for a long time.
            .. versionadded:: 0.0.1
            .. versionupdate:: 0.0.3"""
        _isLoadMp = self._load()
        if _isLoadMp:
            display = _isLoadMp['MPDisplay'].alloc().initWithCGSDisplayID_(self.display)
            modes = display.allModes()
            if modeIndex <= 0 or modeIndex >= len(modes):
                return self._kCGErrorIllegalArgument

            _mode = modes[modeIndex]
            self.status = display.setMode_(_mode)

            if self.status == self._kCGErrorSuccess:
                return self._kCGErrorSuccess
            return self.status

    def _setTransfer(self) -> _kCGErrorSuccess:
        """ Sets the byte values in the 8-bit RGB gamma tables for a display.
                Mac Catalyst 13.1+
                macOS 10.0+
                .. versionadded:: 0.0.1
        """
        def tables():
            table_size = Quartz.kCGDisplayEnabledFlag
            red_table = (ctypes.c_ubyte * table_size)()
            green_table = (ctypes.c_ubyte * table_size)()
            blue_table = (ctypes.c_ubyte * table_size)()
            # Create rgb range and pass for 3 last arguments color values

            for rgb in range(table_size):
                red_table[rgb] = ctypes.c_ubyte(rgb * 3)
                green_table[rgb] = ctypes.c_ubyte(rgb * 4)
                blue_table[rgb] = ctypes.c_ubyte(rgb * 5)
                return red_table, green_table, blue_table

        self.status = Quartz.CGSetDisplayTransferByByteTable(
            self.display,
            1,
            *tables()


        )
        time.sleep(0.02)
        # make delay between executing function, it needs if function is called for a continuous times.

        if self.status == self._kCGErrorSuccess:
            return self._kCGErrorSuccess
        return self.status

    def _load(self):
        _globals = {}  # define globals dict before loading, it requires if framework fails to load.
        objc.loadBundle(
            'MonitorPanel',
            bundle_path=objc.pathForFramework('/System/Library/PrivateFrameworks/MonitorPanel.framework'),
            module_globals=globals(),
        )
        if _globals != globals():
            return globals()
        return _globals  # pragma: no cover

    def _setPalette(self) -> _kCGErrorSuccess:
        """Sets the palette for a display.
            .. versionadded:: 0.0.1
        """
        if Quartz.CGDisplayCanSetPalette(self.display):
            self.status = Quartz.CGDisplaySetPalette(
                self.display,
                None
            )

            if self.status == self._kCGErrorNoneAvailable:
                raise QErrorNoneAvailable(
                    f'Sorry, {self._setPalette.__name__}(:_:) currently not supported by this OS version.')

            elif self.status == self._kCGErrorSuccess:
                return self._kCGErrorSuccess
        return self._kCGErrorNoneAvailable

    def _setRotation(self, angle) -> _kCGErrorSuccess:
        """Rotate display at determine angle multiple to 90.
            .. versionadded:: 0.0.1
        """
        _isLoadMp = self._load()

        if _isLoadMp:
            self._mp_display = _isLoadMp['MPDisplay'].alloc().initWithCGSDisplayID_(self.display)
            _isCan = bool(self._mp_display.canChangeOrientation())
            if _isCan:
                self.status = self._mp_display.setOrientation_(angle)
                if self.status == self._kCGErrorSuccess:
                    return self._kCGErrorSuccess
                elif not angle % 90 == 0:
                    return self._kCGErrorIllegalArgument
                return self.status  # real unknown status
            return None
        raise QErrorNoneAvailable(
            'MonitorPanel framework failed to loading'
        )

    def _defaultMode(self) -> _kCGErrorSuccess:
        """Create desc with summary values of init display.
            .. versionadded:: 0.0.1 """
        _isLoadMp = self._load()

        if _isLoadMp:
            self._mp_display = _isLoadMp['MPDisplay'].alloc().initWithCGSDisplayID_(self.display)
            if self._mp_display.defaultMode():
                return self._mp_display.defaultMode()
            return self._kCGErrorNoneAvailable

    def _setDisplayBrightness(self, value) -> _kCGErrorSuccess:
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

    def _displayRotation(self) -> _kCGErrorSuccess:
        """
        Returns the rotation angle of a display in degrees.
             .. Mac Catalyst 13.1+
            .. macOS 10.5+
            .. versionadded:: 0.0.1
        """
        angle = Quartz.CGDisplayRotation(self.display)
        return int(angle)

    def _vendorNumber(self) -> _kCGErrorSuccess:
        """
        Returns the vendor number of the specified display's monitor.A vendor number for the monitor associated with
         the specified display, or a constant to indicate an exception.
            .. Mac Catalyst 13.1+
            .. macOS 10.2+
            .. versionadded:: 0.0.1
        """
        _v_number = Quartz.CGDisplayVendorNumber(self.display)
        if hex(_v_number) == 0xFFFFFFFF:  # If there is no monitor associated with the display
            return None
        elif _v_number == self._kDisplayVendorIDUnknown:  # If I/O Kit cannot identify the monitor
            # kDisplayVendorIDUnknown is returned
            return self._kDisplayVendorIDUnknown
        return _v_number

    def _setMirror(self) -> _kCGErrorSuccess:
        """Changes the configuration of a mirroring set.
            .. Mac Catalyst 13.1+
            .. macOS 10.2+
            .. versionadded:: 0.0.1 """
        err, config = Quartz.CGBeginDisplayConfiguration(None)
        Quartz.CGConfigureDisplayMirrorOfDisplay(config, self.display, Quartz.kCGNullDirectDisplay)

        options = (Quartz.kCGConfigureForSession & Quartz.kCGConfigureForAppOnly)

        self.status = Quartz.CGCompleteDisplayConfiguration(config, options)
        if self.status == self._kCGErrorSuccess:
            return self._kCGErrorSuccess
        elif self.status == self._kCGErrorIllegalArgument:
            return None
        return self.status

    def _getGamma(self) -> _kCGErrorSuccess:
        """
        Gets the coefficients of the gamma transfer formula for a display.
            .. Mac Catalyst 13.1+
            .. macOS 10.0+
            .. versionadded:: 0.0.2
        """
        self.status, *disp_trans = Quartz.CGGetDisplayTransferByFormula(
            self.display,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        if self.status == self._kCGErrorSuccess:
            return disp_trans
        if self.status == self._kCGErrorIllegalArgument:
            return None
        return self.status

    def _setGamma(self, red, blue, green) -> _kCGErrorSuccess:
        """
        Sets the gamma function for a display, by specifying the coefficients of the gamma transfer formula.
            ..Mac Catalyst 13.1+
            ..macOS 10.0+
            .. versionadded:: 0.0.3
        """
        if all(color == red for color in [blue, green]):
            return self._kCGErrorIllegalArgument
            # if all gamuts are equal, it means that the RGB gamma of the display will not change.

        self.status = Quartz.CGSetDisplayTransferByFormula(
            self.display,
            0.0, 1.0, red,
            0.0, 1.0, green,
            0.0, 1.0, blue
        )
        time.sleep(0.02)
        # make delay between executing function, it needs if function is called for a continuous times.
        if self.status == self._kCGErrorSuccess:
            return self._kCGErrorSuccess

        if self.status == self._kCGErrorRangeCheck:
            return None
        return self.status

    def _modeRetain(self) -> _kCGErrorSuccess:
        """Retains a Core Graphics display mode.
            Mac Catalyst 13.1+
            macOS 10.6+
         .. versionadded:: 0.0.4
        """

        display_modes = Quartz.CGDisplayCopyAllDisplayModes(self.display, None)

        for md in range(Quartz.CFArrayGetCount(display_modes)):
            cur_mode = Quartz.CFArrayGetValueAtIndex(display_modes, md)

            if Quartz.CGDisplayModeGetIOFlags(cur_mode) & self._kDisplayModeNativeFlag:
                io_port = Quartz.CGDisplayModeGetIOFlags(cur_mode)
                return Quartz.CGDisplayModeRetain(io_port)
            return None

    def _isDisplay(self, n) -> _kCGErrorSuccess:
        _listDisplay = Quartz.CGGetActiveDisplayList(30, None, None)
        return _listDisplay

    def _bestDisplayMode(self) -> _kCGErrorSuccess:
        """
        Returns information about the display mode closest to a specified depth, screen size, and refresh rate.
            Mac Catalyst 13.1-13.3
            ..versionadded:: 0.0.4
        """
        mode, self.status = Quartz.CGDisplayBestModeForParametersAndRefreshRate(
            Quartz.CGMainDisplayID(),
            0,
            Quartz.CGDisplayBitsPerPixel(Quartz.CGMainDisplayID()),
            *Quartz.CGDisplayBounds(Quartz.CGMainDisplayID()).size,
            None
        )
        if self.status == self._kCGErrorSuccess:
            return mode
        return self.status
