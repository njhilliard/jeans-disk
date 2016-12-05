OPT	+=  -DUNEQUALSOFTENINGS
OPT	+=  -DMULTIPLEDOMAINS=64
OPT	+=  -DTOPNODEFACTOR=3.0
OPT	+=  -DPEANOHILBERT
OPT	+=  -DWALLCLOCK
OPT	+=  -DMYSORT
OPT	+=  -DDOUBLEPRECISION
OPT	+=  -DNO_ISEND_IRECV_IN_DOMAIN
OPT	+=  -DFIX_PATHSCALE_MPI_STATUS_IGNORE_BUG
OPT	+=  -DOUTPUTPOTENTIAL
OPT	+=  -DOUTPUTACCELERATION
OPT	+=  -DHAVE_HDF5

#OPT	+=  -DSFR
#OPT	+=  -DCOOLING
#OPT	+=  -DGENERATIONS=1			# the number of stars a gas particle may spawn
#OPT	+=  -DMOREPARAMS			# must be enabled if SFR is enabled, but does nothing
#OPT	+=  -DSTELLARAGE			# sets header.flag_stellar_age=1; only stored if SFR is active; assumed present in ICs if set

#OPT	+=  -DMETALS				# requires SFR; Z stars at zero unless CS_MODELS is used; sets header.flag_metals=1