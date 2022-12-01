"""
Build all materials for Legend Geometry structures.
"""
import pyg4ometry as pg4


class LMaterials:
    """
    Define all Legend Geometry materials.
    """

    def __init__(self, reg=None):
        """
        Build materials dictionary

        Parameters
        ----------
        reg : pg4.geant4.Registry, optional
            if None, standalone construction

        Returns
        -------
        None.

        """
        self.store = {}
        self.defineMaterials(reg)

    def getMaterialsDict(self):
        """
        get hold of materials dictionary

        Returns
        -------
        Dict
            Materials dictionary

        """
        return self.store

    def PrintAll(self):
        """
        Print out all keys in dictionary.

        Returns
        -------
        None.

        """
        print("List of keys in Materials dictionary:")
        for key in self.store.keys():
            print("key: ", key)

    def defineMaterials(self, reg):
        """
        Define all materials required to build the geometry
        in one place for look-up. Predefined materials could be
        avoided here but prevents use of materials commands
        elsewhere.

        Parameters
        ----------
        reg : pg4.geant4.Registry or None (standalone construction)

        Returns
        -------
        store: dict
            Dictionary of materials objects as values and
            simple strings as key. Once constructed, should be
            data member for geometry construction.

        """
        if reg is None:
            reg = pg4.geant4.Registry()

        # add predefined materials first - convenience
        vac = pg4.geant4.MaterialPredefined("G4_Galactic", reg)
        self.store["vacuum"] = vac
        air = pg4.geant4.MaterialPredefined("G4_AIR", reg)
        self.store["air"] = air
        water = pg4.geant4.MaterialPredefined("G4_WATER", reg)
        self.store["water"] = water
        lar = pg4.geant4.MaterialPredefined("G4_lAr", reg)
        self.store["LAr"] = lar
        steel = pg4.geant4.MaterialPredefined("G4_STAINLESS-STEEL", reg)
        self.store["steel"] = steel
        copper = pg4.geant4.MaterialPredefined("G4_Cu", reg)
        self.store["Cu"] = copper

        # compound materials
        hydrogen = pg4.geant4.MaterialPredefined("G4_H", reg)
        carbon = pg4.geant4.MaterialPredefined("G4_C", reg)
        oxygen = pg4.geant4.MaterialPredefined("G4_O", reg)
        nitrogen = pg4.geant4.MaterialPredefined("G4_N", reg)
        calcium = pg4.geant4.MaterialPredefined("G4_Ca", reg)
        magnesium = pg4.geant4.MaterialPredefined("G4_Mg", reg)

        rock = pg4.geant4.MaterialCompound("stdrock", 2.65, 4, reg)
        rock.add_material(oxygen, 0.52)
        rock.add_material(calcium, 0.27)
        rock.add_material(carbon, 0.12)
        rock.add_material(magnesium, 0.09)
        self.store["stdrock"] = rock

        polyu = pg4.geant4.MaterialCompound("polyurethane", 0.3, 4, reg)
        polyu.add_material(hydrogen, 0.57)
        polyu.add_material(carbon, 0.29)
        polyu.add_material(oxygen, 0.07)
        polyu.add_material(nitrogen, 0.07)
        self.store["polyu"] = polyu

        ge70 = pg4.geant4.Isotope("Ge70", 32, 70, 69.9243)
        ge72 = pg4.geant4.Isotope("Ge72", 32, 72, 71.9221)
        ge73 = pg4.geant4.Isotope("Ge73", 32, 73, 72.9235)
        ge74 = pg4.geant4.Isotope("Ge74", 32, 74, 73.9212)
        ge76 = pg4.geant4.Isotope("Ge76", 32, 76, 75.9214)
        enrge = pg4.geant4.ElementIsotopeMixture("enrichedGe", "enrGe", 5)
        enrge.add_isotope(ge70, 0.0000397)
        enrge.add_isotope(ge72, 0.0000893)
        enrge.add_isotope(ge73, 0.000278)
        enrge.add_isotope(ge74, 0.1258)
        enrge.add_isotope(ge76, 0.8738)
        matenrge = pg4.geant4.MaterialCompound("enrGe", 5.545, 1, reg)
        matenrge.add_element_massfraction(enrge, 1)
        self.store["enrGe"] = matenrge
