import numpy as np
import matplotlib.pyplot as plt
import pyg4ometry as pg4

# us
from pylegendgeom.LegendBaseline.coaxialTemplate import icpc
from pylegendgeom.LegendBaseline.L1000Baseline.LMaterials import LMaterials

reg  = pg4.geant4.Registry()
lm = LMaterials(reg)
materials = lm.getMaterialsDict()

# test; assumes json file in same folder
det = icpc.detICPC('V09372A.json',reg=reg,materials=materials)

print(det.getName())

det.drawGeometry()

# plot the generic polycone data
#lv = det.getCrystalLV()
#rarr = np.array(lv.solid.pR)
#zarr = np.array(lv.solid.pZ)
#plt.plot(rarr,zarr,'-o')
#plt.show()
