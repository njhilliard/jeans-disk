import gadget
import math
import os
from astropy import units as u
from astropy.constants import G as G_u

# Translation table between GADGET and ChaNGa parameter names
gadget_trans_table = {
    'InitCondFile'          : 'achInFile',
    'SnapshotFileBase'      : 'achOutName',
    'TimeLimitCPU'          : 'iWallRunTime',
    'ComovingIntegrationOn' : 'bComove',
    'CoolingOn'             : 'bGasCooling',
    'StarformationOn'       : 'bStarForm',
    'TimeBegin'             : 'iStartStep',
    'TimeMax'               : 'nSteps',
    'Omega0'                : 'dOmega0',
    'OmegaLambda'           : 'dLambda',
    'OmegaBaryon'           : 'dOmegab',
    'HubbleParam'           : 'dHubble0',
    'BoxSize'               : 'dPeriod',
    'PeriodicBoundariesOn'  : 'bPeriodic',
    'TimeBetSnapshot'       : 'iOutInterval',
    'TimeBetStatistics'     : 'iLogInterval',
    'ErrTolIntAccuracy'     : 'dEta',
    'MaxSizeTimestep'       : 'dDelta',
    'ErrTolTheta'           : 'dTheta',
    'UnitLength_in_cm'      : 'dKpcUnit',
    'UnitMass_in_g'         : 'dMsolUnit'
}

def get_input_file(file_name):
    _, input_name = os.path.split(file_name)
    input_file_basename, _ = os.path.splitext(input_name)
    return input_file_basename

def convert_parameter_file(gadget_params, args, do_gas):
    """Convert parameter values"""
    
    gadget_file, output_directory = args.gadget_file, args.out_dir
    
    if not isinstance(gadget_params, gadget.Parameter_file):
        raise TypeError("parameter file is not a 'gadget.Parameter_file'")
    
    # Translate GADGET parameters into ChaNGa parameters
    changa_params = {}
    for k, v in gadget_params.items():
        if k in gadget_trans_table:
            changa_params[gadget_trans_table[k]] = v
    
    changa_params['achOutName'] = output_directory + '/' + gadget_params['SnapshotFileBase'] + '.out'
    changa_params['achInFile']  = output_directory + '/' + get_input_file(gadget_file) + '.tipsy'
    
    # wall runtime limit seconds to minutes
    changa_params['iWallRunTime'] = int(float(gadget_params['TimeLimitCPU']) / 60.0)
    
    # simulation start step
    _ = float(gadget_params['TimeBegin']) / float(changa_params['dDelta'])
    changa_params['iStartStep'] = math.floor(_)
    
    # number of simulation steps
    _ = float(gadget_params['TimeMax']) - float(gadget_params['TimeBegin'])
    _ /= float(changa_params['dDelta'])
    changa_params['nSteps'] = math.ceil(_)
    
    # use sqrt(eps/a) timestepping
    changa_params['bEpsAccStep'] = 1

    # output writing interval
    _ = float(gadget_params['TimeBetSnapshot']) / float(changa_params['dDelta'])
    changa_params['iOutInterval'] = math.ceil(_)
    
    # output to log file interval
    _ = float(gadget_params['TimeBetStatistics']) / float(changa_params['dDelta'])
    changa_params['iLogInterval'] = math.floor(_)
    
    # factor difference for Eta parameter
    _ = 2.0 * float(gadget_params['ErrTolIntAccuracy'])
    changa_params['dEta'] = math.sqrt(_)
    
    # disable density outputs by default
    changa_params['bDoDensity'] = 0

    # convert cm to kpc
    unitlength = float(gadget_params['UnitLength_in_cm']) * u.cm
    dKpcUnit = unitlength.to(u.kpc) / u.kpc
    changa_params['dKpcUnit'] = dKpcUnit
        
    # convert mass to solar masses
    unitvelocity = float(gadget_params['UnitVelocity_in_cm_per_s']) * u.cm / u.s
    unittime = unitlength / unitvelocity
    m = (dKpcUnit * u.kpc).to(u.m) ** 3 / unittime ** 2 / G_u
    dMsolUnit = m.to(u.Msun) / u.Msun
    unitmass = float(gadget_params['UnitMass_in_g']) * u.g
    mass_convert_factor = (dMsolUnit * u.Msun) / unitmass.to(u.Msun)
    changa_params['dMsolUnit'] = dMsolUnit
    
    if do_gas:
        changa_params['bDoGas'] = int(do_gas)
        changa_params['bSphStep'] = 1
        changa_params['bConcurrentSph'] = 1

        changa_params['nSmooth'] = gadget_params['DesNumNgb']
        changa_params['dhMinOverSoft'] = gadget_params['MinGasHsmlFractional']

        # gadget courant factor is half of normal
        changa_params['dEtaCourant'] = 2.0 * float(gadget_params['CourantFac'])
        
        if int(changa_params['bStarForm']) == 1:
            if not args.generations:
                raise ValueError('Star formation enabled, but --generations not given')
            else:
                # Form *at least* args.generations many stars
                changa_params['dMinGasMass'] = dMsolUnit / (float(args.generations) + 1.0)
            
            # ChaNGa requires dStarEff < 1.0 (this is likely a bug)
            if args.generations == 1:
                changa_params['dStarEff'] = 0.99
            else:
                changa_params['dStarEff'] = 1.0 / float(args.generations)
        
        if args.viscosity:
            changa_params['bBulkViscosity'] = 1
            changa_params['dConstAlpha'] = gadget_params['ArtBulkViscConst']
            changa_params['dConstBeta'] = gadget_params['ArtBulkViscConst']
            print('Beta constant of artificial viscosity assumed to be the same as alpha constant')
        else:
            changa_params['bBulkViscosity'] = 0
    
    return changa_params, mass_convert_factor

all_parameters = """
#----- general_gravity -----
#   bCannonical                              Cannonical Comoving eqns (IGNORED)
#   bDoCSound                                enable/disable sound speed outputs = -csound
#   bDoDensity                               Enable Density outputs
#   bDohOutput                               enable/disable h outputs = -hout
#   bDoIOrderOutput                          enable/disable iOrder outputs = -iordout
#   bDoSoftOutput                            enable/disable soft outputs = -softout
#   bPhysicalSoft                            Physical gravitational softening length
#   bSoftMaxMul                              Use maximum comoving gravitational softening length as a multiplier +SMM
#   daSwitchTheta                            <a to switch theta at> = 1./3.
#   dSoft                                    Gravitational softening
#   dSoftMax                                 maximum comoving gravitational softening length (abs or multiplier)
#   dTheta                                   Opening angle
#   dTheta2                                  Opening angle after switchTheta
#   iBinaryOutput                            <array outputs 0 ascii, 1 float, 2 double, 3 FLOAT(internal)> = 0
#   iCheckInterval                           Checkpoint Interval
#   iLogInterval                             Log Interval
#   iOrder                                   Multipole expansion order(IGNORED)
#   iOutInterval                             Output Interval
#   iStartStep                               Initial step numbering
#   iWallRunTime                             <Maximum Wallclock time (in minutes) to run> = 0 = infinite
#   killAt                                   Stop the simulation after this step
#   nSmooth                                  Number of neighbors for smooth
#
#----- gravity_time_steps -----
#   bEpsAccStep                              Use sqrt(eps/a) timestepping
#   bGravStep                                Use gravity interaction timestepping
#   bKDK                                     KDK timestepping (IGNORED)
#   dDelta                                   Base Timestep for integration
#   dEta                                     Time integration accuracy
#   iInitDecompBins                          Number of bins to use for the first iteration of every Oct decomposition step
#   iMaxRung                                 Maximum timestep rung (IGNORED)
#   iOctRefineLevel                          Binary logarithm of the number of sub-bins a bin is split into for Oct decomposition (e.g. octRefineLevel 3 splits into 8 sub-bins) (default: 1)
#   nSteps                                   Number of Timesteps
#
#----- output_parameters -----
#   achInFile                                input file name (or base file name)
#   achOutName                               output name for snapshots and logfile
#   bDoublePos                               input/output double precision positions = -dp
#   bDoubleVel                               input/output double precision velocities = -dv
#   bLiveViz                                 enable real-time simulation render support (disabled)
#   bOverwrite                               overwrite outputs (IGNORED)
#   bParaRead                                enable/disable parallel reading of files (IGNORED)
#   bParaWrite                               enable/disable parallel writing of files
#   bPrintBinary                             Print accelerations in Binary
#   bStandard                                output in standard TIPSY binary format (IGNORED)
#   dDumpFrameStep                           <number of steps between dumped frames> = -1 (disabled)
#   dDumpFrameTime                           <time interval between dumped frames> = -1 (disabled)
#   dExtraStore                              Extra memory for new particles
#   dFracLoadBalance                         Minimum active particles for load balancing
#   dMaxBalance                              Maximum piece ratio for load balancing
#   iDirector                                <number of director files: 1, 2, 3> = 1
#   nIOProcessor                             number of simultaneous I/O processors = 0 (all)
#
#----- cosmology_parameters -----
#   bComove                                  Comoving coordinates
#   bEwald                                   enable/disable Ewald correction = +ewald
#   bPeriodic                                Periodic Boundaries
#   dEwCut                                   <dEwCut> = 2.6
#   dEwhCut                                  <dEwhCut> = 2.8
#   dHubble0                                 <dHubble0> = 0.0
#   dLambda                                  <dLambda> = 0.0
#   dOmega0                                  <dOmega0> = 1.0
#   dOmegab                                  <dOmegab> = 0.0
#   dOmegaRad                                <dOmegaRad> = 0.0
#   dPeriod                                  Periodic size
#   dQuintess                                <dQuintessence (constant w = -1/2) > = 0.0
#   dRedTo                                   specifies final redshift for the simulation
#   dxPeriod                                 <periodic box length in x-dimension> = 1.0
#   dyPeriod                                 <periodic box length in y-dimension> = 1.0
#   dzPeriod                                 <periodic box length in z-dimension> = 1.0
#   nReplicas                                Number of periodic replicas
#
#----- gas_parameters -----
#   bBulkViscosity                           <Bulk Viscosity> = 0
#   bDoGas                                   Enable Gas Calculation
#   bFastGas                                 Fast Gas Method
#   bGasAdiabatic                            <Gas is Adiabatic> = +GasAdiabatic
#   bGasCooling                              <Gas is Cooling> = +GasCooling
#   bGasIsothermal                           <Gas is Isothermal> = -GasIsothermal
#   bGeometric                               geometric/arithmetic mean to calc Grad(P/rho) = +geo
#   bViscosityLimiter                        <Viscosity Limiter> = 1
#   dConstAlpha                              <Alpha constant in viscosity> = 1.0
#   dConstBeta                               <Beta constant in viscosity> = 2.0
#   dConstGamma                              <Ratio of specific heats> = 5/3
#   ddHonHLimit                              <|dH|/H Limiter> = 0.1
#   dFracFastGas                             <Fraction of Active Particles for Fast Gas>
#   dGasConst                                <Gas Constant>
#   dhMinOverSoft                            <Minimum h as a fraction of Softening> = 0.0
#   dKpcUnit                                 <Kiloparsec/system length unit>
#   dMeanMolWeight                           <Mean molecular weight in amu> = 1.0
#   dMsolUnit                                <Solar mass/system mass unit>
#   dResolveJeans                            <Fraction of pressure to resolve minimum Jeans mass> = 0.0
#   iGasModel                                <Gas model employed> = 0 (Adiabatic)
#   iViscosityLimiter                        <Viscosity Limiter Type> = 1
#
#----- sph_timestepping -----
#   bSphStep                                 <SPH timestepping>
#   bViscosityLimitdt                        <Balsara Viscosity Limit dt> = 0
#   dEtaCourant                              <Courant criterion> = 0.4
#   dEtauDot                                 <uDot criterion> = 0.25
#   nTruncateRung                            <number of MaxRung particles to delete MaxRung> = 0
#
#----- star_formation -----
#   bStarForm                                <Star Forming> = 0
#   dCStar                                   <Star formation coefficient> = 0.1
#   dDeltaStarForm                           <Minimum SF timestep in years> = 1e6
#   dInitStarMass                            <Initial star mass> = 0
#   dMaxStarMass                             <Maximum amount of star mass a hybrid particle can contain = 0.0
#   dMinGasMass                              <Minimum mass of a gas particle> = 0.0
#   dOverDenMin                              <Minimum overdensity for forming stars> = 2
#   dPhysDenMin                              <Minimum physical density for forming stars (atoms/cc)> = .1
#   dSoftMin                                 <Minimum softening for star formation> = 0.0
#   dStarEff                                 <Fraction of gas converted into stars per timestep> = .3333
#   dTempMax                                 <Maximum temperature at which star formation occurs> = 1.5e4
#   iRandomSeed                              <Feedback random Seed> = 1
#   iRandomSeed                              <Star formation random Seed> = 1
#   iStarFormRung                            <Star Formation Rung> = 0
#
#----- feedback -----
#   achIMF                                   <IMF> = Kroupa93
#   bFeedBack                                <Stars provide feedback> = 0
#   bShortCoolShutoff                        <Use snowplow time> = 0
#   bSmallSNSmooth                           <smooth SN ejecta over blast or smoothing radius> = blast radius
#   bSNTurnOffCooling                        <Do SN turn off cooling> = 1
#   dESN                                     <Energy of supernova in ergs> = 0.1e51
#   dExtraCoolShutoff                        <Extend shutoff time> = 1.0
#   dMaxCoolShutoff                          <Maximum time to shutoff cooling in years> = 3e7
#   dMaxGasMass                              <Maximum mass of a gas particle> = FLT_MAX
#   iNSNIIQuantum                            <Min # SNII per timestep> = 0.
#   nSmoothFeedback                          <number of particles to smooth feedback over> = 64
#
#----- cooling_cosmo -----
#   bDoIonOutput                             enable/disable Ion outputs (cooling only) = +Iout
#   bIonNonEqm                               <Gas is Cooling Non-Equilibrium Abundances> = +IonNonEqm
#   bLowTCool                                enable/disable low T cooling = +ltc
#   bSelfShield                              enable/disable Self Shielded Cooling = +ssc
#   bUV                                      read in an Ultra Violet file = +UV
#   bUVTableUsesTime                         Ultra Violet Table uses time = +UVTableUsesTime
#   dCoolingTmax                             <Maximum Temperature for Cooling> = 1e9K
#   dCoolingTmin                             <Minimum Temperature for Cooling> = 10K
#   dMassFracHelium                          <Primordial Helium Fraction (by mass)> = 0.25
#   nCoolingTable                            <# Cooling table elements> = 15001
#
#----- cooling_grackle -----
#   bComoving                                on = +bComoving
#   bDoIonOutput                             enable/disable Ion outputs (cooling only) = +Iout
#   grackle_verbose                          on = +grackle_verbose [off]
#   metal_cooling                            on = +metal_cooling
#   primordial_chemistry                     -primordial_chemistry=0 [values 0,1,2,3]
#   use_grackle                              on = +use_grackle
#   UVbackground                             on = +UVbackground
#   with_radiative_cooling                   on = +with_radiative_cooling
#
#----- cooling_planet -----
#   dBetaCooling                             <Effective cooling time (tCool*omega)> = 1
#   dCoolingTmax                             <Maximum Temperature for Cooling> = 1e9K
#   dCoolingTmin                             <Minimum Temperature for Cooling> = 0K
#   dY_Total                                 <Y_Total> = 2
#
#----- grow_mass: slowly growing mass of particles -----
#   bDynGrowMass                             <dynamic growmass particles>
#   dGrowDeltaM                              <Total growth in mass/particle> = 0.0
#   dGrowEndT                                <End time for growing mass> = 1.0
#   dGrowStartT                              <Start time for growing mass> = 0.0
#   nGrowMass                                <number of particles to increase mass> = 0
#
#----- performance -----
#   bConcurrentSph                           Enable SPH running concurrently with Gravity
#   bdoDumpLB                                Should Orb3dLB dump LB database to text file and stop?
#   bDoSimulateLB                            Should Orb3dLB simulate LB decisions from dumped text file and stop?
#   bNoCache                                 Disable the CacheManager caching behaviour
#   bPrefetch                                Enable prefetching in the cache (default: ON)
#   bRandChunks                              Randomize the order of remote chunk computation (default: ON)
#   bUseCkLoopPar                            enable CkLoop to parallelize within node
#   bVDetails                                Verbosity
#   dFracNoDomainDecomp                      Fraction of active particles for no new DD = 0.0
#   ilbDumpIteration                         Load balancing iteration for which to dump database
#   iVerbosity                               Verbosity
#   lbcommCutoffMsgs                         Cutoff for communication recording (IGNORED)
#   nBucket                                  Particles per Bucket (default: 12)
#   nCacheDepth                              Cache Line Depth (default: 4)
#   nCacheSize                               Size of cache (IGNORED)
#   nChunks                                  Chunks per TreePiece (default: 1)
#   nDomainDecompose                         Kind of domain decomposition of particles
#   nPartPerChare                            Average number of particles per TreePiece
#   nTreePieces                              Number of TreePieces (default: 8*procs)
#   nYield                                   Yield Period (default: 5)
#
#----- push_gravity: required PUSH_GRAVITY to be defined -----
#   dFracPush                                Maximum proportion of active to total particles for push-based force evaluation = 0.0
#
#----- selective_tracing: requires SELECTIVE_TRACING to be defined -----
#   iTraceFor                                Trace this many instances of the selected rungs
#   iTraceMax                                Max. num. iterations traced
#   iTraceRung                               Gravity starting rung to trace selectively
#   iTraceSkip                               Skip tracing for these many iterations
#   iTraceStart                              When to start selective tracing
#
#----- testing -----
#   bBenchmark                               Benchmark only; no output or checkpoints
#   bDoGravity                               Enable Gravity
#   bStaticTest                              Static test of performance
#
#----- cuda_parameters -----
#   largePhaseThreshold                      Ratio of active to total particles at which all particles (not just active ones) are sent to gpu in the target buffer (No source particles are sent.)
#   localNodesPerReq                         Num. local node interactions allowed per CUDA request (in millions)
#   localPartsPerReq                         Num. local particle interactions allowed per CUDA request (in millions)
#   remoteNodesPerReq                        Num. remote node interactions allowed per CUDA request (in millions)
#   remotePartsPerReq                        Num. remote particle interactions allowed per CUDA request (in millions)
#   remoteResumeNodesPerReq                  Num. remote resume node interactions allowed per CUDA request (in millions)
#   remoteResumePartsPerReq                  Num. remote resume particle interactions allowed per CUDA request (in millions)
"""

