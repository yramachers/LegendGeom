"""
L1000 baseline complete setup file.

Build the complete setup of the baseline L1000 experiment.
"""

import csv
import logging

# Third-party imports
from math import pi

import pyg4ometry as pg4

# Our imports
from pylegendgeom.LegendBaseline.coaxialTemplate import icpc
from pylegendgeom.LegendBaseline.L1000Baseline.LInfrastructure import LTank
from pylegendgeom.LegendBaseline.L1000Baseline.LMaterials import LMaterials


class L1000Baseline:
    """Define (simplified) Legend 1000 Baseline setup."""

    def __init__(self, hall_a=True, filled=False, det_config_file=""):
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
        self.materials = lm.get_materials_dict()

        # build the geometry
        self._build_world(hall_a, filled, det_config_file)

    def __repr__(self):
        """Print the object purpose."""
        s = "L1000 baseline object: build the complete setup.\n"
        return s

    def _place_crystals(self, coord_map, det_config_file):
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
        if det_config_file == "":  # empty file name (default)
            # make ideal crystal template
            placeholder_rad = 4.5  # [cm]
            placeholder_height = 11.0  # [cm] Tube of 3.723 kg Ge
            ge_solid = pg4.geant4.solid.Tubs(
                "IGe",
                0.0,
                placeholder_rad,
                placeholder_height,
                0,
                2 * pi,
                self.reg,
                "cm",
                "rad",
            )
            ge_lv = pg4.geant4.LogicalVolume(
                ge_solid, self.materials["enrGe"], "IGeLV", self.reg
            )

            for k, pos in coord_map.items():
                label = str(k[0])
                ular_lv = self.reg.logicalVolumeDict["ULArLV" + label]
                # place in the correct tower
                pg4.geant4.PhysicalVolume(
                    [0, 0, 0], pos, ge_lv, "GePV" + str(k[3]), ular_lv, self.reg
                )
            return

        # Place real crystals
        placement_map = {}

        # For real crystals, don't need copy number.
        # Unique crystals need to be placed.
        # Transfer key to place ID key (tower,string,layer).
        # tower 0..3, string 0..11, layer 0..7 currently
        for k, v in coord_map.items():
            key = (k[0], k[1], k[2])
            placement_map[key] = v

        placementlist = []
        namelist = []
        lv_list = []
        with open(det_config_file, newline="") as f:
            reader = csv.DictReader(f)  # this handles csv with header
            try:
                for row in reader:
                    # get the placement key from configuration
                    placementlist.append(
                        (int(row["tower"]), int(row["string"]), int(row["layer"]))
                    )

                    # get JSON file name from config file.
                    jsonfilename = row["filename"]
                    det = icpc.DetICPC(jsonfilename, self.reg, self.materials)

                    # store detector name from JSON file
                    namelist.append(det.get_name())

                    # store LV's
                    lv_list.append(det.get_crystal_lv())

            except csv.Error as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"file {det_config_file}, line {reader.line_num}: {e}")
                return

        # now place the crystals individually
        for pos, tag, lv in zip(placementlist, namelist, lv_list):
            label = str(pos[0])
            ular_lv = self.reg.logicalVolumeDict["ULArLV" + label]
            if lv is not None:
                pg4.geant4.PhysicalVolume(
                    [0, 0, 0], placement_map[pos], lv, "GePV-" + tag, ular_lv, self.reg
                )

    def _build_world(self, lngs, filled, det_config_file):
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
            world_solid = pg4.geant4.solid.Box(
                "ws",
                wwidth,  # width x-axis
                wlength,  # depth y axis
                wheight,  # up - z axis
                self.reg,
                "m",
            )
            rock_solid = pg4.geant4.solid.Box(
                "rs", wwidth - rock, wlength - rock, wheight - rock, self.reg, "m"
            )
        else:  # SNOLab cryopit
            zero_rad = 0.0
            outer_rad = 8.0  # for a 6 m radius hall
            wheight = 19.0  # for a 17 m full hall height
            world_solid = pg4.geant4.solid.Tubs(
                "ws", zero_rad, outer_rad, wheight, 0, 2 * pi, self.reg, "m", "rad"
            )
            rock_solid = pg4.geant4.solid.Tubs(
                "rs",
                zero_rad,
                outer_rad - rock,
                wheight - rock,
                0,
                2 * pi,
                self.reg,
                "m",
                "rad",
            )

        self.worldLV = pg4.geant4.LogicalVolume(
            world_solid, self.materials["stdrock"], "worldLV", self.reg
        )
        # build the cavern wall and place air volume
        cavern_lv = pg4.geant4.LogicalVolume(
            rock_solid, self.materials["air"], "cavernLV", self.reg
        )
        pg4.geant4.PhysicalVolume(
            zeros, zeros, cavern_lv, "cavernPV", self.worldLV, self.reg
        )
        cavern_height = wheight - rock

        # build the infrastructre inside cavern
        ltank = LTank(self.reg, self.materials)
        tank_lv = ltank.get_tank_lv()
        tank_height = ltank.height / 100  # [m] attribute of tank
        temp_map = ltank.get_det_loc_map()

        # place the tank in cavern
        shift = -(cavern_height - tank_height) / 2  # shift down to floor
        onfloor = [0.0, 0.0, shift * m2mm]  # default units [mm]
        pg4.geant4.PhysicalVolume(
            zeros, onfloor, tank_lv, "tankPV", cavern_lv, self.reg
        )

        # place the crystals
        if filled:  # only for a filled infrastructure
            self._place_crystals(temp_map, det_config_file)

    def draw_geometry(self):
        """
        Draw the geometry held in the World volume.

        TODO: Improve/standardize colour scheme
        """
        v = pg4.visualisation.VtkViewerColouredMaterial()
        v.addLogicalVolume(self.worldLV)
        v.setSurface()
        v.setOpacity(0.5)
        v.addAxes(length=1000.0)  # 1 m axes
        v.view()

    def write_gdml(self, filename):
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
