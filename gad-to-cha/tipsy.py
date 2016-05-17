import gadget
import astropy.units as apu
import astropy.constants as apc
import math
import struct

# Some useful astronomy constants in cgs units
constants = {
    gravity         : apc.G.cgs.value,
    boltzmann       : apc.k_B.cgs.value,
    protonmass      : apc.m_p.cgs.value,
    sec_per_myr     : apu.yr.to(apu.s) * 1e6,
    gamma_minus1    : (5.0 / 3.0) - 1.0,
    h_massfrac      : 0.76
}

class File():
    def __init__(self):
        self.is_cosmological = False
        self.convert_bh = False
        self.gas = None
        self.halo = None
        self.disk = None
        self.bulge = None
        self.star = None
        self.boundary = None
        self.mass_conversion_factor = 1.0
        self.gadget_header = None
    
    def save(self, filename):
        # Gadget units have an extra sqrt(a) in the internal velocities
        vscale = math.sqrt(1.0 + float(gadget_file.header['Redshift']))

        ntotal, ngas, ndark, nstar = 0, 0, 0, 0
        
        # just a placeholder
        header = struct.pack('diiiii', float(gadget_header['Time']), 0, 3, 0, 0, 0)
        
        with open(filename, 'wb') as file:
            file.write(header)
            
        # update the header
        with open(filename, 'wb+') as file:
            file.write(header)
            

    def convert(self, gadget_params, gadget_file, mass_conversion_factor, convert_bh=False):
        if not isinstance(gadget_file, gadget.File):
            raise ValueError("input file must be a gadget.File")
        
        if not isinstance(gadget_params, gadget.Parameter_file):
            raise ValueError("input file must be a gadget.Parameter_file")
        
        self.set_units(gadget_params)
        self.halo = gadget_file.halo
        self.halo.softening = float(gadget_params['SofteningHalo'])
        self.disk = gadget_file.disk
        self.disk.softening = float(gadget_params['SofteningDisk'])
        self.bulge = gadget_file.bulge
        self.bulge.softening = float(gadget_params['SofteningBulge'])
        self.star = gadget_file.star
        self.star.softening = float(gadget_params['SofteningStars'])
        self.boundary = gadget_file.boundary
        self.boundary.softening = float(gadget_params['SofteningBndry'])
        self.mass_conversion_factor = mass_conversion_factor
        self.convert_bh = convert_bh
        self.gadget_header = gadget_file.header
        
        if gadget_file.gas is not None:
            self.gas = gadget_file.gas
            self.gas.softening = gadget_params['SofteningGas']
            self.gas.temperature = np.copy(gadget_file.gas.internal_energy)
            
            # Convert temperature to Kelvin
            mean_weight = (4.0 / 
                           (3 * constants['h_massfrac'] + 1 + 
                            4 * constants['h_massfrac'] * self.gas.electron_density
                           ) * constants['protonmass'])
            
            self.gas.temperature *= (mean_weight / constants['boltzmann'] * 
                                     constants['gamma_minus1'] * self.units['Energy_in_cgs'] / 
                                     self.units['Mass_in_g'])
        
        if float(gadget_file.header.attrs['Redshift']) > 0.0:
            self.is_cosmological = True

    def set_units(self, gadget_params):
        if not isinstance(gadget_params, gadget.Parameter_file):
            raise ValueError("parameter file is not a 'gadget.Parameter_file'")
    
        hubble = float(gadget_params['dHubble0'])
        if hubble == 0.0:
            hubble = 1.0
        
        self.units['Length_in_cm'] = float(gadget_params['UnitLength_in_cm']) / hubble
        self.units['Mass_in_g'] = float(gadget_params['UnitMass_in_g']) / hubble
        self.units['Velocity_in_cm_per_s'] = float(gadget_params['UnitVelocity_in_cm_per_s'])
        self.units['Time_in_s'] = self.units['Length_in_cm'] / self.units['Velocity_in_cm_per_s']
        self.units['Energy_in_cgs'] = self.units['Mass_in_g'] * self.units['Length_in_cm'] ** 2 / self.units['Time_in_s'] ** 2
