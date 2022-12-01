"""
L1000 baseline complete setup file

Build the complete setup of the baseline L1000 experiment.
"""

import csv

# Third-party imports
from math import pi

import pyg4ometry as pg4

# Our imports
from pylegendgeom.LegendBaseline.coaxialTemplate import icpc
from pylegendgeom.LegendBaseline.L1000Baseline.LInfrastructure import LTank
from pylegendgeom.LegendBaseline.L1000Baseline.LMaterials import LMaterials


class L1000Baseline:
    """
    Define (simplified) Legend 1000 Baseline setup.
    """

    def __init__(self, hallA=True, filled=False, detConfigFile=""):
        """
        Construct L1000Baseline object and call world building.

        Parameters
        ----------
        hallA : bool, optional
            Choose LNGS lab (true) or SNOLab. The default is True.
        filled : bool, optional
            Build fully filled infrastructure or without crystals.
        detConfigFile : str, optional file name
            Depends on filled boolean, only filled geometry places
            crystals.
            Use ideal crystals (default) or
            realistic crystals from JSON files. This case requires
            a configuration file as input, assumed CSV for now.

        Returns
        -------
        None.

        After construction, drawGeometry() or writeGDML()
        or continue with the stored pyg4ometry registry (self.reg).

        """
        # registry to store gdml data
        self.reg = pg4.geant4.Registry()

        # dictionary of materials
        lm = LMaterials(self.reg)
        lm.PrintAll()
        self.materials = lm.getMaterialsDict()

        # build the geometry
        self._buildWorld(hallA, filled, detConfigFile)

    def __repr__(self):
        """Print the object purpose."""
        s = "L1000 baseline object: build the complete setup.\n"
        return s

    def _placeCrystals(self, coordMap, detConfigFile):
        """
        Place the Germanium crystals in template slots.

        Parameters
        ----------
        coordMap : dict
                 dictionary of detector locations;
                 key by tuple (tower number,
                 string number, layer number and copy number)
        detConfigFile : str, optional file name
            Depends on filled boolean, only filled geometry places
            crystals.
            Use ideal crystals (default) or
            realistic crystals from JSON files. This case requires
            a configuration file as input, assumed CSV for now.
            Copy number in coordMap key not required in this case.

        Returns
        -------
        None. Stores geometry in registry.

        """
        if detConfigFile == "":  # empty file name (default)
            # make ideal crystal template
            placeholderRad = 4.5  # [cm]
            placeholderHeight = 11.0  # [cm] Tube of 3.723 kg Ge
            geSolid = pg4.geant4.solid.Tubs(
                "IGe",
                0.0,
                placeholderRad,
                placeholderHeight,
                0,
                2 * pi,
                self.reg,
                "cm",
                "rad",
            )
            geLV = pg4.geant4.LogicalVolume(
                geSolid, self.materials["enrGe"], "IGeLV", self.reg
            )

            for k, pos in coordMap.items():
                label = str(k[0])
                ularLV = self.reg.logicalVolumeDict["ULArLV" + label]
                # place in the correct tower
                pg4.geant4.PhysicalVolume(
                    [0, 0, 0], pos, geLV, "GePV" + str(k[3]), ularLV, self.reg
                )
            return

        # Place real crystals
        placementMap = {}

        # For real crystals, don't need copy number.
        # Unique crystals need to be placed.
        # Transfer key to place ID key (tower,string,layer).
        # tower 0..3, string 0..11, layer 0..7 currently
        for k, v in coordMap.items():
            key = (k[0], k[1], k[2])
            placementMap[key] = v

        placementlist = []
        namelist = []
        LVlist = []
        with open(detConfigFile, newline="") as f:
            reader = csv.DictReader(f)  # this handles csv with header
            try:
                for row in reader:
                    # get the placement key from configuration
                    placementlist.append(
                        (int(row["tower"]), int(row["string"]), int(row["layer"]))
                    )

                    # get JSON file name from config file.
                    jsonfilename = row["filename"]
                    det = icpc.detICPC(jsonfilename, self.reg, self.materials)

                    # store detector name from JSON file
                    namelist.append(det.getName())

                    # store LV's
                    LVlist.append(det.getCrystalLV())

            except csv.Error as e:
                print("file {}, line {}: {}".format(detConfigFile, reader.line_num, e))
                return

        # now place the crystals individually
        for pos, tag, lv in zip(placementlist, namelist, LVlist):
            label = str(pos[0])
            ularLV = self.reg.logicalVolumeDict["ULArLV" + label]
            if lv is not None:
                pg4.geant4.PhysicalVolume(
                    [0, 0, 0], placementMap[pos], lv, "GePV-" + tag, ularLV, self.reg
                )

    def _buildWorld(self, lngs, filled, detConfigFile):
        """
        Build the entire geometry using module objects, see imports.

        Parameters
        ----------
        hallA : bool, optional
            Choose LNGS lab (true) or SNOLab. The default is True.
        filled : bool, optional
            Build fully filled infrastructure or without crystals.
        detConfigFile : str, optional file name
            Depends on filled boolean, only filled geometry places
            crystals.
            Use ideal crystals (default) or
            realistic crystals from JSON files. This case requires
            a configuration file as input, assumed CSV for now.

        Returns
        -------
        None. Stores geometry in registry.

        """
        # world solid and logical
        m2mm = 1000  # convert to default [mm] unit
        rock = 2.0  # rock thickness
        zeros = [0.0, 0.0, 0.0]
        if lngs:
            # Hall A 18x20x100 m3 + 2m rock
            wheight = 20.0
            wwidth = 22.0
            wlength = 102.0
            worldSolid = pg4.geant4.solid.Box(
                "ws",
                wwidth,  # width x-axis
                wlength,  # depth y axis
                wheight,  # up - z axis
                self.reg,
                "m",
            )
            rockSolid = pg4.geant4.solid.Box(
                "rs", wwidth - rock, wlength - rock, wheight - rock, self.reg, "m"
            )
        else:  # SNOLab cryopit
            zeroRad = 0.0
            outerRad = 8.0  # for a 6 m radius hall
            wheight = 19.0  # for a 17 m full hall height
            worldSolid = pg4.geant4.solid.Tubs(
                "ws", zeroRad, outerRad, wheight, 0, 2 * pi, self.reg, "m", "rad"
            )
            rockSolid = pg4.geant4.solid.Tubs(
                "rs",
                zeroRad,
                outerRad - rock,
                wheight - rock,
                0,
                2 * pi,
                self.reg,
                "m",
                "rad",
            )

        self.worldLV = pg4.geant4.LogicalVolume(
            worldSolid, self.materials["stdrock"], "worldLV", self.reg
        )
        # build the cavern wall and place air volume
        cavernLV = pg4.geant4.LogicalVolume(
            rockSolid, self.materials["air"], "cavernLV", self.reg
        )
        pg4.geant4.PhysicalVolume(
            zeros, zeros, cavernLV, "cavernPV", self.worldLV, self.reg
        )
        cavernHeight = wheight - rock

        # build the infrastructre inside cavern
        ltank = LTank(self.reg, self.materials)
        tankLV = ltank.getTankLV()
        tankHeight = ltank.height / 100  # [m] attribute of tank
        tempMap = ltank.getDetLocMap()

        # place the tank in cavern
        shift = -(cavernHeight - tankHeight) / 2  # shift down to floor
        onfloor = [0.0, 0.0, shift * m2mm]  # default units [mm]
        pg4.geant4.PhysicalVolume(zeros, onfloor, tankLV, "tankPV", cavernLV, self.reg)

        # place the crystals
        if filled:  # only for a filled infrastructure
            self._placeCrystals(tempMap, detConfigFile)

    def drawGeometry(self):
        """
        Draw the geometry held in the World volume.
        Improve/standardize colour scheme
        """
        v = pg4.visualisation.VtkViewerColouredMaterial()
        v.addLogicalVolume(self.worldLV)
        v.setSurface()
        v.setOpacity(0.5)
        v.addAxes(length=1000.0)  # 1 m axes
        v.view()

    def writeGDML(self, filename):
        """
        Create GDML file from stored pyg4ometry registry.

        Parameters
        ----------
        filename : string
            Full GDML file name for storing data, append '.gdml'.

        Returns
        -------
        None.

        """
        self.reg.setWorld(self.worldLV)
        w = pg4.gdml.Writer()
        w.addDetector(self.reg)
        w.write(filename)
