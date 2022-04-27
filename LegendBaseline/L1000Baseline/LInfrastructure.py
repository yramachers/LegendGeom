"""
Build infrastructure objects for Legend Geometry.
"""
from math import pi, sin, cos
import pyg4ometry as pg4

class LTank(object):
    '''
    Define Legend Tank volume.

    '''
    
    def __init__(self, reg=None, materials={}):
        '''
        Build materials dictionary

        Parameters
        ----------
        reg : pg4.geant4.Registry, optional
            if None, (almost, see next) standalone construction
        materials : dict
            predefined materials dictionary, required input.

        Returns
        -------
        None.

        '''
        # allow for independent construction
        # BUT dependence on materials dictionary remains
        if reg is None:
            reg = pg4.geant4.Registry()

        # attribute for germanium placements
        self.locStore = {}

        # build tank
        self.tankLV = None
        self.buildTank(reg, materials)


    def getTankLV(self):
        '''
        get hold of tank logical volume,

        Returns
        -------
        pg4.geant4.LogicalVolume

        '''
        return self.tankLV


    def getDetLocMap(self):
        '''
        get hold of location map with positions of detector
        placements.

        Returns
        -------
        pg4.geant4.LogicalVolume

        '''
        return self.locStore


    def buildTank(self, reg, materials):
        '''
        Build the experiment infrastructure, excluding crystals.

        Parameters
        ----------
        reg : registry
            geometry storage registry from pyg4ometry.
        materials : dict
            dictionary of predefined materials.

        Returns
        -------
        None; but creates tank logical volume attribute for return
        method.
        
        '''
        # add auxiliary info: type, value
        aux = pg4.gdml.Defines.Auxiliary("SensDet","WaterDet",reg)

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

        # declare as detector
        self.waterLV.addAuxiliaryInfo(aux)

        # build rest
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
        # add auxiliary info: type, value
        aux = pg4.gdml.Defines.Auxiliary("SensDet","LArDet",reg)

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
        # declare as detector
        self.larLV.addAuxiliaryInfo(aux)
        
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
        Arrange for placeholder coordinates which
        determine locations for crystal placements
        later.

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
        # add auxiliary info: type, value
        aux = pg4.gdml.Defines.Auxiliary("SensDet","ULArDet",reg)

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
        placeholderHeight = 13.0 # [cm] cylinder height for Ge+holder
        gap               = 3.0  # [cm] gap between placeholders on string
        layerthickness    = gap + placeholderHeight

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
        # declare as detector
        ularLV.addAuxiliaryInfo(aux)
        
        # make layer positions and strings in ULAr
        localStore = {}
        step  = 10*layerthickness/2 # cm2mm
        angle = 2*pi / nofStrings
        for j in range(nofStrings):
            xpos = 10*stringRad * cos(j*angle) # cm2mm
            ypos = 10*stringRad * sin(j*angle) # cm2mm
            ltmm = layerthickness*10           # cm2mm
            for i in range(nofLayers):
                zpos = -step + nofLayers/2 * ltmm - i*ltmm
                key = (j,i,i+j*nofLayers) # (string,layer,copynr) key
                localStore[key] = [xpos,ypos,zpos]

        # place the copper inserts
        # tower 1
        pos1 = [10*ringRad, 0.0, 10*cushift]
        pg4.geant4.PhysicalVolume(zeros, pos1,
                                  copperLV,"CopperPV1",
                                  self.larLV,reg,0)
        pg4.geant4.PhysicalVolume(zeros,pos1,
                                  ularLV,"ULArPV1",
                                  self.larLV,reg,0)
        # tower 2
        pos2 = [0.0, 10*ringRad, 10*cushift]
        pg4.geant4.PhysicalVolume(zeros,pos2,
                                  copperLV,"CopperPV2",
                                  self.larLV,reg,1)
        pg4.geant4.PhysicalVolume(zeros,pos2,
                                  ularLV,"ULArPV2",
                                  self.larLV,reg,1)
        # tower 3
        pos3 = [-10*ringRad, 0.0, 10*cushift]
        pg4.geant4.PhysicalVolume(zeros,pos3,
                                  copperLV,"CopperPV3",
                                  self.larLV,reg,2)
        pg4.geant4.PhysicalVolume(zeros,pos3,
                                  ularLV,"ULArPV3",
                                  self.larLV,reg,2)
        # tower 4
        pos4 = [0.0, -10*ringRad, 10*cushift]
        pg4.geant4.PhysicalVolume(zeros,pos4,
                                  copperLV,"CopperPV4",
                                  self.larLV,reg,3)
        pg4.geant4.PhysicalVolume(zeros,pos4,
                                  ularLV,"ULArPV4",
                                  self.larLV,reg,3)

        # transform placeholder locations from local to global
        maxid = len(localStore)
        trsf = [pos1,pos2,pos3,pos4]
        for tower, vec in enumerate(trsf): # hard-coded four towers as above
            for k,v in localStore.items():
                # (tower,string,layer,copynr) key
                key = (tower,k[0],k[1],tower*maxid+k[2])
                val = [a+b for a,b in zip(localStore[k],vec)]
                self.locStore[key] = val
