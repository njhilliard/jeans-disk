import numpy as np
import os
from snap_tools.snapshot import Snapshot
import h5py
"""
This file contains the Snapshot classes
These inherit modules from their superclass SnapshotMethods
Next two classes are for particular filetypes
"""


class SnapHDF5(Snapshot):
    """
    Snapshots in HDF5
    snap = SnapHDF5('mycoolsnapshot.hdf5')
    Note: Must have matching header and data.
    Todo: Gracefully handle mismatches between header and data
    """
    def __init__(self, fname):
        # Convienent names for header attributes
        # Add more here if you need more.
        # Will use the name in the HDF5 file if not specified
        head_attrs = {'NumPart_ThisFile': 'npart',
                      'NumPart_Total': 'nall',
                      'NumPart_Total_HighWord': 'nall_highword',
                      'MassTable': 'massarr',
                      'Time': 'time',
                      'Redshift': 'redshift',
                      'BoxSize': 'boxsize',
                      'NumFilesPerSnapshot': 'filenum',
                      'Omega0': 'omega0',
                      'OmegaLambda': 'omega_l',
                      'HubbleParam': 'hubble',
                      'Flag_Sfr': 'sfr',
                      'Flag_Cooling': 'cooling',
                      'Flag_StellarAge': 'stellar_age',
                      'Flag_Metals': 'metals',
                      'Flag_Feedback': 'feedback',
                      'Flag_DoublePrecision': 'double'}
        # Defines convienent standard names for misc. data blocks
        # Todo: add function for arbitrary datablocks
        misc_datablocks = {"InternalEnergy": "U   ",
                           "Density": "RHO ",
                           "Volume": "VOL ",
                           "Center-of-Mass": "CMCE",
                           "Surface Area": "AREA",
                           "Number of faces of cell": "NFAC",
                           "ElectronAbundance": "NE  ",
                           "NeutralHydrogenAbundance": "NH  ",
                           "SmoothingLength": "HSML",
                           "StarFormationRate": "SFR ",
                           "StellarFormationTime": "AGE ",
                           "Metallicity": "Z   ",
                           "Acceleration": "ACCE",
                           "VertexVelocity": "VEVE",
                           "MaxFaceAngle": "FACA",
                           "CoolingRate": "COOR",
                           "MachNumber": "MACH",
                           "DM Hsml": "DMHS",
                           "DM Density": "DMDE",
                           "PSum": "PTSU",
                           "DMNumNgb": "DMNB",
                           "NumTotalScatter": "NTSC",
                           "SIDMHsml": "SHSM",
                           "SIDMRho": "SRHO",
                           "SVelDisp": "SVEL",
                           "GFM StellarFormationTime": "GAGE",
                           "GFM InitialMass": "GIMA",
                           "GFM Metallicity": "GZ  ",
                           "GFM Metals": "GMET",
                           "GFM MetalsReleased": "GMRE",
                           "GFM MetalMassReleased": "GMAR"}

        with h5py.File(fname, 'r') as s:
            self.header = {}
            #header_keys = s['Header'].attrs.keys()
            for head_key, head_val in s['Header'].attrs.iteritems():
                if head_key in head_attrs.keys():
                    self.header[head_attrs[head_key]] = head_val
                else:
                    self.header[head_key] = head_val

            part_names = ['gas',
                          'halo',
                          'stars',
                          'bulge',
                          'sfr',
                          'other']
            self.pos = {}
            self.vel = {}
            self.ids = {}
            self.masses = {}
            self.pot = {}
            self.misc = {}
            for i, n in enumerate(self.header['npart']):
                if n > 0:
                    group = 'PartType%s' % i
                    part_name = part_names[i]
                    for key in s[group].keys():
                        if key == 'Coordinates':
                            self.pos[part_name] = s[group]['Coordinates'][()]
                        elif key == 'Velocities':
                            self.vel[part_name] = s[group]['Velocities'][()]
                        elif key == 'ParticleIDs':
                            self.ids[part_name] = s[group]['ParticleIDs'][()]
                        elif key == 'Potential':
                            self.pot[part_name] = s[group]['Potential'][()]
                        elif key == 'Masses':
                            self.masses[part_name] = s[group]['Masses'][()]
                        # If we find a misc. key then add it to the misc variable (a dict)
                        elif key in misc_datablocks.keys():
                            if part_name not in self.misc.keys():
                                self.misc[part_name] = {}
                            self.misc[part_name][misc_datablocks[key]] = s[group][key][()]
                        # We have an unidentified key, throw it in with the misc. keys
                        else:
                            if part_name not in self.misc.keys():
                                self.misc[part_name] = {}
                            self.misc[part_name][key] = s[group][key][()]
                    # If we never found the masses key then make one
                    if part_name not in self.masses.keys():
                        self.masses[part_name] = (np.ones(n)*
                                                  self.header['massarr'][i])

class SnapBinary(Snapshot):
    def __init__(self, fname):
        f = open(fname, 'rb')
        blocksize = np.fromfile(f, dtype=np.int32, count=1)
        if blocksize[0] == 8:
            swap = 0
            format = 2
        elif blocksize[0] == 256:
            swap = 0
            format = 1
        else:
            blocksize.byteswap(True)
            if blocksize[0] == 8:
                swap = 1
                format = 2
            elif blocksize[0] == 256:
                swap = 1
                format = 1
            else:
                print "incorrect file format encountered when " +\
                      "reading header of", fname
        self.header = {}
        if format == 2:
            f.seek(16, os.SEEK_CUR)
        part_names = ['gas',
                      'halo',
                      'stars',
                      'bulge',
                      'sfr',
                      'other']
        npart = np.fromfile(f, dtype=np.int32,
                            count=6)
        self.header['npart'] = npart
        massarr = np.fromfile(f, dtype=np.float64,
                              count=6)
        self.header['massarr'] = massarr
        self.header['time'] = (np.fromfile(f, dtype=np.float64,
                                           count=1))[0]
        self.header['redshift'] = (np.fromfile(f, dtype=np.float64,
                                               count=1))[0]
        self.header['sfr'] = (np.fromfile(f, dtype=np.int32,
                                          count=1))[0]
        self.header['feedback'] = (np.fromfile(f, dtype=np.int32,
                                               count=1))[0]
        nall = np.fromfile(f, dtype=np.int32,
                           count=6)
        self.header['nall'] = nall
        self.header['cooling'] = (np.fromfile(f, dtype=np.int32,
                                              count=1))[0]
        self.header['filenum'] = (np.fromfile(f, dtype=np.int32,
                                              count=1))[0]
        self.header['boxsize'] = (np.fromfile(f, dtype=np.float64,
                                              count=1))[0]
        self.header['omega0'] = (np.fromfile(f, dtype=np.float64,
                                              count=1))[0]
        self.header['omega_l'] = (np.fromfile(f, dtype=np.float64,
                                              count=1))[0]
        self.header['hubble'] = (np.fromfile(f, dtype=np.float64,
                                             count=1))[0]
        self.header['double'] = 0
        if swap:
            self.header['npart'].byteswap(True)
            self.header['massarr'].byteswap(True)
            self.header['time'] = self.time.byteswap()
            self.header['redshift'] = self.redshift.byteswap()
            self.header['sfr'] = self.sfr.byteswap()
            self.header['feedback'] = self.feedback.byteswap()
            self.header['nall'].byteswap(True)
            self.header['cooling'] = self.cooling.byteswap()
            self.header['filenum'] = self.filenum.byteswap()
            self.header['boxsize'] = self.boxsize.byteswap()
            self.header['omega0'] = self.omega_m.byteswap()
            self.header['omega_l'] = self.omega_l.byteswap()
            self.header['hubble'] = self.hubble.byteswap()
        np.fromfile(f, dtype=np.int32, count=1)
        np.fromfile(f, dtype=np.int32, count=25)
        NPARTS = np.sum(self.header['npart'])
        self.pos = {}
        positions = np.fromfile(f, dtype=np.float32,
                                count=NPARTS*3).reshape(NPARTS, 3)
        NGAS = self.header['npart'][0]
        if NGAS:
            self.pos['gas'] = positions[0:NGAS, :]
        NHALO = self.header['npart'][1]
        if NHALO:
            self.pos['halo'] = positions[NGAS:NGAS+NHALO, :]
        NSTARS = self.header['npart'][2]
        if NSTARS:
            self.pos['stars'] = positions[NGAS+NHALO:NGAS+NHALO+NSTARS, :]
        self.vel = {}
        np.fromfile(f, dtype=np.int32, count=2)
        velocities = np.fromfile(f, dtype=np.float32,
                                 count=NPARTS*3).reshape(NPARTS, 3)
        if NGAS:
            self.vel['gas'] = velocities[0:NGAS, :]
        if NHALO:
            self.vel['halo'] = velocities[NGAS:NGAS+NHALO, :]
        if NSTARS:
            self.vel['stars'] = velocities[NGAS+NHALO:NGAS+NHALO+NSTARS, :]
        self.ids = {}
        np.fromfile(f, dtype=np.int32, count=2)
        ids = np.fromfile(f, dtype=np.int32,
                          count=NPARTS)
        if NGAS:
            self.ids['gas'] = ids[0:NGAS]
        if NHALO:
            self.ids['halo'] = ids[NGAS:NGAS+NHALO]
        if NSTARS:
            self.ids['stars'] = ids[NGAS+NHALO:NGAS+NHALO+NSTARS]
        self.pot = {}
        self.masses = {}
        self.misc = {}

        np.fromfile(f, dtype=np.int32, count=2)

        #if massarr[parttype] > 0:
        #    np.ones(nall[parttype], dtype=np.float)*massarr[parttype]

        if not any(massarr):
            masses = np.fromfile(f, dtype=np.float32,
                                 count=NPARTS)
            np.fromfile(f, dtype=np.int32, count=2)
            potentials = np.fromfile(f, dtype=np.float32,
                                     count=NPARTS)
        else:
            potentials = np.fromfile(f, dtype=np.float32,
                                     count=NPARTS)

        if NGAS:
            if massarr[0] != 0:
                self.masses['gas'] = np.zeros(NGAS) + \
                    self.header['massarr'][0]
                self.pot['gas'] = potentials[0:NGAS]
            else:
                self.masses['gas'] = masses[0:NGAS]
                self.pot['gas'] = potentials[0:NGAS]

        if NHALO:
            if massarr[1] != 0:
                self.masses['halo'] = np.zeros(NHALO) + \
                    self.header['massarr'][1]
                self.pot['halo'] = potentials[NGAS:NGAS+NHALO]
            else:
                self.masses['halo'] = masses[NGAS:NGAS+NHALO]
                self.pot['halo'] = potentials[NGAS:NGAS+NHALO]

        if NSTARS:
            if massarr[2] != 0:
                self.masses['stars'] = np.zeros(NSTARS) + \
                    self.header['massarr'][2]
                self.pot['stars'] = potentials[NGAS+NHALO:NGAS+NHALO+NSTARS]
            else:
                self.masses['stars'] = masses[NGAS+NHALO:NGAS+NHALO+NSTARS]
                self.pot['stars'] = potentials[NGAS+NHALO:NGAS+NHALO+NSTARS]
        f.close()
