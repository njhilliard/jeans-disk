import numpy as np
import numpy.ctypeslib as npct
import ctypes

float_p = ctypes.POINTER(ctypes.c_float)

def tipsy_make_array(size, ndims=1, type=np.float32):
    if ndims == 1:
        return np.empty(size, dtype=type)
    if ndims == 2:
        return np.empty((size, 3), dtype=type)
    raise ValueError("tipsy only supports 1d and 2d arrays")

class tipsy_struct(ctypes.Structure):
    def __init__(self):
        self.is_simple = False

    def __str__(self):
        repr = []
        attrs = [k[0] for k in self._fields_] if self.is_simple else sorted(self.__dict__.keys())
        for k in attrs:
            if k == 'is_simple':
                continue
            a = getattr(self, k)
            repr.append('{0:10s}: {1:s}'.format(k, str(a.shape) if isinstance(a, np.ndarray) else str(a)))
        return '\n'.join(repr)

def tipsy_init_basic_particle(p, size):
    """For internal use only"""
    p.mass   = tipsy_make_array(size)
    p.mass_p = p.mass.ctypes.data_as(float_p)
    p.pos    = tipsy_make_array(size, ndims=2)
    p.pos_p  = p.pos.ctypes.data_as(float_p)
    p.vel    = tipsy_make_array(size, ndims=2)
    p.vel_p  = p.vel.ctypes.data_as(float_p)
    p.phi    = tipsy_make_array(size)
    p.phi_p  = p.phi.ctypes.data_as(float_p)
    p.soft   = 0.0
    p.size   = size

class tipsy_header(tipsy_struct):
    _fields_ = [
        ('time'   , ctypes.c_double),
        ('nbodies', ctypes.c_int),
        ('ndim'   , ctypes.c_int),
        ('ngas'   , ctypes.c_int),
        ('ndark'  , ctypes.c_int),
        ('nstar'  , ctypes.c_int)
    ]
    
    def __init__(self):
        self.is_simple = True

class tipsy_gas_data(tipsy_struct):
    _fields_ = [
        ('mass_p'   , float_p),
        ('pos_p'    , float_p),
        ('vel_p'    , float_p),
        ('rho_p'    , float_p),
        ('temp_p'   , float_p),
        ('metals_p' , float_p),
        ('hsmooth_p', float_p),
        ('phi_p'    , float_p),
        ('soft'     , ctypes.c_float),
        ('size'     , ctypes.c_size_t)
    ]
    
    def __init__(self, size):
        super().__init__()
        tipsy_init_basic_particles(self, size)
        
        self.rho        = tipsy_make_array(size)
        self.rho_p      = self.rho.ctypes.data_as(float_p)
        self.temp       = tipsy_make_array(size)
        self.temp_p     = self.temp.ctypes.data_as(float_p)
        self.metals     = tipsy_make_array(size)
        self.metals_p   = self.metals.ctypes.data_as(float_p)
        self.hsmooth    = tipsy_make_array(size)
        self.hsmooth_p  = self.hsmooth.ctypes.data_as(float_p)

class tipsy_dark_data(tipsy_struct):
    _fields_ = [
        ('mass_p', float_p),
        ('pos_p' , float_p),
        ('vel_p' , float_p),
        ('phi_p' , float_p),
        ('soft'  , ctypes.c_float),
        ('size'  , ctypes.c_size_t)
    ]

    def __init__(self, size):
        super().__init__()
        tipsy_init_basic_particle(self, size)

class tipsy_star_data(tipsy_struct):
    _fields_ = [
        ('mass_p'  , float_p),
        ('pos_p'   , float_p),
        ('vel_p'   , float_p),
        ('metals_p', float_p),
        ('tform_p' , float_p),
        ('phi_p'   , float_p),
        ('soft'    , ctypes.c_float),
        ('size'    , ctypes.c_size_t)
    ]
    
    def __init__(self, size):
        super().__init__()
        tipsy_init_basic_particle(self, size)
        self.metals     = tipsy_make_array(size)
        self.metals_p   = self.metals.ctypes.data_as(float_p)
        self.tform      = tipsy_make_array(size)
        self.tform_p    = self.tform.ctypes.data_as(float_p)

class tipsy_blackhole_data(tipsy_struct):
    _fields_ = [
        ('mass_p', float_p),
        ('pos_p' , float_p),
        ('vel_p' , float_p),
        ('phi_p' , float_p),
        ('soft'  , ctypes.c_float),
        ('size'  , ctypes.c_size_t)
    ]
    
    def __init__(self, size):
        super().__init__()
        tipsy_init_basic_particle(self, size)

def load_tipsy():
    """Load the tipsy module. For internal use only """
    if load_tipsy.is_loaded:
        return
    
    def decode_err(err):
        if err < 0:
            # Tipsy error
            raise IOError(lib.tipsy_strerror(err).decode('utf-8'))
        
        if err > 0:
            # system error
            raise IOError('{0:s}: {1:s}'.format(
                    lib.tipsy_get_last_system_error().decode('utf-8'),
                    lib.tipsy_strerror(err).decode('utf-8')
                ))
    
    lib = npct.load_library("libtipsy", "")
    
    array_1d_float = npct.ndpointer(dtype=np.float32, ndim=1, flags='CONTIGUOUS')
    array_2d_float = npct.ndpointer(dtype=np.float32, ndim=2, flags='CONTIGUOUS')
    
    # Force parameter type-checking and return-value error checking
    lib.tipsy_get_last_system_error.restype = ctypes.c_char_p
    lib.tipsy_get_last_system_error.argtypes = []
    
    lib.tipsy_strerror.restype = ctypes.c_char_p
    lib.tipsy_strerror.argtypes = [ctypes.c_int]
    
    lib.tipsy_open_file.restype = None
    lib.tipsy_open_file.argtypes = [ctypes.c_char_p]
    
    lib.tipsy_close_file.restype = None
    lib.tipsy_close_file.argtypes = []
    
    lib.tipsy_write_header.restype = decode_err
    lib.tipsy_write_header.argtypes = [ctypes.c_double, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    
    lib.tipsy_write_star_particles.restype = decode_err
    lib.tipsy_write_star_particles.argtypes = [array_1d_float, array_2d_float, array_2d_float,
                                               array_1d_float, array_1d_float, ctypes.c_float,
                                               ctypes.c_size_t]
    
    lib.tipsy_write_dark_particles.restype = decode_err
    lib.tipsy_write_dark_particles.argtypes = [array_1d_float, array_2d_float, array_2d_float,
                                               ctypes.c_float, ctypes.c_size_t]
    
    lib.tipsy_write_gas_particles.restype = decode_err
    lib.tipsy_write_gas_particles.argtypes = [array_1d_float, array_2d_float, array_2d_float,
                                              array_1d_float, array_1d_float, array_1d_float,
                                              array_1d_float, ctypes.c_size_t]
    
    lib.tipsy_write_blackhole_particles.restype = decode_err
    lib.tipsy_write_blackhole_particles.argtypes = [array_1d_float, array_2d_float, array_2d_float,
                                                    ctypes.c_float, ctypes.c_size_t]
    
    lib.tipsy_read_header.restype = decode_err
    lib.tipsy_read_header.argtypes = [ctypes.POINTER(tipsy_header)]
    
    lib.tipsy_read_star_particles.restype = decode_err
    lib.tipsy_read_star_particles.argtypes = [ctypes.POINTER(tipsy_star_data)]
    
    lib.tipsy_read_dark_particles.restype = decode_err
    lib.tipsy_read_dark_particles.argtypes = [ctypes.POINTER(tipsy_dark_data)]
    
    lib.tipsy_read_gas_particles.restype = decode_err
    lib.tipsy_read_gas_particles.argtypes = [ctypes.POINTER(tipsy_gas_data)]
    
    load_tipsy.is_loaded = True
    return lib
load_tipsy.is_loaded = False