import numpy as np
import h5py

class gadget_particles:
    def __init__(self, data, mass, read_metals=False):
        self.positions = np.empty(data['Coordinates'].shape, data['Coordinates'].dtype)
        data['Coordinates'].read_direct(self.positions)
        
        self.velocities = np.empty(data['Velocities'].shape, data['Velocities'].dtype)
        data['Velocities'].read_direct(self.velocities)
        
        self.mass = mass        
        if (self.mass <= 0):
            self.mass = np.empty(data['Masses'].shape, data['Masses'].dtype)
            data['Masses'].read_direct(self.mass)

        self.metals = None       
        if read_metals:
            self.metals = np.empty(data['metals'].shape, data['metals'].dtype)
            data['metals'].read_direct(self.metals)

class gadget_gas_particles(gadget_particles):
    def __init__(self, data, header):
        super().__init__(self, data, header.attrs['MassTable'][()][0])

        self.internal_energy = np.empty(data['internal_energy'].shape, data['internal_energy'].dtype)
        data['internal_energy'].read_direct(self.internal_energy)
        
        self.density = np.empty(data['Density'].shape, data['Density'].dtype)
        data['Density'].read_direct(self.density)

        self.electron_density = 1.0
        self.hsml = 1.0
        if header.attrs['Flag_Cooling']:
            self.electron_density = np.empty(data['ElectronAbundance'].shape, data['ElectronAbundance'].dtype)
            data['ElectronAbundance'].read_direct(self.electron_density)
            
            self.hsml = np.empty(data['hsml'].shape, data['hsml'].dtype)
            data['hsml'].read_direct(self.hsml)
        
        self.t_form = None
        if header.attrs['Flag_StellarAge']:
            self.t_form = np.empty(data['t_form'].shape, data['t_form'].dtype)
            data['t_form'].read_direct(self.t_form)
        
        self.metals = None
        if header.attrs['Flag_Metals']:
            self.metals = np.empty(data['metals'].shape, data['metals'].dtype)
            data['metals'].read_direct(self.metals)

class File:
    def __init__(self, fname):
        with h5py.File(fname, 'r') as file:
            self.header = file['Header']

            self.gas = None
            if file.__contains__('PartType0'):
                self.gas = gadget_gas_particles(file['PartType0'], header)

            self.halo = None
            if file.__contains__('PartType1'):
                self.halo = gadget_particles(file['PartType1'], self.header.attrs['MassTable'][()][1])
                
            self.disk = None
            if file.__contains__('PartType2'):
                self.disk = gadget_particles(file['PartType2'], self.header.attrs['MassTable'][()][2])
            
            self.bulge = None
            if file.__contains__('PartType3'):
                self.bulge = gadget_particles(file['PartType3'], self.header.attrs['MassTable'][()][3])
            
            self.star = None
            if file.__contains__('PartType4'):
                self.star = gadget_particles(file['PartType4'], self.header.attrs['MassTable'][()][4],
                                             int(self.header.attrs['Flag_Metals']) > 0)

            self.boundary = None
            if file.__contains__('PartType5'):
                self.boundary = gadget_particles(file['PartType5'], self.header.attrs['MassTable'][()][5])

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
