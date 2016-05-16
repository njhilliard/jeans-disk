import gadget
import math
from astropy import units as u
from astropy.constants import G

gadget_trans_table = {
    """Translation table between GADGET and ChaNGa parameter names"""
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
            raise ValueError("parameter file is not a 'gadget.Parameter_file'")
        
        # Translate GADGET parameters into ChaNGa parameters
        changa_params = {}
        for k,v in gadget_params.items():
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
        m = (dKpcUnit * u.kpc).to(u.m) ** 3 / t ** 2 / G
        dMsolUnit = m.to(u.Msun) / u.Msun
        unitmass = float(gadget_params['UnitMass_in_g']) * u.g
        mass_convert_factor = (dMsolUnit * u.Msun) / unitmass.to(u.Msun)
        changa_params['dMsolUnit'] = dMsolUnit

        return changa_params, mass_convert_factor