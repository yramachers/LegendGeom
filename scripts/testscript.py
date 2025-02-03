"""test script."""

# import pyg4ometry
from pylegendgeom.LegendBaseline.L1000Baseline import L1000CompleteSetup

det = L1000CompleteSetup.L1000Baseline(filled=True)

print("All logical volumes:")
print(det.reg.logicalVolumeDict.keys())

print("All physical volumes:")
print(det.reg.physicalVolumeDict.keys())

# lay = det.reg.logicalVolumeDict['cavernLV'] # all volumes in Cavern
lay = det.reg.logicalVolumeDict["ULArLV0"]  # all volumes in ULAr
# lay = det.reg.logicalVolumeDict['LArLV'] # all volumes in LAr
for pv in lay.daughterVolumes:  # is list of physical Volumes
    print("Name: ", pv.name, " copy number: ", pv.copyNumber)
    print("Position: ", pv.position.eval())

# det.drawGeometry() # draw all

# selective logical volume drawing
# v = pyg4ometry.visualisation.VtkViewerColoured(defaultColour='random')
# wl = det.reg.logicalVolumeDict['LArLV'] # pick any LV
# v.addLogicalVolume(wl)
# v.setWireframe()
# v.addAxes(length=1000.0) # 1 m axes
# v.view()
