import numpy as np
import h5py

class gadget_particles:
    def __init__(self, data, mass):
        self.positions = np.empty(data['Coordinates'].shape, data['Coordinates'].dtype)
        data['Coordinates'].read_direct(self.positions)
        
        self.velocities = np.empty(data['Velocities'].shape, data['Velocities'].dtype)
        data['Velocities'].read_direct(self.velocities)
        
        self.mass = mass
        
        if (self.mass <= 0):
            self.mass = np.empty(data['Masses'].shape, data['Masses'].dtype)
            data['Masses'].read_direct(self.mass)

class gadget_gas_particles(gadget_particles):
    def __init__(self, data, mass):
        super().__init__(self, data, mass)

        self.temperature = np.empty(data['Temperature'].shape, data['Temperature'].dtype)
        data['Temperature'].read_direct(self.temperature)
        
        self.density = np.empty(data['Density'].shape, data['Density'].dtype)
        data['Density'].read_direct(self.density)


class gadget_file:
    def __init__(self, fname):
        with h5py.File(fname, 'r') as file:
            self.header = file['Header']

            self.gas = None
            if file.__contains__('PartType0'):
                self.gas = gadget_gas_particles(file['PartType0'], header.attrs['MassTable'][()][0])

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
                self.star = gadget_particles(file['PartType4'], self.header.attrs['MassTable'][()][4])

            self.boundary = None
            if file.__contains__('PartType5'):
                self.boundary = gadget_particles(file['PartType5'], self.header.attrs['MassTable'][()][5])
