#!/bin/sh

# no gas
cp snap_000.hdf5 snap_000.hdf5.tmp
python3 fix_ics.py --nogas snap_000.hdf5.tmp
h5repack snap_000.hdf5.tmp Gadget3/nogas/nogas.hdf5
rm snap_000.hdf5.tmp

# gas + stars
cp snap_000.hdf5 snap_000.hdf5.tmp
python3 fix_ics.py snap_000.hdf5.tmp
h5repack snap_000.hdf5.tmp Gadget3/gas/gas.hdf5
rm snap_000.hdf5.tmp

# gas + sfr
cp snap_000.hdf5 snap_000.hdf5.tmp
python3 fix_ics.py --sfr snap_000.hdf5.tmp
h5repack snap_000.hdf5.tmp Gadget3/gas+sfr/gas+sfr.hdf5
rm snap_000.hdf5.tmp
