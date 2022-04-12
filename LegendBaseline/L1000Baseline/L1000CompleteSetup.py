"""
L1000 baseline complete setup file

Build the complete setup of the baseline L1000 experiment.
"""

# Third-party imports
import numpy as np
import pyg4ometry as pg4

# Our imports
# from LegendBaseline.coaxialTemplate import icpc
from LegendBaseline.L1000Baseline.LMaterials import LMaterials
from LegendBaseline.L1000Baseline.LInfrastructure import LTank


class L1000Baseline(object):
    
    def __init__(self, hallA=True, templateGe=True, filled = False):
        '''
        Construct L1000Baseline object and call world building.

        Parameters
        ----------
        hallA : bool, optional
            Choose LNGS lab (true) or SNOLab. The default is True.
        templateGe : bool, optional
            Use ideal crystals (true) or
            realistic crystals from JSON files. The default is True.
        filled : bool, optional
            Build fully filled infrastructure or tank with water only.

        Returns
        -------
        None.
        
        After construction, drawGeometry() or writeGDML()
        or continue with the stored pyg4ometry registry (self.reg).

        '''
        # registry to store gdml data
        self.reg  = pg4.geant4.Registry()

        # dictionary of materials
        lm = LMaterials(self.reg)
        lm.defineMaterials(self.reg)
        lm.PrintAll()
        self.materials = lm.getMaterialsDict()
        
        # build the geometry
        self._buildWorld(hallA, templateGe, filled)


    def __repr__(self):
        ''' Print the object purpose. '''
        s = "L1000 baseline object: build the complete setup.\n"
        return s
    


    def _placeCrystals(self, coordMap, idealGe):
        '''
        Place the Germanium crystals in template slots.

        Parameters
        ----------
        coordMap : dict
                 dictionary of detector locations;
                 key by tuple (tower number, 
                 string number, layer number and copy number)
        idealGe : bool
                True: Use default idealized crystals.
                False: Use realistic crystals from JSON files.
                Copy number in coordMap key not required in this case.

        Returns
        -------
        None. Stores geometry in registry.

        '''
        if idealGe:
            # make ideal crystal template
            placeholderRad    = 4.5   # [cm]
            placeholderHeight = 11.0  # [cm]
            geSolid = pg4.geant4.solid.Tubs("IGe", 0.0,
                                            placeholderRad,
                                            placeholderHeight,
                                            0,2*np.pi,self.reg,"cm","rad")
            geLV    = pg4.geant4.LogicalVolume(geSolid,
                                               self.materials['enrGe'],
                                               "IGeLV", self.reg)
 
            layerLV = self.reg.logicalVolumeDict['LayerLV'] # placeholder LV
            for k, pos in coordMap.items():
                pg4.geant4.PhysicalVolume([0,0,0],
                                          pos,
                                          geLV,
                                          "GePV"+str(k[3]),
                                          layerLV,
                                          self.reg, 
                                          k[3]) # with copy number
            return
        else:
            pass
        

    def _buildWorld(self, lngs, templateGe, filled):
        '''
        Build the entire geometry using module objects, see imports.

        Parameters
        ----------
        hallA : bool, optional
            Choose LNGS lab (true) or SNOLab. The default is True.
        templateGe : bool
            True: Use default idealized crystals.
            False: Use realistic crystals from JSON files.
        filled : bool, optional
            Build fully filled infrastructure or tank with water only.

        Returns
        -------
        None. Stores geometry in registry.

        '''
        # world solid and logical
        m2mm    = 1000 # convert to default [mm] unit
        rock    = 2.0   # rock thickness
        zeros   = [0.0, 0.0, 0.0]
        if lngs:
            # Hall A 18x20x100 m3 + 2m rock
            wheight = 20.0
            wwidth  = 22.0
            wlength = 102.0
            worldSolid = pg4.geant4.solid.Box("ws",wwidth,  # width x-axis
                                              wlength,      # depth y axis
                                              wheight,      # up - z axis
                                              self.reg,"m")
            rockSolid  = pg4.geant4.solid.Box("rs",wwidth-rock,
                                              wlength-rock,
                                              wheight-rock,
                                              self.reg,"m")
        else:  # SNOLab cryopit
            zeroRad = 0.0
            outerRad = 8.0 # for a 6 m radius hall
            wheight = 19.0 # for a 17 m full hall height
            worldSolid = pg4.geant4.solid.Tubs("ws",zeroRad,outerRad,
                                               wheight,
                                               0,2*np.pi,self.reg,"m","rad")
            rockSolid  = pg4.geant4.solid.Tubs("rs",zeroRad,outerRad-rock,
                                               wheight-rock,
                                               0,2*np.pi,self.reg,"m","rad")

        self.worldLV = pg4.geant4.LogicalVolume(worldSolid,
                                                self.materials['stdrock'],
                                                "worldLV", self.reg)
        # build the cavern wall and place air volume
        cavernLV     = pg4.geant4.LogicalVolume(rockSolid,
                                                self.materials["air"],
                                                "cavernLV", self.reg)
        pg4.geant4.PhysicalVolume(zeros,zeros,cavernLV,"cavernPV",
                                  self.worldLV,self.reg)
        cavernHeight = wheight - rock

        # build the infrastructre inside cavern
        ltank = LTank(self.reg, self.materials, filled) # false = not filled
        tankLV = ltank.getTankLV()
        tankHeight = ltank.height / 100 # [m] attribute of tank
        tempMap = ltank.getDetLocMap()
        
        # place the tank in cavern
        shift = -(cavernHeight-tankHeight)/2 # shift down to floor
        onfloor = [0.0, 0.0, shift*m2mm] # default units [mm]
        pg4.geant4.PhysicalVolume(zeros,onfloor,tankLV,"tankPV",
                                  cavernLV,self.reg)
        # transform local to global
        locMap = {}
        for k,v in tempMap.items():
            val = [a+b for a,b in zip(tempMap[k],onfloor)]
            locMap[k] = val
        
        # build the infrastructre inside cavern
        if filled:   # only for a filled infrastructure
            self._placeCrystals(locMap, templateGe)



    def drawGeometry(self):
        '''
        Draw the geometry held in the World volume.
        '''
        v = pg4.visualisation.VtkViewer()
        v.addLogicalVolume(self.worldLV)
        v.view()


    def writeGDML(self, filename):
        '''
        Create GDML file from stored pyg4ometry registry.

        Parameters
        ----------
        filename : string
            Full GDML file name for storing data, append '.gdml'.

        Returns
        -------
        None.

        '''
        self.reg.setWorld(self.worldLV)
        w = pg4.gdml.Writer()
        w.addDetector(self.reg)
        w.write(filename)
