import numpy as np
import h5py

class gadget_particle:
    def __init__(self, data, mass, header):
        self.positions = np.empty(data['Coordinates'].shape, data['Coordinates'].dtype)
        data['Coordinates'].read_direct(self.positions)
        
        self.velocities = np.empty(data['Velocities'].shape, data['Velocities'].dtype)
        data['Velocities'].read_direct(self.velocities)
        
        self.size = self.positions.shape[0]
        
        if (float(mass) <= 0.0):
            self.mass = np.empty(data['Masses'].shape, data['Masses'].dtype)
            data['Masses'].read_direct(self.mass)
        else:
            self.mass = float(mass) * np.ones(self.size, dtype=np.float32)
        
        self.potential = None
        if 'Potential' in data.keys():
             self.potential = np.empty(data['Potential'].shape, data['Potential'].dtype)
             data['Potential'].read_direct(self.potential)

class gadget_particle_with_metals(gadget_particle):
    def __init__(self, data, mass, header):
        super().__init__(data, mass, header)
        self.t_form = None
        if header['Flag_Sfr'] and header['Flag_StellarAge']:
            if 'StellarFormationTime' in data.keys():
                self.t_form = np.empty(data['StellarFormationTime'].shape, data['StellarFormationTime'].dtype)
                data['StellarFormationTime'].read_direct(self.t_form)
            else:
                print('Stellar evolution enabled, but StellarFormationTime is not present. Skipping...')
        
        self.metals = None
        if header['Flag_Sfr'] and header['Flag_Metals']:
            if 'Metallicity' in data.keys():
                self.metals = np.empty(data['Metallicity'].shape, data['Metallicity'].dtype)
                data['Metallicity'].read_direct(self.metals)
            else:
                print('Star formation and metals enabled, but no stellar metals found. Skipping...')

class gadget_gas_particle(gadget_particle_with_metals):
    def __init__(self, data, mass, header):
        super().__init__(data, mass, header)
        # If not using traditional SPH, then this is really
        #
        #    meanweight = 4.0 / (1 + 3 * HYDROGEN_MASSFRAC)
        #    All.MinEgySpec = 1 / meanweight * (1.0 / GAMMA_MINUS1) * (BOLTZMANN / PROTONMASS) * All.MinGasTemp
        #    All.MinEgySpec *= All.UnitMass_in_g / All.UnitEnergy_in_cgs
        #
        #    max(All.MinEgySpec,
        #        SphP[pindex].Entropy / GAMMA_MINUS1 * pow(SphP[pindex].d.Density * a3inv, GAMMA_MINUS1))
        #
        self.internal_energy = np.empty(data['InternalEnergy'].shape, data['InternalEnergy'].dtype)
        data['InternalEnergy'].read_direct(self.internal_energy)
        
        self.density = np.empty(data['Density'].shape, data['Density'].dtype)
        data['Density'].read_direct(self.density)
        
        self.hsml = np.empty(data['SmoothingLength'].shape, data['SmoothingLength'].dtype)
        data['SmoothingLength'].read_direct(self.hsml)

        
        self.electron_density = None
        if header['Flag_Cooling']:
            self.electron_density = np.empty(data['ElectronAbundance'].shape, data['ElectronAbundance'].dtype)
            data['ElectronAbundance'].read_direct(self.electron_density)
        
        self.sfr = None
        if header['Flag_Sfr']:
            self.sfr = np.empty(data['StarFormationRate'].shape, data['StarFormationRate'].dtype)
            data['StarFormationRate'].read_direct(self.sfr)

class File:
    def __init__(self, fname):
        with h5py.File(fname, 'r') as file:
            self.header = {}
            
            # copy.deepcopy was failing, so just do it manually
            for k, v in file['Header'].attrs.items():
                self.header[k] = v

            self.gas = None
            if file.__contains__('PartType0'):
                print('GADGET: Reading gas...')
                self.gas = gadget_gas_particle(file['PartType0'], self.header['MassTable'][()][0], self.header)

            self.halo = None
            if file.__contains__('PartType1'):
                print('GADGET: Reading halo...')
                self.halo = gadget_particle(file['PartType1'], self.header['MassTable'][()][1], self.header)
                
            self.disk = None
            if file.__contains__('PartType2'):
                print('GADGET: Reading disk...')
                self.disk = gadget_particle(file['PartType2'], self.header['MassTable'][()][2], self.header)
            
            self.bulge = None
            if file.__contains__('PartType3'):
                print('GADGET: Reading bulge...')
                self.bulge = gadget_particle_with_metals(file['PartType3'], self.header['MassTable'][()][3], self.header)
            
            self.stars = None
            if file.__contains__('PartType4'):
                print('GADGET: Reading star...')
                self.stars = gadget_particle_with_metals(file['PartType4'], self.header['MassTable'][()][4], self.header)

            self.boundary = None
            if file.__contains__('PartType5'):
                print('GADGET: Reading boundary...')
                self.boundary = gadget_particle(file['PartType5'], self.header['MassTable'][()][5], self.header)

class Parameter_file():
    def __init__(self, fname):
        self.data = {}
        with open(fname, 'r') as file:
            for line in file:
                line = line.strip()
                if line == '':
                    continue
                name, value, *_ = line.split()
                if '%' in name:
                    continue
                self.data[name] = value
    
    def __getitem__(self, key):
        return self.data[key]
    
    def items(self):
        return self.data.items()
