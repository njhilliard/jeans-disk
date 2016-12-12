# g2c


### Convert GADGET2 data and parameter files to ChaNGa (tipsy) files
---

	usage: gadget2changa.py [-h] [--convert-bh] [--preserve-boundary-softening]
	                        [--no-param-list] [--generations GENERATIONS]
	                        [--viscosity]
	                        GADGET Parameter out_dir
	
	Convert GADGET2 files to ChaNGa files
	
	positional arguments:
	  GADGET                GADGET2 HDF5 file to convert
	  Parameter             GADGET2 parameter file to convert
	  out_dir               Location of output
	
	optional arguments:
	  -h, --help            show this help message and exit
	  
	  --convert-bh          Treat boundary particles as black holes
	  
	  --preserve-boundary-softening
	                        Preserve softening lengths for boundary particles
	                        
	  --no-param-list       Do not store a complete list ChaNGa parameters in
	                        "param_file"
	                        
	  --generations GENERATIONS
	                        Number of generations of stars each gas particle can
	                        spawn (see GENERATIONS in Gadget)
	                        
	  --viscosity           Use artificial bulk viscosity

---
#### Build Instructions

Simply run the included Makefile to build the C interface.

#### Known Issues

- Only works under Python3
- Only works with Gadget HDF5 files
- ChaNGa has no support for stellar winds
- BH physics not converted
- Only basic cosmological parameters are converted