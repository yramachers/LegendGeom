"""
test script
"""
import L1000CompleteSetup as cs

det = cs.L1000Baseline(filled=True)

print('All logical volumes:')
print(det.reg.logicalVolumeDict.keys())

print('All physical volumes:')
print(det.reg.physicalVolumeDict.keys())

#lay = det.reg.logicalVolumeDict['cavernLV'] # all volumes in Cavern
#lay = det.reg.logicalVolumeDict['ULArLV'] # all volumes in ULAr
lay = det.reg.logicalVolumeDict['LayerLV'] # all volumes in Layer
for pv in lay.daughterVolumes: # is list of physical Volumes
    print('Name: ',pv.name,' copy number: ',pv.copyNumber)
    print('Position: ',pv.position.eval())

