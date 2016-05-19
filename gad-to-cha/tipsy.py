import gadget
import astropy.units as apu
import astropy.constants as apc
import math
import struct

# Some useful astronomy constants in cgs units
constants = {
    'gravity'       : apc.G.cgs.value,
    'boltzmann'     : apc.k_B.cgs.value,
    'protonmass'    : apc.m_p.cgs.value,
    'sec_per_myr'   : apu.yr.to(apu.s) * 1e6,
    'gamma_minus1'  : (5.0 / 3.0) - 1.0,
    'h_massfrac'    : 0.76
}

def dark_particle(mass, pos, vel, softening):
    return struct.pack('fffffffff', mass,
                       pos[0], pos[1], pos[2],
                       vel[0], vel[1], vel[2],
                       softening, 0.0)

def star_particle(mass, pos, vel, metals, tform, softening):
    return struct.pack('fffffffffff', mass,
                       pos[0], pos[1], pos[2],
                       vel[0], vel[1], vel[2],
                       metals, tform,
                       softening, 0.0)

def gas_particle(mass, pos, vel, rho, temp, hsmooth, metals):
    return struct.pack('ffffffffffff', mass,
                       pos[0], pos[1], pos[2],
                       vel[0], vel[1], vel[2],
                       rho, temp, hsmooth,
                       metals, 0.0)

def header(time, nsph, ndark, nstar):
    total = nsph + ndark + nstar
    return struct.pack('diiiii', time, total, 3, nsph, ndark, nstar)

class gadget_converter():
    def __init__(self, gadget_params, gadget_file, mass_conversion_factor, convert_bh=False, preserve_bndry_softening=False):
        if not isinstance(gadget_file, gadget.File):
            raise ValueError("input file must be a gadget.File")
        
        if not isinstance(gadget_params, gadget.Parameter_file):
            raise ValueError("input file must be a gadget.Parameter_file")

        self.convert_bh = convert_bh
        self.preserve_bndry_softening = preserve_bndry_softening
        self.mass_conversion_factor = float(mass_conversion_factor)
        self.time = float(gadget_file.header['Time'])
        self.redshift = float(gadget_file.header['Redshift'])
        self.is_cosmological = int(gadget_params['ComovingIntegrationOn']) == 1
        
        self.halo = None
        if gadget_file.halo is not None:
            self.halo = gadget_file.halo
            self.halo.softening = float(gadget_params['SofteningHalo'])
        
        self.disk = None
        if gadget_file.disk is not None:
            self.disk = gadget_file.disk
            self.disk.softening = float(gadget_params['SofteningDisk'])
        
        self.bulge = None
        if gadget_file.bulge is not None:
            self.bulge = gadget_file.bulge
            self.bulge.softening = float(gadget_params['SofteningBulge'])
        
        self.star = None
        if gadget_file.star is not None:
            self.star = gadget_file.star
            self.star.softening = float(gadget_params['SofteningStars'])
        
        self.boundary = None
        if gadget_file.boundary is not None:
            self.boundary = gadget_file.boundary
            self.boundary.softening = float(gadget_params['SofteningBndry'])

        self.gas = None
        if gadget_file.gas is not None:
            self.gas = gadget_file.gas
            self.gas.softening = gadget_params['SofteningGas']
            self.gas.temperature = np.copy(gadget_file.gas.internal_energy)
            
            # Convert temperature to Kelvin
            mean_weight = (4.0 / 
                           (3 * constants['h_massfrac'] + 1 + 
                            4 * constants['h_massfrac'] * self.gas.electron_density
                           ) * constants['protonmass'])
            
            hubble = 1.0
            if int(gadget_params['ComovingIntegrationOn']) == 1:
                hubble = float(gadget_params['HubbleParam'])
                if hubble == 0.0:
                    hubble = 1.0
            
            # TODO: Check these units wrt the mass conversion between GADGET and ChaNGa
            units['Length_in_cm'] = float(gadget_params['UnitLength_in_cm']) / hubble
            units['Mass_in_g'] = float(gadget_params['UnitMass_in_g']) / hubble
            units['Velocity_in_cm_per_s'] = float(gadget_params['UnitVelocity_in_cm_per_s'])
            units['Time_in_s'] = units['Length_in_cm'] / units['Velocity_in_cm_per_s']
            units['Energy_in_cgs'] = units['Mass_in_g'] * units['Length_in_cm'] ** 2 / units['Time_in_s'] ** 2
            
            self.gas.temperature *= (mean_weight / constants['boltzmann'] * 
                                     constants['gamma_minus1'] * units['Energy_in_cgs'] / 
                                     units['Mass_in_g'])

    
    def save(self, filename):
        # Gadget units have an extra sqrt(a) in the internal velocities
        vscale = math.sqrt(1.0 + self.redshift)

        ngas, ndark, nstar = 0, 0, 0
        
        with open(filename, 'wb') as file:
            # just a placeholder
            file.write(header(self.time, ngas, ndark, nstar))
            
            if self.halo is not None:
                ndark += self.halo.size
                for i in range(self.halo.size):
                    file.write(dark_particle(self.halo.mass[i] * self.mass_conversion_factor,
                                             self.halo.positions[i, :],
                                             self.halo.velocities[i, :] * vscale,
                                             self.halo.softening))
            
            # In ChaNGa, cosmological simulations treat disk and bulge particles
            # as dark matter particles
            if self.is_cosmological:
                if self.disk is not None:
                    ndark += self.disk.size
                    for i in range(self.disk.size):
                        file.write(dark_particle(self.disk.mass[i] * self.mass_conversion_factor,
                                                 self.disk.positions[i, :],
                                                 self.disk.velocities[i, :] * vscale,
                                                 self.disk.softening))
                
                if self.bulge is not None:
                    ndark += self.bulge.size
                    for i in range(self.bulge.size):
                        file.write(dark_particle(self.bulge.mass[i] * self.mass_conversion_factor,
                                                 self.bulge.positions[i, :],
                                                 self.bulge.velocities[i, :] * vscale,
                                                 self.bulge.softening))
            else:
                if self.disk is not None:
                    nstar += self.disk.size
                    for i in range(self.disk.size):
                        file.write(star_particle(self.disk.mass[i] * self.mass_conversion_factor,
                                                 self.disk.positions[i, :],
                                                 self.disk.velocities[i, :] * vscale,
                                                 self.disk.metals[i],
                                                 self.disk.t_form[i],
                                                 self.disk.softening))
                
                if self.bulge is not None:
                    nstar += self.bulge.size
                    for i in range(self.bulge.size):
                        file.write(star_particle(self.bulge.mass[i] * self.mass_conversion_factor,
                                                 self.bulge.positions[i, :],
                                                 self.bulge.velocities[i, :] * vscale,
                                                 self.bulge.softening))
    
            if self.boundary is not None and not self.convert_bh:
                ndark += self.boundary.size
                eps = self.halo.softening
                if not self.preserve_bndry_softening:
                    eps = self.boundary.softening
                for i in range(self.boundary.size):
                    file.write(dark_particle(self.boundary.mass[i] * self.mass_conversion_factor,
                                             self.boundary.positions[i],
                                             self.boundary.velocities[i] * vscale,
                                             eps))
            
            if self.star is not None:
                for i in range(self.star):
                    nstar += self.star.size
                    file.write(star_particle(self.star.mass[i] * self.mass_conversion_factor,
                                             self.star.positions[i],
                                             self.star.velocities[i] * vscale,
                                             self.star.metals[i],
                                             self.star.t_form[i],
                                             self.star.softening))
            
            if self.boundary is not None and self.convert_bh:
                nstar += self.boundary.size
                file.write(star_particle(self.boundary.mass[i] * self.mass_conversion_factor,
                                         self.boundary.positions[i],
                                         self.boundary.velocities[i] * vscale,
                                         0.0,  # These are not stars in GADGET, so there is no metalicity
                                         -1.0,  # Negative tForm signals black hole to GASOLINE
                                         self.boundary.softening))
       
        # update the header
        with open(filename, 'r+b') as file:
            file.write(header(self.time, ngas, ndark, nstar))
