import gadget
import numpy as np
from tipsy_c import *

class File():
    """Read or write a tipsy file using multiple streams of data."""
    def __init__(self, filename, mode='rb'):
        self.lib = load_tipsy()
        self.lib.tipsy_open_file(ctypes.c_char_p(bytes(filename, 'utf-8')),
                                 ctypes.c_char_p(bytes(mode, 'utf-8')))
        
        self.hdr = None
        self.dark_particles = None
        self.star_particles = None
        self.gas_particles = None

    def close(self):
        self.lib.tipsy_close_file()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False  # always re-raise exceptions
    
    def _read_header(self):
        """For internal use only"""
        self.hdr = tipsy_header()
        self.lib.tipsy_read_header(ctypes.byref(self.hdr))
    
    @property
    def header(self):
        if self.hdr is None:
            _read_header()
        return self.hdr

    @property
    def darkmatter(self):
        if self.hdr is None:
            _read_header()
            
        if self.dark_particles is None:
            self.dark_particles = tipsy_dark_data(self.hdr.ndark)
            self.lib.tipsy_read_dark_particles(ctypes.byref(self.dark_particles))
        return self.dark_particles
        
    @property
    def stars(self):
        if self.hdr is None:
            _read_header()

        if self.star_particles is None:
            self.star_particles = tipsy_star_data(self.hdr.nstar)
            self.lib.tipsy_read_star_particles(ctypes.byref(self.star_particles))
        return self.star_particles

    @property
    def gas(self):
        if self.hdr is None:
            _read_header()
            
        if self.gas_particles is None:
            self.gas_particles = tipsy_gas_data(self.hdr.ngas)
            self.lib.tipsy_read_gas_particles(ctypes.byref(self.gas_particles))
        return self.gas_particles

class streaming_writer():
    def __init__(self, filename, mode='wb'):
        self.lib = load_tipsy()
        self.lib.tipsy_open_file(ctypes.c_char_p(bytes(filename, 'utf-8')),
                                 ctypes.c_char_p(bytes(mode, 'utf-8')))
    
    def header(self, time, ngas, ndark, nstars):
        self.lib.tipsy_write_header(time, ngas, ndark, nstars)

    def gas(self, mass, pos, vel, rho, temp, hsmooth, metals, phi, size):
        self.lib.tipsy_write_gas_particles(mass, pos, vel, rho, temp, hsmooth, metals, phi, size)
    
    def darkmatter(self, mass, pos, vel, phi, softening, size):
        softening = np.asscalar(np.array(softening, dtype=np.float32))
        self.lib.tipsy_write_dark_particles(mass, pos, vel, phi, softening, size)    
    
    def stars(self, mass, pos, vel, metals, tform, phi, softening, size, is_blackhole=False):
        softening = np.asscalar(np.array(softening, dtype=np.float32))
        self.lib.tipsy_write_star_particles(mass, pos, vel, metals, tform, phi, softening, size, is_blackhole)

    def close(self):
        self.lib.tipsy_close_file()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False  # always re-raise exceptions
