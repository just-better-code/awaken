from ctypes import Structure, c_int, c_uint

class LastInputInfo(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_int),
    ]

