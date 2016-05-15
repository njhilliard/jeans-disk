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

def convert_parameter_file(self):
        """Convert parameter values"""
        # mash together gadget directory output and file prefix
        self.cha_dict['achOutFile'] = \
                self.gad_dict['OutputDir'] + '/'\
                + self.gad_dict['SnapshotFileBase']
        # wall runtime limit seconds to minutes
        self.cha_dict['iWallRunTime'] = \
                str(int(self.gad_dict['TimeLimitCPU']) / 60)
        # simulation start step
        if self.gad_dict['TimeBegin'] != 0:
            step_floor = math.floor(float(self.gad_dict['TimeBegin']) / \
                                    float(self.cha_dict['dDelta']))
            self.cha_dict['iStartStep'] = str(step_floor)
        else:
            self.cha_dict['iStartStep'] = '0'
        # number of simulation steps
        self.cha_dict['nSteps'] = str(math.ceil(\
                (float(self.gad_dict['TimeMax'])\
                 - float(self.gad_dict['TimeBegin']))\
                / float(self.cha_dict['dDelta'])))
        # output writing interval
        self.cha_dict['iOutInterval'] = str(math.ceil(\
                float(self.gad_dict['TimeBetSnapshot'])\
                / float(self.cha_dict['dDelta'])))
        # output to log file interval
        self.cha_dict['iLogInterval'] = str(math.floor(\
                float(self.gad_dict['TimeBetStatistics'])\
                / float(self.cha_dict['dDelta'])))
        # factor difference for Eta parameter
        self.cha_dict['dEta'] = str(math.sqrt(\
                2 * float(self.gad_dict['ErrTolIntAccuracy'])))
        # gadget courant factor is half of normal
        self.cha_dict['dEtaCourant'] = \
                str(2 * float(self.gad_dict['CourantFac']))
        # convert cm to kpc
        unitlength = float(self.gad_dict['UnitLength_in_cm']) * u.cm
        dKpcUnit = float(unitlength.to(u.kpc) / u.kpc)
        self.cha_dict['dKpcUnit'] = str(dKpcUnit)
        # convert g to solar masses
        unitmass = float(self.gad_dict['UnitMass_in_g']) * u.g
        unitvelocity = float(self.gad_dict['UnitVelocity_in_cm_per_s'])\
                       * u.cm / u.s
        dMsolUnit = float(((((dKpcUnit * u.kpc).to(u.m)) ** 3\
                              / (unitlength / unitvelocity) ** 2\
                             ) / G\
                           ).to(u.Msun) / u.Msun\
                        )
        mass_convert_factor = float(float(dMsolUnit) * u.Msun\
                                    / unitmass.to(u.Msun))
        self.cha_dict['dMsolUnit'] = str(dMsolUnit)
        print('Warning: mass of simulation has changed due to changa G=1')

        return self.cha_dict, mass_convert_factor