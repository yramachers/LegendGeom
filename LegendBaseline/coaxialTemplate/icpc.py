"""
Build the inverted coaxial point contact crystal
template.

"""

# Third-party imports
import pyg4ometry as pg4
import json


class detICPC(object):
    
    def __init__(self, jsonfile, reg=None, materials={}):
        '''
        Create ICPC detector logical volume (LV).

        Parameters
        ----------
        jsonfile : str
            JSON input file name describing crystal shape.
        reg : pg4.geant4.Registry, optional
            if None, (almost, see next) standalone construction
        materials : dict
            predefined materials dictionary, required input.

        Returns
        -------
        None.

        '''
        # registry to store gdml data
        # allow for independent construction
        # BUT dependence on materials dictionary remains
        if reg is None:
            reg = pg4.geant4.Registry()

        # read, then build the geometry
        self.crystalLV = None
        self.detname = ''

        jsondict = self._readFromFile(jsonfile)
        if jsondict is not None:
            self.crystalLV = self._buildCrystal(jsondict,
                                                reg, materials)


    def __repr__(self):
        ''' Print the object purpose. '''
        s = "ICPC detector: build a given ICPC from JSON input file.\n"
        return s


    def getCrystalLV(self):
        '''
        Access to logical volume as constructed here.

        Returns
        -------
        pg4.geant4.LogicalVolume
            Fully constructed LV of ICPC detector.

        '''
        return self.crystalLV
    

    def getName(self):
        '''
        Access to detector name from JSON file.

        Returns
        -------
        name : str
            Detector name string.

        '''
        return self.detname
    

    def _readFromFile(self, jsonfile):
        '''
        Internal: read the JSON file description of the crystal.

        Parameters
        ----------
        jsonfile : str
            JSON input file name describing crystal shape.

        Returns
        -------
        data : dict
            Decoded JSON file content as dictionary.

        '''
        try:
            with open(jsonfile) as jfile:
                data = json.load(jfile)
                self.detname = data['det_name'] # get name first
        except:
            print ('Error parsing JSON file.')
            return None
        return data['geometry'] # only geometry data is of interest here
    

    def _buildCrystal(dataDict, reg, materials):
        # build shape, generic polycone, and logical volume
        pass
