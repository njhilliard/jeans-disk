import numpy as np
import numpy.ctypeslib as npct
import ctypes

class File():
    """Read or write a tipsy file using multiple streams of data."""
    def __init__(self, filename, mode='wb'):
        self.lib = load_tipsy()
        self.lib.tipsy_open_file(ctypes.c_char_p(bytes(filename, 'utf-8')),
                                 ctypes.c_char_p(bytes(mode, 'utf-8')))

    def close(self):
        self.lib.tipsy_close_file()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False  # always re-raise exceptions

    def write_header(self, time, ngas, ndark, nstar):
        self.lib.tipsy_write_header(time, ngas, ndark, nstar)
        
    def write_dark(self, mass, pos, vel, softening, mass_scale, vel_scale):
        self.lib.tipsy_write_dark_particles(mass, pos, vel, softening, mass_scale, vel_scale, mass.shape[0])
    
    def write_star(self, mass, pos, vel, metals, t_form, mass_scale, vel_scale, softening):
        self.lib.tipsy_write_star_particles(mass, pos, vel, metals, t_form, softening, mass_scale, vel_scale, mass.shape[0])
    
    def write_gas(self, mass, pos, vel, density, temperature, hsmooth, metals, mass_scale, vel_scale):
        self.lib.tipsy_write_gas_particles(mass, pos, vel, density, temperature, hsmooth, metals, mass_scale, vel_scale, mass.shape[0])
    
    def write_blackhole(self, mass, pos, vel, softening, mass_scale, vel_scale):
        self.lib.tipsy_write_blackhole_particles(mass, pos, vel, softening, mass_scale, vel_scale, mass.shape[0])

def load_tipsy():
    """Load the tipsy module. For internal use only """
    
    if self.is_loaded is not None:
        return
    
    array_1d_float = npct.ndpointer(dtype=np.float32, ndim=1, flags='CONTIGUOUS')
    array_2d_float = npct.ndpointer(dtype=np.float32, ndim=2, flags='CONTIGUOUS')
    
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
    lib.tipsy_write_header.argtypes = [ctypes.c_double, ctypes.c_int, ctypes.c_int,
                                       ctypes.c_int]
    
    lib.tipsy_write_star_particles.restype = decode_err
    lib.tipsy_write_star_particles.argtypes = [array_1d_float, array_2d_float, array_2d_float,
                                               array_1d_float, array_1d_float, ctypes.c_float,
                                               ctypes.c_float, ctypes.c_float, ctypes.c_size_t]
    
    lib.tipsy_write_dark_particles.restype = decode_err
    lib.tipsy_write_dark_particles.argtypes = [array_1d_float, array_2d_float, array_2d_float,
                                               ctypes.c_float, ctypes.c_float, ctypes.c_float,
                                               ctypes.c_size_t]
    
    lib.tipsy_write_gas_particles.restype = decode_err
    lib.tipsy_write_gas_particles.argtypes = [array_1d_float, array_2d_float, array_2d_float,
                                              array_1d_float, array_1d_float, array_1d_float,
                                              array_1d_float, ctypes.c_float, ctypes.c_float,
                                              ctypes.c_size_t]
    
    lib.tipsy_write_blackhole_particles.restype = decode_err
    lib.tipsy_write_blackhole_particles.argtypes = [array_1d_float, array_2d_float, array_2d_float,
                                                    ctypes.c_float, ctypes.c_float, ctypes.c_float,
                                                    ctypes.c_size_t]
    
    lib.tipsy_read_header.restype = decode_err
    lib.tipsy_read_header.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int),
                                      ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int) ]
    
    lib.tipsy_read_star_particles.restype = decode_err
    lib.tipsy_read_star_particles.argtypes = [array_1d_float, array_2d_float, array_2d_float,
                                              array_1d_float, array_1d_float, array_1d_float,
                                              ctypes.c_size_t]
    
    lib.tipsy_read_dark_particles.restype = decode_err
    lib.tipsy_read_dark_particles.argtypes = [array_1d_float, array_2d_float, array_2d_float,
                                              array_1d_float, ctypes.c_size_t]
    
    lib.tipsy_read_gas_particles.restype = decode_err
    lib.tipsy_read_gas_particles.argtypes = [array_1d_float, array_2d_float, array_2d_float,
                                             array_1d_float, array_1d_float, array_1d_float, 
                                             array_1d_float, array_1d_float, ctypes.c_size_t]
    
    lib.tipsy_read_black_holes.restype = decode_err
    lib.tipsy_read_black_holes.argtype = [array_1d_float, array_2d_float, array_2d_float,
                                          array_1d_float, ctypes.c_size_t]
    
    self.is_loaded = True
    return lib