from ctypes import Structure, c_int, c_ulong

class XScreenSaverInfo(Structure):
    _fields_ = [
        ('window', c_ulong),  # screen saver window
        ('state', c_int),  # off, on, disabled
        ('kind', c_int),  # blanked, internal, external
        ('since', c_ulong),  # milliseconds
        ('idle', c_ulong),  # milliseconds
        ('event_mask', c_ulong),
    ]  # events