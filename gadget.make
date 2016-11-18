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
#OPT	+=  -DMETALS				# requires SFR; Z stars at zero unless CS_MODELS is used; sets header.flag_metals=1
#OPT	+=  -DSTELLARAGE			# sets header.flag_stellar_age=1; only stored if SFR is active; assumed present in ICs if set
#OPT	+=  -DMHM					# kinetic feedback
#OPT    +=  -DMODIFIED_SFR			# affects cooling; see srf_eff.c:157
#OPT    +=  -DALTERNATIVE_SFR		# requires !NOISMPRESSURE; see sfr_eff.c:452

#-------------------------------------- Viscous gas treatment 
#OPT	+=  -DNAVIERSTOKES            # Braginskii-Spitzer parametrization of the shear viscosity: mu = f x T^{5/2}
#OPT	+=  -DNAVIERSTOKES_CONSTANT   # Shear viscosity set constant for all gas particles
#OPT	+=  -DNAVIERSTOKES_BULK       # Bulk viscosity set constant for all gas particles. To run with bulk visocity only one has to set shear viscosity to zero in the parameterfile.
#OPT	+=  -DVISCOSITY_SATURATION    # Both shear and bulk viscosities are saturated, so that unphysical accelerations and entropy increases are avoided. Relevant for the cosmological simulations.
#OPT	+=  -DNS_TIMESTEP             # Enables timestep criterion based on entropy increase due to internal friction forces
#OPT	+=  -DOUTPUTSTRESS            # Outputs diagonal and offdiagonal components of viscous shear stress tensor
#OPT	+=  -DOUTPUTBULKSTRESS        # Outputs viscous bulk stress tensor
#OPT	+=  -DOUTPUTSHEARCOEFF        # Outputs variable shear viscosity coefficient in internal code units

#-------------------------------------------- Things for special behaviour
#OPT	+=  -DTRADITIONAL_SPH_FORMULATION
#OPT	+=  -DSNIA_HEATING
#OPT	+=  -DNOISMPRESSURE
#OPT	+=  -DNOVISCOSITYLIMITER
#OPT	+=  -DALLOWEXTRAPARAMS
#OPT	+=  -DLONGIDS
#OPT	+=  -DINHOMOG_GASDISTR_HINT         # if the gas is distributed very different from collisionless particles, this can helps to avoid problems in the domain decomposition
#OPT	+=  -DSPH_BND_PARTICLES
#OPT	+=  -DNEW_RATES                     # switches in updated cooling rates from Naoki
#OPT	+=  -DREAD_HSML                     # reads hsml from IC file
#OPT   	+=  -DADAPTIVE_GRAVSOFT_FORGAS      # allows variable softening length for gas particles (requires UNEQUALSOFTENINGLENGTH)
#OPT	+=  -DADAPTIVE_GRAVSOFT_FORGAS_HSML # this sets the gravitational softening for SPH particles equal to the SPH smoothing (requires ADAPTIVE_GRAVSOFT_FORGAS)
#OPT	+=  -DGENERATE_GAS_IN_ICS
#OPT	+=  -DSPLIT_PARTICLE_TYPE=4+8
#OPT	+=  -DSTART_WITH_EXTRA_NGBDEV        # Uses special MaxNumNgbDeviation for starting
#OPT	+=  -DVOLUME_CORRECTION=1.75
#OPT	+=  -DISOTHERM_EQS                  # isothermal equation of state
#OPT	+=  -DNO_UTHERM_IN_IC_FILE
#OPT	+=  -DSPECIAL_GAS_TREATMENT_IN_HIGHRESREGION
#OPT	+=  -DDONOTUSENODELIST

#--------------------------------------- Time integration options
#OPT	+=  -DALTERNATIVE_VISCOUS_TIMESTEP
#OPT	+=  -DNOSTOP_WHEN_BELOW_MINTIMESTEP
#OPT	+=  -DNOWINDTIMESTEPPING            # Disable wind reducing timestep (not recommended)
#OPT	+=  -DNOPMSTEPADJUSTMENT
#OPT	+=  -DFORCE_EQUAL_TIMESTEPS

#--------------------------------------- Output/Input options
#OPT	+=  -DOUTPUTCOOLRATE                # outputs cooling rate, and conduction rate if enabled
#OPT	+=  -DOUTPUTDENSNORM

#--------------------------------------- SPH viscosity options
#OPT	+=  -DCONVENTIONAL_VISCOSITY     # enables the old viscosity
#OPT	+=  -DTIME_DEP_ART_VISC          # Enables time dependend viscosity
#OPT	+=  -DNO_SHEAR_VISCOSITY_LIMITER # Turns of the shear viscosity supression
#OPT	+=  -DHIGH_ART_VISC_START        # Start with high rather than low viscosity
#OPT	+=  -DALTVISCOSITY               # enables alternative viscosity based on div(v)
#OPT    +=  -DARTIFICIAL_CONDUCTIVITY    # enables Price-Monaghan artificial conductivity
