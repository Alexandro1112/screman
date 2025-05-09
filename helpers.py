import Quartz



def err_to_exception(err):
    query_exc = {
         0: '_kCGErrorSuccess',
         1000: '_kCGErrorFailure',
         1001: '_kCGErrorIllegalArgument',
         1011: '_kCGErrorNoneAvailable',
         1970170734: '_kDisplayVendorIDUnknown',
         1007: '_kCGErrorRangeCheck'


    }
    return query_exc.get(err, query_exc[0])



def getbounds(display):
    return Quartz.CGDisplayBounds(display).size

def createbounds(w, h):
    return Quartz.CGPoint(w, h)

