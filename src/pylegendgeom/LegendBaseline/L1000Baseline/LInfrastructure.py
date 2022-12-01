"""Build infrastructure objects for Legend Geometry."""
from math import cos, pi, sin

import pyg4ometry as pg4


class LTank:
    """Define Legend Tank volume."""

    def __init__(self, reg, materials):
        """
        Build LEGEND tankl volume.

        Parameters
        ----------
        reg : pg4.geant4.Registry, optional
            if None, (almost, see next) standalone construction
        materials : dict
            predefined materials dictionary, required input.

        Returns
        -------
        None.

        """
        # allow for independent construction
        # BUT dependence on materials dictionary remains
        if reg is None:
            reg = pg4.geant4.Registry()

        # attribute for germanium placements
        self.locStore = {}

        # build tank
        self.tankLV = None
        self.build_tank(reg, materials)

    def get_tank_lv(self):
        """
        Return tank logical volume.

        Returns
        -------
        pg4.geant4.LogicalVolume

        """
        return self.tankLV

    def get_det_loc_map(self):
        """
        Return location map of positions of detector placements.

        Returns
        -------
        pg4.geant4.LogicalVolume

        """
        return self.locStore

    def build_tank(self, reg, materials):
        """
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

        """
        # add auxiliary info: type, value
        aux = pg4.gdml.Defines.Auxiliary("SensDet", "WaterDet", reg)

        zeros = [0.0, 0.0, 0.0]
        tankwalltop = 0.6  # 6 mm top wall thickness
        tankwallbottom = 0.8  # 8 mm bottom wall thickness
        inner_rad = 550  # [cm] for a 11 m diameter
        self.height = 1300.0  # [cm] attribute for requests

        tank_solid = pg4.geant4.solid.Cons(
            "tank",
            0.0,
            inner_rad + tankwallbottom,
            0.0,
            inner_rad + tankwalltop,
            self.height,
            0,
            2 * pi,
            reg,
            "cm",
            "rad",
        )
        self.tankLV = pg4.geant4.LogicalVolume(
            tank_solid, materials["steel"], "tankLV", reg
        )

        # build the water body inside tank
        # build self.waterLV as link to inner structures.
        water_solid = pg4.geant4.solid.Tubs(
            "water",
            0.0,
            inner_rad,
            self.height - tankwallbottom,
            0,
            2 * pi,
            reg,
            "cm",
            "rad",
        )
        self.water_lv = pg4.geant4.LogicalVolume(
            water_solid, materials["water"], "waterLV", reg
        )
        pg4.geant4.PhysicalVolume(
            zeros, zeros, self.water_lv, "waterPV", self.tankLV, reg
        )

        # declare as detector
        self.water_lv.addAuxiliaryInfo(aux)

        # build rest
        lar_lv = self.build_cryostat(reg, materials)
        self.build_copper_inserts(lar_lv, reg, materials)

    def build_cryostat(self, reg, materials):
        """
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

        """
        # add auxiliary info: type, value
        aux = pg4.gdml.Defines.Auxiliary("SensDet", "LArDet", reg)

        zeros = [0.0, 0.0, 0.0]
        cryowall = 0.5  # [cm]
        vacgap = 0.25  # [cm]
        cry_rad = 350.0  # [cm]
        cry_height = 700.0  # [cm]
        lidshift = (cry_height / 2 + cryowall / 2) * 10  # cm2mm factor
        top_pos = [0.0, 0.0, lidshift]
        bot_pos = [0.0, 0.0, -lidshift]

        # solids first, all cylinders
        cryo_outer_solid = pg4.geant4.solid.Tubs(
            "Cout", 0.0, cry_rad, cry_height, 0, 2 * pi, reg, "cm", "rad"
        )
        cryo_vac_solid = pg4.geant4.solid.Tubs(
            "Cvac", 0.0, cry_rad - cryowall, cry_height, 0, 2 * pi, reg, "cm", "rad"
        )
        cryo_inner_solid = pg4.geant4.solid.Tubs(
            "Cinn",
            0.0,
            cry_rad - cryowall - vacgap,
            cry_height,
            0,
            2 * pi,
            reg,
            "cm",
            "rad",
        )
        lid_solid = pg4.geant4.solid.Tubs(
            "Lid", 0.0, cry_rad, cryowall, 0, 2 * pi, reg, "cm", "rad"
        )
        lar_solid = pg4.geant4.solid.Tubs(
            "LAr",
            0.0,
            cry_rad - 2 * cryowall - vacgap,
            cry_height,
            0,
            2 * pi,
            reg,
            "cm",
            "rad",
        )
        # logical volumes next
        # build self.larLV as link to inner structures.
        cryo_outer_lv = pg4.geant4.LogicalVolume(
            cryo_outer_solid, materials["steel"], "CoutLV", reg
        )
        cryo_vac_lv = pg4.geant4.LogicalVolume(
            cryo_vac_solid, materials["vacuum"], "CvacLV", reg
        )
        cryo_inner_lv = pg4.geant4.LogicalVolume(
            cryo_inner_solid, materials["steel"], "CinnLV", reg
        )
        lid_lv = pg4.geant4.LogicalVolume(lid_solid, materials["steel"], "LidLV", reg)
        bot_lv = pg4.geant4.LogicalVolume(lid_solid, materials["steel"], "BotLV", reg)
        lar_lv = pg4.geant4.LogicalVolume(lar_solid, materials["LAr"], "LArLV", reg)
        # declare as detector
        lar_lv.addAuxiliaryInfo(aux)

        # placements
        pg4.geant4.PhysicalVolume(
            zeros, zeros, cryo_outer_lv, "CoutPV", self.water_lv, reg
        )
        pg4.geant4.PhysicalVolume(
            zeros, zeros, cryo_vac_lv, "CvacPV", cryo_outer_lv, reg
        )
        pg4.geant4.PhysicalVolume(
            zeros, zeros, cryo_inner_lv, "CinnPV", cryo_vac_lv, reg
        )
        pg4.geant4.PhysicalVolume(zeros, top_pos, lid_lv, "LidPV", self.water_lv, reg)
        pg4.geant4.PhysicalVolume(zeros, bot_pos, bot_lv, "BotPV", self.water_lv, reg)
        pg4.geant4.PhysicalVolume(zeros, zeros, lar_lv, "LArPV", cryo_inner_lv, reg)
        return lar_lv

    def build_copper_inserts(self, lar_lv, reg, materials):
        """
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

        """
        # add auxiliary info: type, value
        aux = pg4.gdml.Defines.Auxiliary("SensDet", "ULArDet", reg)

        zeros = [0.0, 0.0, 0.0]
        copper = 0.1  # [cm]
        cu_rad = 45.5  # [cm]
        cu_height = 400.0  # [cm]
        cu_shift = 150.0  # [cm] shift copper tubes inside cryostat
        ring_rad = 100.0  # [cm] copper inserts in cryostat
        # inside the copper insert
        string_rad = 34.0  # [cm] ring of strings
        inner_ring = 13.5  # [cm] inner strings 13 and 14
        n_of_layers = 8  # layers holding templates
        n_of_strings = 12  # outer ring strings holding templates
        placeholder_height = 13.0  # [cm] cylinder height for Ge+holder
        gap = 3.0  # [cm] gap between placeholders on string
        layerthickness = gap + placeholder_height

        # insert structures
        copper_solid = pg4.geant4.solid.Tubs(
            "Copper", cu_rad - copper, cu_rad, cu_height, 0, 2 * pi, reg, "cm", "rad"
        )
        ular_solid = pg4.geant4.solid.Tubs(
            "ULAr", 0.0, cu_rad - copper, cu_height, 0, 2 * pi, reg, "cm", "rad"
        )

        # make layer positions and strings in ULAr
        local_store = {}
        step = 10 * layerthickness / 2  # cm2mm
        angle = 2 * pi / n_of_strings
        zmin = 0
        for j in range(n_of_strings):  # outer ring, 12 strings
            xpos = 10 * string_rad * cos(j * angle)  # cm2mm
            ypos = 10 * string_rad * sin(j * angle)  # cm2mm
            ltmm = layerthickness * 10  # cm2mm
            for i in range(n_of_layers):
                zpos = -step + n_of_layers / 2 * ltmm - i * ltmm
                if zpos < zmin:
                    zmin = zpos
                key = (j, i, i + j * n_of_layers)  # (string,layer,copynr) key
                local_store[key] = [xpos, ypos, zpos]
        # strings 13 and 14
        for j in [12, 13]:
            for i in range(n_of_layers):
                xpos = 0  # place on x-axis
                ypos = 10 * inner_ring * cos((j - 12) * pi)
                zpos = -step + n_of_layers / 2 * ltmm - i * ltmm
                key = (j, i, i + j * n_of_layers)  # (string,layer,copynr) key
                local_store[key] = [xpos, ypos, zpos]

        # place the copper inserts
        # tower 0
        pos1 = [10 * ring_rad, 0.0, 10 * cu_shift]  # [mm]
        # tower 1
        pos2 = [0.0, 10 * ring_rad, 10 * cu_shift]
        # tower 2
        pos3 = [-10 * ring_rad, 0.0, 10 * cu_shift]
        # tower 3
        pos4 = [0.0, -10 * ring_rad, 10 * cu_shift]

        # place towers
        maxid = len(local_store)
        trsf = [pos1, pos2, pos3, pos4]
        zshift = 10 * cu_height / 2 + zmin - 100  # 10 cm gap to bottom of copper
        for tower, vec in enumerate(trsf):  # hard-coded four towers as above
            label = str(tower)
            copper_lv = pg4.geant4.LogicalVolume(
                copper_solid, materials["Cu"], "CopperLV" + label, reg
            )
            ular_lv = pg4.geant4.LogicalVolume(
                ular_solid, materials["LAr"], "ULArLV" + label, reg
            )
            # declare as detector
            ular_lv.addAuxiliaryInfo(aux)
            # placement
            pg4.geant4.PhysicalVolume(
                zeros, vec, copper_lv, "CopperPV" + label, lar_lv, reg
            )
            pg4.geant4.PhysicalVolume(
                zeros, vec, ular_lv, "ULArPV" + label, lar_lv, reg
            )
            for k, v in local_store.items():
                # (tower,string,layer,copynr) key
                key = (tower, k[0], k[1], tower * maxid + k[2])
                val = [v[0], v[1], v[2] - zshift]  # shift strings to bottom
                self.locStore[key] = val
