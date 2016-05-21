import numpy as np
import numpy.ctypeslib as npct
import ctypes

class streaming_writer():
    """Write a tipsy file from multiple streams of data.
       This is essentially a conversion from SoA to AoS.
     """
    def __init__(self, filename, mode='wb'):
        self.lib = load_tipsy()
        self.lib.tipsy_open_file(ctypes.c_char_p(bytes(filename, 'utf-8')),
                                 ctypes.c_char_p(bytes(mode, 'utf-8')))

    def set_velocity_scale(self, vs):
        self.lib.tipsy_set_velocity_scale(float(vs))

    def set_mass_scale(self, ms):
        self.lib.tipsy_set_mass_scale(float(ms))

    def close(self):
        self.lib.tipsy_close_file()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def write_header(self, time, ngas, ndark, nstar):
        self.lib.tipsy_write_header(time, ngas, ndark, nstar)
        
    def write_dark(self, mass, pos, vel, softening):
        self.lib.tipsy_write_dark_particles(mass, pos, vel, softening, mass.shape[0])
    
    def write_star(self, mass, pos, vel, metals, t_form, softening):
        self.lib.tipsy_write_star_particles(mass, pos, vel, metals, t_form, softening, mass.shape[0])
    
    def write_gas(self, mass, pos, vel, density, temperature, hsmooth, metals):
        self.lib.tipsy_write_gas_particles(mass, pos, vel, density, temperature, hsmooth, metals, mass.shape[0])
    
    def write_blackhole(self, mass, pos, vel, softening):
        self.lib.tipsy_write_blackhole_particles(mass, pos, vel, softening, mass.shape[0])

def load_tipsy():
    """Load the tipsy module. For internal use only """
    array_1d_float = npct.ndpointer(dtype=np.float32, ndim=1, flags='CONTIGUOUS')
    array_2d_float = npct.ndpointer(dtype=np.float32, ndim=2, flags='CONTIGUOUS')
    
    lib = npct.load_library("libtipsy", "")
    
    # Force parameter type-checking
    lib.tipsy_open_file.restype = None
    lib.tipsy_open_file.argtypes = [ctypes.c_char_p]
    
    lib.tipsy_close_file.restype = None
    lib.tipsy_close_file.argtypes = []
    
    lib.tipsy_set_velocity_scale.restypes = None
    lib.tipsy_set_velocity_scale.argtypes = [ctypes.c_float]
    
    lib.tipsy_set_mass_scale.restype = None
    lib.tipsy_set_mass_scale.argtypes = [ctypes.c_float]
    
    lib.tipsy_write_header.restype = ctypes.c_int
    lib.tipsy_write_header.argtypes = [ctypes.c_double, ctypes.c_int, ctypes.c_int,
                                       ctypes.c_int]
    
    lib.tipsy_write_star_particles.restype = ctypes.c_int
    lib.tipsy_write_star_particles.argtypes = [array_1d_float, array_2d_float, array_2d_float,
                                               array_1d_float, array_1d_float, ctypes.c_float,
                                               ctypes.c_size_t]
    
    lib.tipsy_write_dark_particles.restype = ctypes.c_int
    lib.tipsy_write_dark_particles.argtypes = [array_1d_float, array_2d_float, array_2d_float,
                                               ctypes.c_float, ctypes.c_size_t]
    
    lib.tipsy_write_gas_particles.restype = ctypes.c_int
    lib.tipsy_write_gas_particles.argtypes = [array_1d_float, array_2d_float, array_2d_float,
                                              array_1d_float, array_1d_float, array_1d_float,
                                              array_1d_float, ctypes.c_size_t]
    
    lib.tipsy_write_blackhole_particles.restype = ctypes.c_int
    lib.tipsy_write_blackhole_particles.argtypes = [array_1d_float, array_2d_float, array_2d_float,
                                                    ctypes.c_float, ctypes.c_size_t]
    
    return lib