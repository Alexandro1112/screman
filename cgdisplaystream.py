import re
import time
import Quartz.CoreGraphics
import dispatch
from .types import kCGErrorTypes
from typing_extensions import SupportsInt
from IOSurface import IOSurfaceRef


class DisplayStreamDelegate:
    """.
        ...CGDisplayStreamDelegate class is designed to facilitate the capture of images from a specified display
     on macOS using the Core Graphics framework. This class manages the configuration and operation of a
      display stream that captures frames from a given display and saves them as image files.
      """
    _kCGErrorSuccess: kCGErrorTypes | SupportsInt = 0
    _kCGErrorIllegalArgument: kCGErrorTypes | SupportsInt = 1001

    def __init__(self, display, pixel_format, bounds, **kwargs):
        self.display = display
        self.bounds = bounds
        self.pixel_format = pixel_format
        self.properties =  {
            Quartz.kCGDisplayStreamMinimumFrameTime: int(kwargs['minimumFrameTime']),
            Quartz.kCGDisplayStreamShowCursor: bool(kwargs['showCursor']),
        }

        _pixelFormats = (b'420f', b'l10r', b'BGR', b'420v')
        _, displays, _ = Quartz.CGGetActiveDisplayList(30, None, None)

        if display not in displays:
            msg = f'Display with index {display} does not found, code: {kCGErrorTypes(self._kCGErrorIllegalArgument).err()}'
            raise IndexError(msg)

        if pixel_format not in _pixelFormats:
            msg = f'Pixel format {pixel_format} is not supported, code: {kCGErrorTypes(self._kCGErrorIllegalArgument).err()}'
            raise ValueError(msg)


    def run(self, filename):
        """Running capturing image from display at specified display direct ID.
            ..versionadded:: 0.0.7"""

        def handler(status: Quartz.CGDisplayStreamFrameStatus,
                    display_time, io_surface: IOSurfaceRef, updates):
            if status == self._kCGErrorSuccess:

                image = Quartz.CIImage.alloc().initWithIOSurface_(io_surface)
                bitmap = Quartz.NSBitmapImageRep.alloc().initWithCIImage_(image)
                represented = bitmap.representationUsingType_properties_(Quartz.NSBitmapImageFileTypeJPEG, None)
                represented.writeToFile_atomically_(
                    Quartz.NSString.stringWithString_(filename), True)
            return None

        extn = re.findall(r'.jpeg|.bmp|.png|.gif|.tiff', filename, flags=re.DOTALL)
        if not extn:
            msg = f'No extension found for {filename}, code: {self._kCGErrorIllegalArgument}'
            raise ValueError(msg)

        queue = dispatch.dispatch_get_global_queue(dispatch.DISPATCH_QUEUE_PRIORITY_HIGH, 0)

        stream = Quartz.CGDisplayStreamCreateWithDispatchQueue(
            self.display,
            *self.bounds,
            int.from_bytes(self.pixel_format, byteorder='big'),
            self.properties,
            queue,
            handler
        )

        Quartz.CGDisplayStreamStart(stream)

        while True:
            time.sleep(1)
            break









