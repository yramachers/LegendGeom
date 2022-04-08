"""
Build infrastructure objects for Legend Geometry.
"""
from math import pi, sin, cos
import pyg4ometry as pg4

class LTank(object):
    '''
    Define Legend Tank volume.

    filled=True results in complete static structure construction,
    including veto, cryostat, and other details of the infastructure.
    '''
    
    def __init__(self, reg=None, materials={}, filled=False):
        '''
        Build materials dictionary

        Parameters
        ----------
        reg : pg4.geant4.Registry, optional
            if None, (almost, see next) standalone construction
        materials : dict
            predefined materials dictionary, required input.
        filled : bool, optional
            if False, construct Tank only,
            else, construct all other static objects inside Tank

        Returns
        -------
        None.

        '''
        if reg is None:
            reg = pg4.geant4.Registry()

        # build tank, switch for filled is input
        self.tankLV = None
        self.buildTank(reg, materials, filled)


    def getTankLV(self):
        '''
        get hold of tank logical volume, filled or not,
        depends on bool in construction.

        Returns
        -------
        pg4.geant4.LogicalVolume

        '''
        return self.tankLV


    def buildTank(self, reg, materials, filled):
        '''
        Build the experiment infrastructure, either just the tank
        with water volume, or fully filled excluding crystals.

        Parameters
        ----------
        reg : registry
            geometry storage registry from pyg4ometry.
        materials : dict
            dictionary of predefined materials.
        filled : bool
            decide on filled infrastructure or just tank+water volume.

        Returns
        -------
        None; but creates tank logical volume attribute for return
        method.
        
        '''
        zeros   = [0.0, 0.0, 0.0]
        tankwalltop    = 0.6 # 6 mm top wall thickness
        tankwallbottom = 0.8 # 8 mm bottom wall thickness
        innerRad = 550 # [cm] for a 11 m diameter
        self.height = 1300.0 # [cm] attribute for requests

        tankSolid  = pg4.geant4.solid.Cons("tank",0.0,
                                           innerRad+tankwallbottom,
                                           0.0, 
                                           innerRad+tankwalltop,
                                           self.height,
                                           0,2*pi,reg,"cm","rad")
        self.tankLV = pg4.geant4.LogicalVolume(tankSolid,
                                               materials["steel"],
                                               "tankLV", reg)

        # build the water body inside tank
        # build self.waterLV as link to inner structures.
        waterSolid = pg4.geant4.solid.Tubs("water", 0.0,
                                           innerRad,
                                           self.height-tankwallbottom,
                                           0,2*pi,reg,"cm","rad")
        self.waterLV = pg4.geant4.LogicalVolume(waterSolid,
                                                materials['water'],
                                                "waterLV", reg)
        pg4.geant4.PhysicalVolume(zeros,zeros,self.waterLV,"waterPV",
                                  self.tankLV,reg)

        if filled:
            self.buildCryostat(reg, materials)
            self.buildCopperInserts(reg, materials)
            
    
    def buildCryostat(self, reg, materials):
        '''
        Build the cryostat and its liquid argon filling.

        Parameters
        ----------
        reg : registry
            geometry storage registry from pyg4ometry.
        materials : dict
            dictionary of predefined materials.

        Returns
        -------
        None.

        '''
        zeros   = [0.0, 0.0, 0.0]
        cryowall = 3.0 # [cm]
        vacgap = 1.0   # [cm]
        cryRad = 350.0 # [cm]
        cryHeight = 700.0 # [cm]
        lidshift = (cryHeight/2+cryowall/2)*10 # cm2mm factor
        topPos  = [0.0,0.0,lidshift]
        botPos  = [0.0,0.0,-lidshift]

        # solids first, all cylinders
        cryoOuterSolid = pg4.geant4.solid.Tubs("Cout", 0.0,
                                           cryRad,
                                           cryHeight,
                                           0,2*pi,reg,"cm","rad")
        cryoVacSolid   = pg4.geant4.solid.Tubs("Cvac", 0.0,
                                           cryRad-cryowall,
                                           cryHeight,
                                           0,2*pi,reg,"cm","rad")
        cryoInnerSolid = pg4.geant4.solid.Tubs("Cinn", 0.0,
                                           cryRad-cryowall-vacgap,
                                           cryHeight,
                                           0,2*pi,reg,"cm","rad")
        lidSolid       = pg4.geant4.solid.Tubs("Lid", 0.0,
                                           cryRad,
                                           cryowall,
                                           0,2*pi,reg,"cm","rad")
        larSolid       = pg4.geant4.solid.Tubs("LAr", 0.0,
                                           cryRad-2*cryowall-vacgap,
                                           cryHeight,
                                           0,2*pi,reg,"cm","rad")
        # logical volumes next
        # build self.larLV as link to inner structures.
        cryoOuterLV  = pg4.geant4.LogicalVolume(cryoOuterSolid,
                                                materials['steel'],
                                                "CoutLV", reg)
        cryoVacLV    = pg4.geant4.LogicalVolume(cryoVacSolid,
                                                materials['vacuum'],
                                                "CvacLV", reg)
        cryoInnerLV  = pg4.geant4.LogicalVolume(cryoInnerSolid,
                                                materials['steel'],
                                                "CinnLV", reg)
        lidLV        = pg4.geant4.LogicalVolume(lidSolid,
                                                materials['steel'],
                                                "LidLV", reg)
        botLV        = pg4.geant4.LogicalVolume(lidSolid,
                                                materials['steel'],
                                                "BotLV", reg)
        self.larLV   = pg4.geant4.LogicalVolume(larSolid,
                                                materials['LAr'],
                                                "LArLV", reg)
        
        # placements
        pg4.geant4.PhysicalVolume(zeros,zeros,cryoOuterLV,"CoutPV",
                                  self.waterLV,reg)
        pg4.geant4.PhysicalVolume(zeros,zeros,cryoVacLV,"CvacPV",
                                  cryoOuterLV,reg)
        pg4.geant4.PhysicalVolume(zeros,zeros,cryoInnerLV,"CinnPV",
                                  cryoVacLV,reg)
        pg4.geant4.PhysicalVolume(zeros,topPos,lidLV,"LidPV",
                                  self.waterLV,reg)
        pg4.geant4.PhysicalVolume(zeros,botPos,botLV,"BotPV",
                                  self.waterLV,reg)
        pg4.geant4.PhysicalVolume(zeros,zeros,self.larLV,"LArPV",
                                  cryoInnerLV,reg)
        
    
    def buildCopperInserts(self, reg, materials):
        '''
        Build the copper inserts into the LAr volume.
        Those are filled with layers, representing
        place holders for Germanium assemblies, i.e.
        physical volumes, called TemplatePV, that are meant
        to hold crystal and holder, all placed and 
        distinguished by copy number.

        Parameters
        ----------
        reg : registry
            geometry storage registry from pyg4ometry.
        materials : dict
            dictionary of predefined materials.

        Returns
        -------
        None.

        '''
        zeros   = [0.0, 0.0, 0.0]
        copper = 0.35    # [cm]
        cuRad  = 40.0    # [cm]
        cuHeight = 400.0 # [cm]
        cushift  = 150.0 # [cm] shift copper tubes inside cryostat
        ringRad  = 100.0 # [cm] copper inserts in cryostat
        # inside the copper insert
        stringRad = 30.0 # [cm] ring of strings
        nofLayers  = 8   # layers holding templates
        nofStrings = 12  # how many strings holding templates
        placeholderRad    = 5.0  # [cm] place holder volume for Ge+holder
        placeholderHeight = 13.0 # [cm] cylinder height for Ge+holder
        gap               = 3.0  # [cm] gap between placeholders on string
        layerthickness    = gap + placeholderHeight
        topph             = [0.0, 0.0, 10*placeholderHeight/2] # cm2mm
        botph             = [0.0, 0.0, -10*gap/2] # cm2mm

        # insert structures
        copperSolid = pg4.geant4.solid.Tubs("Copper", cuRad-copper,
                                            cuRad,
                                            cuHeight,
                                            0,2*pi,reg,"cm","rad")
        ularSolid   = pg4.geant4.solid.Tubs("ULAr", 0.0,
                                            cuRad-copper,
                                            cuHeight,
                                            0,2*pi,reg,"cm","rad")
        
        copperLV  = pg4.geant4.LogicalVolume(copperSolid,
                                             materials['Cu'],
                                             "CopperLV", reg)
        ularLV    = pg4.geant4.LogicalVolume(ularSolid,
                                             materials['LAr'],
                                             "ULArLV", reg)
        # Layers for place holders
        layerSolid = pg4.geant4.solid.Tubs("Layer", 0.0,
                                            placeholderRad,
                                            layerthickness,
                                            0,2*pi,reg,"cm","rad")
        layerLV    = pg4.geant4.LogicalVolume(layerSolid,
                                              materials['LAr'],
                                              "LayerLV", reg)
        # insert gap on top and place holder template volume at bottom
        # in layer
        gapSolid   = pg4.geant4.solid.Tubs("Gap", 0.0,
                                            placeholderRad,
                                            gap,
                                            0,2*pi,reg,"cm","rad")
        gapLV      = pg4.geant4.LogicalVolume(gapSolid,
                                              materials['LAr'],
                                              "GapLV", reg)
        pg4.geant4.PhysicalVolume(zeros,topph,gapLV,"GapPV",
                                  layerLV,reg)
        templateSolid = pg4.geant4.solid.Tubs("Template", 0.0,
                                              placeholderRad,
                                              placeholderHeight,
                                              0,2*pi,reg,"cm","rad")
        templateLV   = pg4.geant4.LogicalVolume(templateSolid,
                                                materials['LAr'],
                                                "TemplateLV", reg)
        pg4.geant4.PhysicalVolume(zeros,botph,templateLV,"TemplatePV",
                                  layerLV,reg)
        
        # make layers and strings in ULAr
        step  = 10*layerthickness/2 # cm2mm
        angle = pi / nofStrings
        for j in range(nofStrings):
            xpos = 10*stringRad * cos(j*angle) # cm2mm
            ypos = 10*stringRad * sin(j*angle) # cm2mm
            ltmm = layerthickness*10           # cm2mm
            for i in range(nofLayers):
                pg4.geant4.PhysicalVolume(zeros,
                                          [xpos,ypos,
                                           -step + nofLayers/2*ltmm
                                           -i*ltmm],
                                          layerLV,
                                          "LayerPV"+str(i+j*nofLayers),
                                          ularLV,
                                          reg, 
                                          i+j*nofLayers) # with copy number

        # place the copper inserts
        # tower 0
        pg4.geant4.PhysicalVolume(zeros,[10*ringRad, 0.0, 10*cushift],
                                  copperLV,"CopperPV",
                                  self.larLV,reg,0)
        pg4.geant4.PhysicalVolume(zeros,[10*ringRad, 0.0, 10*cushift],
                                  ularLV,"ULArPV",
                                  self.larLV,reg,0)
        # tower 1
        pg4.geant4.PhysicalVolume(zeros,[0.0, 10*ringRad, 10*cushift],
                                  copperLV,"CopperPV2",
                                  self.larLV,reg,1)
        pg4.geant4.PhysicalVolume(zeros,[0.0, 10*ringRad,10*cushift],
                                  ularLV,"ULArPV2",
                                  self.larLV,reg,1)
        # tower 2
        pg4.geant4.PhysicalVolume(zeros,[-10*ringRad, 0.0, 10*cushift],
                                  copperLV,"CopperPV3",
                                  self.larLV,reg,2)
        pg4.geant4.PhysicalVolume(zeros,[-10*ringRad, 0.0, 10*cushift],
                                  ularLV,"ULArPV3",
                                  self.larLV,reg,2)
        # tower 3
        pg4.geant4.PhysicalVolume(zeros,[0.0, -10*ringRad, 10*cushift],
                                  copperLV,"CopperPV4",
                                  self.larLV,reg,3)
        pg4.geant4.PhysicalVolume(zeros,[0.0, -10*ringRad, 10*cushift],
                                  ularLV,"ULArPV4",
                                  self.larLV,reg,3)
