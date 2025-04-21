import re
import time
import Quartz
import dispatch



class CGDisplayStreamDelegate:
    def __init__(self,
                 display,
                 pixel_format,
                 bounds,
                 delay,
                 **kwargs,
                 ):
        self.display = display
        self.delay = delay
        self.bounds = bounds
        self.pixel_format = pixel_format
        self.kwargs = kwargs

        _pixelFormats = (b'420f', b'l10r', b'BGR', b'420v')
        _, displays, _ = Quartz.CGGetActiveDisplayList(32, None, None)

        if display not in displays:
            msg = f'Display with index {display} does not found.'
            raise IndexError(msg)

        if pixel_format not in _pixelFormats:
            msg = f'Pixel format {pixel_format} is not supported.'
            raise ValueError(msg)


    def run(self, filename):
        def handler(status, ids, io_surface, updates):
            if status == 0:
                image = Quartz.CIImage.alloc().initWithIOSurface_(io_surface)
                bitmap = Quartz.NSBitmapImageRep.alloc().initWithCIImage_(image)
                represented = bitmap.representationUsingType_properties_(Quartz.NSBitmapImageFileTypeJPEG, None)
                represented.writeToFile_atomically_(
                    Quartz.NSString.stringWithString_(filename), True
                )

        extn = re.findall(r'.jpeg|.bmp|.png|.gif|.tiff', filename, flags=re.DOTALL)
        if not extn:
            msg = f'No extension found for {filename}.'
            raise ValueError(msg)

        queue = dispatch.dispatch_get_global_queue(dispatch.DISPATCH_QUEUE_PRIORITY_HIGH, 0)

        stream = Quartz.CGDisplayStreamCreateWithDispatchQueue(
            self.display,
            *self.bounds,
            int.from_bytes(self.pixel_format),
            self.kwargs,
            (queue or None),
            handler
        )

        Quartz.CGDisplayStreamStart(stream)

        while True:
            time.sleep(1)
            break






