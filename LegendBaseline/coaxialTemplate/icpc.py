"""
Build the inverted coaxial point contact crystal
template.

"""
from math import pi, tan
import numpy as np
import json

# Third-party imports
import pyg4ometry as pg4


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

        # add auxiliary info: type, value
        aux = pg4.gdml.Defines.Auxiliary("SensDet","GeDet",reg)

        # build crystal, declare as detector
        jsondict = self._readFromFile(jsonfile)
        if jsondict is not None:
            self.crystalLV = self._buildCrystal(jsondict,
                                                reg, materials)
            self.crystalLV.addAuxiliaryInfo(aux)


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
    

    def _decodePolycone(self, datadict):
        '''
        Decode shape information from JSON file as points
        constructing a G4GenericPolycone.        

        Parameters
        ----------
        datadict : dictionary
            Dictionary extracted from JSON file,
            containing crystal shape information.

        Returns
        -------
        2 lists of r and z coordinates, respectively.

        '''
        rlist = []
        zlist = []
        # extract values
        det_h = datadict['height_in_mm']
        det_r = datadict['radius_in_mm']
        # well
        welldata      = datadict['well']
        wgap = welldata['gap_in_mm']
        wrad = welldata['radius_in_mm']
        # first point
        rlist.append(wrad)
        zlist.append(det_h-wgap)
        
        # groove
        groovedata    = datadict['groove']
        grad = groovedata['outer_radius_in_mm']
        gdepth = groovedata['depth_in_mm']
        gwidth = groovedata['width_in_mm']
    
        # taper top
        tapertopdata  = datadict['taper']['top']
        tinner = tapertopdata['inner']
        alpha = tinner['angle_in_deg']
        tinheight = tinner['height_in_mm']
        tstepinner = tinheight * tan(np.deg2rad(alpha))
        if tinheight>0: # inner taper exists
            rlist.append(wrad)
            zlist.append(det_h-tinheight)
            rlist.append(wrad+tstepinner)
            zlist.append(0)
        else:
            rlist.append(wrad)
            zlist.append(0)
            
        touter = tapertopdata['outer']
        alpha = touter['angle_in_deg']
        toutheight = touter['height_in_mm']
        tstepouter = toutheight * tan(np.deg2rad(alpha))
        if toutheight>0: # outer taper exists
            rlist.append(det_r-tstepouter)
            zlist.append(0)
            rlist.append(det_r)
            zlist.append(toutheight)
        else:
            rlist.append(det_r)
            zlist.append(0)
            
        taperbotdata  = datadict['taper']['bottom']
        touter = taperbotdata['outer']
        alpha = touter['angle_in_deg']
        toutheight = touter['height_in_mm']
        tstepouter = toutheight * tan(np.deg2rad(alpha))
        if toutheight>0: # bottom taper exists
            rlist.append(det_r)
            zlist.append(det_h-toutheight)
            rlist.append(det_r-tstepouter)
            zlist.append(det_h)
        else:
            rlist.append(det_r)
            zlist.append(det_h)
        
        # walk rest of shape
        rlist.append(grad)
        zlist.append(det_h)
        rlist.append(grad)
        zlist.append(det_h-gdepth)
        rlist.append(grad-gwidth)
        zlist.append(det_h-gdepth)
        rlist.append(grad-gwidth)
        zlist.append(det_h)
        rlist.append(0)
        zlist.append(det_h)
        rlist.append(0)
        zlist.append(det_h-wgap)
        
        return rlist, zlist


    def _buildCrystal(self, dataDict, reg, materials):
        '''
        Internal: build the crystal from JSON data dict.

        Parameters
        ----------
        dataDict : dict
                dictionary data describing crystal shape.

        Returns
        -------
        geLV : pg4.geant4.LogicalVolume
            the crystal logical volume; placement in main code.

        '''
        # return ordered r,z lists, default unit [mm]
        rlist, zlist = self._decodePolycone(dataDict)

        # build generic polycone, and logical volume, default [mm]
        geSolid = pg4.geant4.solid.GenericPolycone("Ge", 0, 2*pi,
                                                   rlist,
                                                   zlist,
                                                   reg)
        geLV    = pg4.geant4.LogicalVolume(geSolid,
                                           materials['enrGe'],
                                           "GeLV", reg)
        return geLV


    def drawGeometry(self):
        '''
        Draw the geometry held in the World volume.
        Improve/standardize colour scheme
        '''
        v = pg4.visualisation.VtkViewerColoured(defaultColour='random')
        v.addLogicalVolume(self.crystalLV)
        v.addAxes(length=100.0) # 10 cm axes
        v.view()
