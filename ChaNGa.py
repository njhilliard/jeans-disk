import gadget
import math
from astropy import units as u
from astropy.constants import G as G_u

# Translation table between GADGET and ChaNGa parameter names
gadget_trans_table = {
    'InitCondFile'          : 'achInFile',
    'SnapshotFileBase'      : 'achOutFile',
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
    'ArtBulkViscConst'      : 'dConstAlpha',
    'CourantFac'            : 'dEtaCourant',
    'DesNumNgb'             : 'nSmooth',
    'UnitLength_in_cm'      : 'dKpcUnit',
    'UnitMass_in_g'         : 'dMsolUnit',
    'MinGasHsmlFractional'  : 'dhMinOverSoft'
}

def convert_parameter_file(gadget_params):
        """Convert parameter values"""
        
        if not isinstance(gadget_params, gadget.Parameter_file):
            raise TypeError("parameter file is not a 'gadget.Parameter_file'")
        
        # Translate GADGET parameters into ChaNGa parameters
        changa_params = {}
        for k, v in gadget_params.items():
            if k in gadget_trans_table:
                changa_params[gadget_trans_table[k]] = v
        
        # mash together gadget directory output and file prefix
        _ = gadget_params['OutputDir'] + '/'
        changa_params['achOutFile'] = _ + gadget_params['SnapshotFileBase']
        
        # wall runtime limit seconds to minutes
        changa_params['iWallRunTime'] = int(float(gadget_params['TimeLimitCPU']) / 60.0)
        
        # simulation start step
        _ = float(gadget_params['TimeBegin']) / float(changa_params['dDelta'])
        changa_params['iStartStep'] = math.floor(_)
        
        # number of simulation steps
        _ = float(gadget_params['TimeMax']) - float(gadget_params['TimeBegin'])
        _ /= float(changa_params['dDelta'])
        changa_params['nSteps'] = math.ceil(_)

        # output writing interval
        _ = float(gadget_params['TimeBetSnapshot']) / float(changa_params['dDelta'])
        changa_params['iOutInterval'] = math.ceil(_)
        
        # output to log file interval
        _ = float(gadget_params['TimeBetStatistics']) / float(changa_params['dDelta'])
        changa_params['iLogInterval'] = math.floor(_)
        
        # factor difference for Eta parameter
        _ = 2.0 * float(gadget_params['ErrTolIntAccuracy'])
        changa_params['dEta'] = math.sqrt(_)
        
        # gadget courant factor is half of normal
        changa_params['dEtaCourant'] = 2.0 * float(gadget_params['CourantFac'])
        
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

        return changa_params, mass_convert_factor

all_parameters = """
#bBenchmark                                   Benchmark only; no output or checkpoints
#bDoGravity                                   Enable Gravity
#bLiveViz                                     enable real-time simulation render support (disabled)
#bPrintBinary                                 Print accelerations in Binary
#bStaticTest                                  Static test of performance
#bVDetails                                    Verbosity
#bdoDumpLB                                    Should Orb3dLB dump LB database to text file and stop?
#dExtraStore                                  Extra memory for new particles
#dSoft                                        Gravitational softening
#dTheta                                       Opening angle
#dTheta2                                      Opening angle after switchTheta
#iDirector                                    <number of director files
#iOctRefineLevel                              Binary logarithm of the number of sub-bins a bin is split into for Oct decomposition (e.g. octRefineLevel "3 splits into 8 sub-bins) (default
#iStartStep                                   Initial step numbering
#iVerbosity                                   Verbosity
#iWallRunTime                                 <Maximum Wallclock time (in minutes) to run> (DEFAULT
#killAt                                       Stop the simulation after this step
#nTreePieces                                  Number of TreePieces (default
#nYield                                       Yield Period (default

# Cosmological+periodic parameters
#bComove                                      Comoving coordinates
#bEwald                                       enable/disable Ewald correction
#bPeriodic                                    Periodic Boundaries
#bPhysicalSoft                                Physical gravitational softening length
#bSoftMaxMul                                  Use maximum comoving gravitational softening length as a multiplier +SMM
#dEwCut                                       <dEwCut> (DEFAULT
#dEwhCut                                      <dEwhCut> (DEFAULT
#dHubble0                                     <dHubble0> (DEFAULT
#dKpcUnit                                     <Kiloparsec/system length unit>
#dLambda                                      <dLambda> (DEFAULT
#dOmega0                                      <dOmega0> (DEFAULT
#dOmegaRad                                    <dOmegaRad> (DEFAULT
#dOmegab                                      <dOmegab> = (DEFAULT
#dPeriod                                      Periodic size
#dQuintess                                    <dQuintessence (constant w = -1/2) > (DEFAULT
#dRedTo                                       specifies final redshift for the simulation
#dSoftMax                                     maximum comoving gravitational softening length (abs or multiplier)
#daSwitchTheta                                <a to switch theta at> (DEFAULT
#ddHonHLimit                                  <|dH|/H Limiter> (DEFAULT
#dhMinOverSoft                                <Minimum h as a fraction of Softening> (DEFAULT
#dxPeriod                                     <periodic box length in x-dimension> (DEFAULT
#dyPeriod                                     <periodic box length in y-dimension> (DEFAULT
#dzPeriod                                     <periodic box length in z-dimension> (DEFAULT
#nReplicas                                    Number of periodic replicas

# Basic I/O
#achInFile                                    input file name (or base file name)
#achOutName                                   output name for snapshots and logfile
#bDoIOrderOutput                              enable/disable iOrder outputs
#bDoSoftOutput                                enable/disable soft outputs
#bDohOutput                                   enable/disable h outputs
#bDoublePos                                   input/output double precision positions
#bDoubleVel                                   input/output double precision velocities
#bParaWrite                                   enable/disable parallel writing of files
#dDumpFrameStep                               <number of steps between dumped frames> (DEFAULT
#dDumpFrameTime                               <time interval between dumped frames> (DEFAULT
#iBinaryOutput                                <array outputs 0 ascii, 1 float, 2 double, 3 FLOAT(internal)> (DEFAULT
#iCheckInterval                               Checkpoint Interval
#iLogInterval                                 Log Interval
#iOutInterval                                 Output Interval

# Time steps
#bEpsAccStep                                  Use sqrt(eps/a) timestepping
#bGravStep                                    Use gravity interaction timestepping
#dDelta                                       Base Timestep for integration
#dEta                                         Time integration accuracy
#iInitDecompBins                              Number of bins to use for the first iteration of every Oct decomposition step
#nSteps                                       Number of Timesteps
#nTruncateRung                                <number of MaxRung particles to delete MaxRung> (DEFAULT

# Performance
#bDoSimulateLB                                Should Orb3dLB simulate LB decisions from dumped text file and stop?
#bPrefetch                                    Enable prefetching in the cache (default
#bRandChunks                                  Randomize the order of remote chunk computation (default
#bUseCkLoopPar                                enable CkLoop to parallelize within node
#dFracLoadBalance                             Minimum active particles for load balancing
#dFracNoDomainDecomp                          Fraction of active particles for no new DD (DEFAULT
#dMaxBalance                                  Maximum piece ratio for load balancing
#ilbDumpIteration                             Load balancing iteration for which to dump database
#nBucket                                      Particles per Bucket (default
#nCacheDepth                                  Cache Line Depth (default
#nChunks                                      Chunks per TreePiece (default
#nDomainDecompose                             Kind of domain decomposition of particles
#nIOProcessor                                 number of simultaneous I/O processors (DEFAULT
#nPartPerChare                                Average number of particles per TreePiece

# Gas parameters
#bConcurrentSph                               Enable SPH running concurrently with Gravity
#bDoCSound                                    enable/disable sound speed outputs
#bDoDensity                                   Enable Density outputs
#bDoGas                                       Enable Gas Calculation
#bDynGrowMass                                 <dynamic growmass particles>
#bFastGas                                     Fast Gas Method
#bFeedBack                                    <Stars provide feedback> (DEFAULT
#bGasAdiabatic                                <Gas is Adiabatic>
#bGasCooling                                  <Gas is Cooling>
#bGasIsothermal                               <Gas is Isothermal>
#bSphStep                                     <SPH timestepping>
#bStarForm                                    <Star Forming> (DEFAULT
#bViscosityLimitdt                            <Balsara Viscosity Limit dt> (DEFAULT
#bViscosityLimiter                            <Viscosity Limiter> (DEFAULT
#dConstAlpha                                  <Alpha constant in viscosity> (DEFAULT
#dConstBeta                                   <Beta constant in viscosity> (DEFAULT
#dConstGamma                                  <Ratio of specific heats> (DEFAULT
#dEtaCourant                                  <Courant criterion> (DEFAULT
#dEtauDot                                     <uDot criterion> (DEFAULT
#dFracFastGas                                 <Fraction of Active Particles for Fast Gas>
#dGasConst                                    <Gas Constant>
#dGrowDeltaM                                  <Total growth in mass/particle> (DEFAULT
#dGrowEndT                                    <End time for growing mass> (DEFAULT
#dGrowStartT                                  <Start time for growing mass> (DEFAULT
#dMeanMolWeight                               <Mean molecular weight in amu> (DEFAULT
#dMsolUnit                                    <Solar mass/system mass unit>
#dResolveJeans                                <Fraction of pressure to resolve minimum Jeans mass> (DEFAULT
#iRandomSeed                                  <Feedback random Seed> (DEFAULT
#iViscosityLimiter                            <Viscosity Limiter Type> (DEFAULT
#nGrowMass                                    <number of particles to increase mass> (DEFAULT
#nSmooth                                      Number of neighbors for smooth

# requires PUSH_FORCE
#dFracPush                                    Maximum proportion of active to total particles for push-based force evaluation (DEFAULT

# requires SELECTIVE_TRACING
#iTraceRung                                   Gravity starting rung to trace selectively
#iTraceStart                                  When to start selective tracing
#iTraceFor                                    Trace this many instances of the selected rungs
#iTraceSkip                                   Skip tracing for these many iterations
#iTraceMax                                    Max. num. iterations traced

# requires CUDA
#localNodesPerReq                             Num. local node interactions allowed per CUDA request
#remoteNodesPerReq                            Num. remote node interactions allowed per CUDA request
#remoteResumeNodesPerReq                      Num. remote resume node interactions allowed per CUDA request
#localPartsPerReq                             Num. local particle interactions allowed per CUDA request
#remotePartsPerReq                            Num. remote particle interactions allowed per CUDA request
#remoteResumePartsPerReq                      Num. remote resume particle interactions allowed per CUDA request
#largePhaseThreshold                          Ratio of active to total particles at which all particles (not just active ones) are sent to gpu in the target buffer (No source particles are sent.)
"""