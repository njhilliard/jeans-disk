import gadget
import astropy.units as apu
import astropy.constants as apc
import math
import numpy as np
import tipsy_file

# Some useful astronomy constants in cgs units
constants = {
    'gravity'       : apc.G.cgs.value,
    'boltzmann'     : apc.k_B.cgs.value,
    'protonmass'    : apc.m_p.cgs.value,
    'sec_per_myr'   : apu.yr.to(apu.s) * 1e6,
    'gamma_minus1'  : (5.0 / 3.0) - 1.0,
    'h_massfrac'    : 0.76
}

class gadget_converter():
    def __init__(self, gadget_params, gadget_file, mass_conversion_factor, convert_bh=False, preserve_bndry_softening=False):
        if not isinstance(gadget_file, gadget.File):
            raise ValueError("input file must be a gadget.File")
        
        if not isinstance(gadget_params, gadget.Parameter_file):
            raise ValueError("input file must be a gadget.Parameter_file")

        self.convert_bh = convert_bh
        self.preserve_bndry_softening = preserve_bndry_softening
        self.mass_scale = float(mass_conversion_factor)
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
            print('Converting internal energy to temperature assuming a gamma=5/3 gas')
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
        ngas, ndark, nstar = 0, 0, 0
        
        with tipsy_file.streaming_writer(filename) as file:
            # Gadget units have an extra sqrt(a) in the internal velocities
            file.set_velocity_scale(math.sqrt(1.0 + self.redshift))
            
            file.set_mass_scale(self.mass_scale)
            
            # just a placeholder
            file.write_header(self.time, ngas, ndark, nstar)
            
            if self.halo is not None:
                ndark += self.halo.size
                file.write_dark(self.halo.mass, self.halo.positions,
                                self.halo.velocities, self.halo.softening)
                
            # In ChaNGa, cosmological simulations treat disk and bulge particles
            # as dark matter particles
            if self.is_cosmological:
                if self.disk is not None:
                    ndark += self.disk.size
                    file.write_dark(self.disk.mass, self.disk.positions,
                                    self.disk.velocities, self.disk.softening)
                
                if self.bulge is not None:
                    ndark += self.bulge.size
                    file.write_dark(self.bulge.mass, self.bulge.positions,
                                    self.bulge.velocities, self.bulge.softening)
            else:
                if self.disk is not None:
                    nstar += self.disk.size
                    file.write_star(self.disk.mass, self.disk.positions,
                                    self.disk.velocities, self.disk.metals,
                                    self.disk.t_form, self.disk.softening)
                
                if self.bulge is not None:
                    nstar += self.bulge.size
                    file.write_star(self.bulge.mass, self.bulge.positions,
                                    self.bulge.velocities, self.bulge.softening)
    
            # Convert boundary particles to dark matter particles
            if self.boundary is not None and not self.convert_bh:
                ndark += self.boundary.size
                eps = self.halo.softening
                if not self.preserve_bndry_softening:
                    eps = self.boundary.softening
                file.write_dark(self.boundary.mass, self.boundary.positions,
                                self.boundary.velocities, eps)

            if self.star is not None:
                nstar += self.star.size
                file.write_star(self.star.mass, self.star.positions,
                                self.star.velocities, self.star.metals,
                                self.star.t_form, self.star.softening)
            
            # Convert boundary particles to black holes
            if self.boundary is not None and self.convert_bh:
                nstar += self.boundary.size
                file.write_star(self.boundary.mass, self.boundary.positions,
                                self.boundary.velocities, self.boundary.softening)
       
        # update the header
        with tipsy_file.streaming_writer(filename, 'r+b') as file:
            file.write_header(self.time, ngas, ndark, nstar)
