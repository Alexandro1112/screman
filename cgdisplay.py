import time
from types import NoneType
import Quartz.CoreGraphics
import ctypes
import abc
import objc
from typing_extensions import Iterable, Dict, SupportsInt
from .mapping import c_keycode, keycode
from .types import kCGErrorTypes, QErrorNoneAvailable, DictionaryKeys, SelectedWindow
from string import ascii_lowercase, digits, punctuation
import subprocess
import re


class CGDisplayDelegate:
    """
            ...CGDisplayDelegate - Abstract base class for managing and interacting with display
           properties and behaviors on macOS using the Quartz framework.
           This class provides a structure for subclasses to implement various display-related functionalities, including
           cursor management, key presses, display mode settings, brightness adjustments, and more. The methods defined in this
           class are abstract and must be overridden in any subclass to provide specific implementations.

       Attributes:
           display (Quartz.CGMainDisplayID): Reference to the main display ID. If no display ID is provided during
                                               initialization, it defaults to the main display.
           status (kCGErrorTypes): Status variable for tracking errors related to display operations.

       Methods:
            _hideCursor(): Abstract method to hide the cursor on the display. Must be implemented in subclasses.

           _pressKey(key): Abstract method to simulate a key press on the display.
            Must be implemented in subclasses.

             _moveTo(x, y): Abstract method to move the cursor to specified coordinates on the display.
           Must be implemented in subclasses.

            _setDisplayMode(modeIndex): Abstract method to set the display mode based on the provided index.
           Must be implemented in subclasses.

             _setTransfer(): Abstract method to set the color transfer function for the display.
           Must be implemented in subclasses.

           _setPalette(): Abstract method to set the color palette for the display. Must be implemented in subclasses.

           _setRotation(angle): Abstract method to rotate the display by a specified angle.
            Must be implemented in subclasses.

           _defaultMode(): Abstract method to get the display default mode.
            Must be implemented in subclasses.

           _setDisplayBrightness(value): Abstract method to adjust the brightness of the display.
            Must be implemented in subclasses.

           _displayRotation(): Abstract method to retrieve the current rotation of the display.
           Must be implemented in subclasses.

           _vendorNumber(): Abstract method to retrieve the vendor number of the display.
           Must be implemented in subclasses.

           _setMirror(): Abstract method to enable or disable display mirroring.
           Must be implemented in subclasses.

           _getWindowsOnDisplay(index): Abstract method to retrieve windows currently displayed on the specified index.
            Must be implemented in subclasses.

           _getGamma(): Abstract method to get the current gamma settings of the display.
           Must be implemented in subclasses.

           _setGamma(red, blue, green): Abstract method to set the gamma values for red, blue, and green channels.
            Must be implemented in subclasses.

           _modeRetain(): Abstract method to retain the current mode settings of the display.
           Must be implemented in subclasses.

           _isDisplay(): Abstract method to check if an object is a valid display.
            Must be implemented in subclasses.

           _bestDisplayMode(): Abstract method to determine and return the best available display mode.
            Must be implemented in subclasses.

           _switchTrueTone(): Abstract method to enable or disable True Tone functionality on compatible displays.
            Must be implemented in subclasses.

           _displayProperties(): Abstract method to retrieve properties of the display,
           as supported display function. Must be implemented in subclasses.

       """
    def __init__(self, display: Quartz.CGMainDisplayID() = 0) -> None:
        self.display = display or Quartz.CGMainDisplayID()  # define main display reference in abc class.
        self._mp_display = None
        self.status: kCGErrorTypes = kCGErrorTypes(NoneType)

        if not self._isDisplay():
            msg = f'Display {self.display} is not a valid display ID.'
            raise IndexError(msg)


    def __abs__(self):
        raise NotImplementedError

    def _load(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _hideCursor(self):
        pass

    @abc.abstractmethod
    def _pressKey(self, key):
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
    def _getWindowsOnDisplay(self, index):
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
    def _isDisplay(self):
        pass

    @abc.abstractmethod
    def _bestDisplayMode(self):
        pass

    @abc.abstractmethod
    def _switchTrueTone(self):
        pass

    @abc.abstractmethod
    def _displayProperties(self):
        pass

    @abc.abstractmethod
    def _displayBrightnessDictionary(self):
        pass


class _DisplayCallbackDelegate(CGDisplayDelegate):

    """
        ... DisplayCallbackDelegate can interact with
            display setting between external and internal displays.
            Inherit from CGDisplayDelegate, class facilitates interaction with display settings.
            Don't run something function which can change system setting in infinite loops. It can crush your device.

    """

    _kCGErrorSuccess: kCGErrorTypes | SupportsInt = 0
    _kCGErrorFailure: kCGErrorTypes | SupportsInt = 1000
    _kCGErrorIllegalArgument: kCGErrorTypes | SupportsInt = 1001
    _kCGErrorNoneAvailable: kCGErrorTypes | SupportsInt= 1011
    _kDisplayVendorIDUnknown: kCGErrorTypes | SupportsInt = 1970170734  # defined in IOGraphicsTypes.h
    _kCGErrorRangeCheck: kCGErrorTypes | SupportsInt = 1007
    _kDisplayModeNativeFlag: kCGErrorTypes | SupportsInt = 33554432  # defined in IOGraphicsTypes.h

    def __int__(self):
        return self.display

    def __le__(self, other):
        return self.display <= 0

    def __lt__(self, other):
        return self.display >= 0

    def __is_exist(self):
        return self._isDisplay()

    def __repr__(self):
        return '<' + _DisplayCallbackDelegate.__name__.__repr__() + f' with display at {repr(self.display)} index>'

    def _displayProperties(self) -> Dict:
        disp_properties = {}
        _isLoadMp = self._load()
        if _isLoadMp:
            display = globals()['MPDisplay'].alloc().initWithCGSDisplayID_(self.display)
            for attrs in dir(display):
                if attrs.startswith('is') and not attrs.endswith('_'):
                    disp_properties[attrs] = eval(f'display.{attrs}()')
            return disp_properties

    def _load(self):
        objc.loadBundle(
            'MonitorPanel',
            bundle_path=objc.pathForFramework('/System/Library/PrivateFrameworks/MonitorPanel.framework'),
            module_globals=globals(),
        )
        objc.loadBundle(
            'CoreBrightness',
            bundle_path=objc.pathForFramework('/System/Library/PrivateFrameworks/CoreBrightness.framework'),
            module_globals=globals(),
        )

        return globals()

    def _pressKey(self, key: Iterable | str) -> _kCGErrorSuccess:
        """Synthesizes a low-level keyboard event on the local machine.
            ..Mac Catalyst 13.1–13.1
            * Deprecated
            ..versionadded: 0.0.7
            """
        key = key.capitalize()  # if key passed in lower register

        _hexKey = (keycode.get(key if key.startswith('kVK_ANSI') else 'kVK_ANSI_' + key, None)
            or c_keycode.get(key if key.startswith('kVK_') else 'kVK_' + key, None)
        )  # if passed name of key which isn't startswith from kVK_ANSI or kVK

        _virtualKey = Quartz.kCGKeyboardEventKeycode if (key.lower() in
                    ' '.join(ascii_lowercase + digits + punctuation).split()) else Quartz.kCGKeyboardEventKeyboardType

        if _hexKey:
            self.status = Quartz.CGPostKeyboardEvent(
                _virtualKey,
                _hexKey,
                True
            )
            if self.status == self._kCGErrorSuccess:
                return kCGErrorTypes(self._kCGErrorSuccess)
            return kCGErrorTypes(self.status)
        return kCGErrorTypes(self._kCGErrorIllegalArgument)

    def _getWindowsOnDisplay(self, index=None):
        """
        Generates and returns information about the selected windows in the current user session.
            ..Mac Catalyst 13.1+
            ..macOS 10.5+
            ..versionadded: 0.0.7
        """
        options = (Quartz.kCGWindowListOptionIncludingWindow & Quartz.kCGWindowListExcludeDesktopElements)
        self._openedWindows = Quartz.CGWindowListCopyWindowInfo(
            options, Quartz.kCGNullWindowID
        )
        if index is None:
            return self._openedWindows
        return SelectedWindow(self._openedWindows[index])

    def _hideCursor(self) -> _kCGErrorSuccess:
        """ Hides the mouse cursor, and increments the hide cursor count.
                Mac Catalyst 13.1+
                macOS 10.0+
            .. versionadded:: 0.0.1 """
        self.status = Quartz.CGDisplayHideCursor(self.display)
        time.sleep(0.05)
        # make delay between executing function, it needs if function is called for a continuous times.

        return kCGErrorTypes(self.status)

    def _moveTo(self, x, y) -> _kCGErrorSuccess:
        """ Moves the mouse cursor to a specified point
        relative to the display origin (the upper left corner of the display).
                Mac Catalyst 13.1+
                macOS 10.0+
            .. versionadded:: 0.0.1
            ..versionupdate:: 0.0.3
        """
        w, h = Quartz.CGDisplayBounds(self.display).size
        _globalPoint = Quartz.CGPointMake(x, y)

        if x >= w or y >= h:
            return self._kCGErrorIllegalArgument
        self.status = Quartz.CGDisplayMoveCursorToPoint(
            self.display,
            _globalPoint
        )
        if self.status == self._kCGErrorSuccess:
            return kCGErrorTypes(self._kCGErrorSuccess)
        return kCGErrorTypes(self.status)

    def _setDisplayMode(self, modeIndex) -> _kCGErrorSuccess:
        """ Switches a display to a different mode.
        In an update 0.0.3 I prefer use a MPDisplay for switches modes, because it sets the modes for a long time.
            .. versionadded:: 0.0.1
            .. versionupdate:: 0.0.3
            """
        _isLoadMp = self._load()
        if _isLoadMp:
            display = _isLoadMp['MPDisplay'].alloc().initWithCGSDisplayID_(self.display)
            modes = display.allModes()
            if modeIndex <= 0 or modeIndex > len(modes):
                return self._kCGErrorIllegalArgument

            _mode = modes[modeIndex]
            self.status = display.setMode_(_mode)

            if self.status == self._kCGErrorSuccess:
                return kCGErrorTypes(self._kCGErrorSuccess)
            return kCGErrorTypes(self.status)

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
            return kCGErrorTypes(self._kCGErrorSuccess)
        return kCGErrorTypes(self.status)

    def _setPalette(self) -> _kCGErrorSuccess:
        """Sets the palette for a display.
            .. versionadded:: 0.0.1
        """
        self.status = Quartz.CGDisplaySetPalette(
            self.display,
            None
        )

        if self.status == self._kCGErrorNoneAvailable or Quartz.CGDisplayCanSetPalette(self.display):
            msg = f'Sorry, {self._setPalette.__name__}(:_:) currently not supported by this OS version.'
            raise QErrorNoneAvailable(msg)

        elif self.status == self._kCGErrorSuccess:
            return kCGErrorTypes(self._kCGErrorSuccess)
        return kCGErrorTypes(self._kCGErrorNoneAvailable)

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
                    return kCGErrorTypes(self._kCGErrorSuccess)
                elif not angle % 90 == 0:
                    return kCGErrorTypes(self._kCGErrorIllegalArgument)
                return kCGErrorTypes(self.status)  # real unknown status
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
            return kCGErrorTypes(self._kCGErrorNoneAvailable)

    def _setDisplayBrightness(self, value) -> _kCGErrorSuccess:
        """regulating brightness of screen to value
            .. versionadded:: 0.0.1
        """
        _controller = Quartz.IKMonitorBrightnessController.alloc().init()
        try:
            self.status = _controller.setBrightnessOnAllDisplays_(value)
        except ValueError:
            return kCGErrorTypes(self._kCGErrorIllegalArgument)
        finally:
            return kCGErrorTypes(self._kCGErrorSuccess)

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
            return kCGErrorTypes(self._kDisplayVendorIDUnknown)
        return _v_number

    def _setMirror(self) -> _kCGErrorSuccess:
        """Changes the configuration of a mirroring set.
            .. Mac Catalyst 13.1+
            .. macOS 10.2+
            .. versionadded:: 0.0.1 """
        err, config = Quartz.CGBeginDisplayConfiguration(None)
        if err == self._kCGErrorSuccess:
            Quartz.CGConfigureDisplayMirrorOfDisplay(config, self.display, Quartz.kCGNullDirectDisplay)

            options = (Quartz.kCGConfigureForSession & Quartz.kCGConfigureForAppOnly)

            self.status = Quartz.CGCompleteDisplayConfiguration(config, options)
            if self.status == self._kCGErrorSuccess:
                return kCGErrorTypes(self._kCGErrorSuccess)
            elif self.status == self._kCGErrorIllegalArgument:
                return None
            return kCGErrorTypes(self.status)
        return None

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
        return kCGErrorTypes(self.status)

    def _setGamma(self, red, blue, green) -> _kCGErrorSuccess:
        """
        Sets the gamma function for a display, by specifying the coefficients of the gamma transfer formula.
            ..Mac Catalyst 13.1+
            ..macOS 10.0+
            .. versionadded:: 0.0.3
        """
        if red == blue == green:
            return kCGErrorTypes(self._kCGErrorIllegalArgument)
            # if all gamuts are equal, it means that the RGB gamma of the display will not change.

        self.status = Quartz.CGSetDisplayTransferByFormula(
            self.display,
            0.1, 1.0, red,
            0.1, 1.0, green,
            0.1, 1.0, blue
        )
        time.sleep(0.02)
        # make delay between executing function, it needs if function is called for a continuous times.
        if self.status == self._kCGErrorSuccess:
            return kCGErrorTypes(self._kCGErrorSuccess)

        if self.status == self._kCGErrorRangeCheck:
            return None
        return kCGErrorTypes(self.status)

    def _modeRetain(self) -> _kCGErrorSuccess:
        """Retains a Core Graphics display mode.
            Mac Catalyst 13.1+
            macOS 10.6+
         .. versionadded:: 0.0.4
        """

        display_modes = Quartz.CGDisplayCopyAllDisplayModes(self.display, None)

        for modes in range(Quartz.CFArrayGetCount(display_modes)):
            cur_mode = Quartz.CFArrayGetValueAtIndex(display_modes, modes)

            if Quartz.CGDisplayModeGetIOFlags(cur_mode) & self._kDisplayModeNativeFlag:
                io_port = Quartz.CGDisplayModeGetIOFlags(cur_mode)
                return Quartz.CGDisplayModeRetain(io_port)
            return None

    def _isDisplay(self) -> _kCGErrorSuccess:
        _, _listDisplays, _ = Quartz.CGGetActiveDisplayList(30, None, None)
        return self.display in _listDisplays

    def _bestDisplayMode(self) -> _kCGErrorSuccess:
        """
        Returns information about the display mode closest to a specified depth, screen size, and refresh rate.
            Mac Catalyst 13.1-13.3
            ..versionadded:: 0.0.4
        """
        mode, self.status = Quartz.CGDisplayBestModeForParametersAndRefreshRate(
            Quartz.CGMainDisplayID(),
            Quartz.CGDisplayBitsPerPixel(self.display),
            *Quartz.CGDisplayBounds(self.display).size,
            0,
            None
        )
        if self.status == 1:
            return mode
        return kCGErrorTypes(self.status)

    def _switchTrueTone(self)-> _kCGErrorSuccess:
        """
        switch display TrueTone mode to other status.
        ..versionadded:: 0.0.5
        """
        _isLoadCb = self._load()
        if _isLoadCb:
            client = _isLoadCb['CBTrueToneClient'].alloc().init()
            old_status = client.enabled()
            if client.available() and client.supported():
                self.status = client.setEnabled_((not client.enabled()))
                new_status = client.enabled()
                if new_status != old_status:
                    return kCGErrorTypes(self._kCGErrorSuccess)

    def _displayBrightnessDictionary(self):
        """Return dictionary about brightness and colors settings of display.
        ..versionadded:: 0.0.7"""
        runner = subprocess.Popen(
            ['/usr/libexec/corebrightnessdiag', 'status-info'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )
        xml, err = runner.communicate()
        dictionary = {}
        if not err:
            keys = re.findall(r'<key>.*</key>', xml.decode('utf-8'))
            for tags in keys:
                keys = tags.replace('<key>', '').replace('</key>', '')
                result = subprocess.getoutput(f'/usr/libexec/corebrightnessdiag status-info | grep "{keys}"').split('\n')

                for line in result:
                    lines = line.strip().split()
                    if len(lines) >= 3:  # if block contain "key = value"
                        strings = ' '.join(lines).split()

                        if len(strings) > 2:
                            if (digits not in strings[0]) and (punctuation not in strings[2]) and not (strings[0].startswith('<')):
                                dictionary[strings[0]] = re.sub(r'([^\w])', '', strings[2])
            for i in range(6):
                del dictionary[str(i)]

            return DictionaryKeys(dictionary)
        raise NotImplementedError('command /usr/libexec/corebrightnessdiag not supporting on current device.')
