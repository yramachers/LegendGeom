# LegendGeom
Legend simulation geometry management system

Demonstrate a proof of principle system, managing a baseline Legend simulation geometry in Python.

Depends on [PyG4ometry:](http://www.pp.rhul.ac.uk/bdsim/pyg4ometry/index.html)

Run testscript.py for output to terminal. See the list of logical volumes and physical volumes created and how to get hold of positioning information on dedicated detector
locations in the geometry as example.

The L1000Baseline object in LegendBaseline.L1000Baseline.L1000CompleteSetup knows how to build itself, how to draw itself (see pyG4ometry's VTK dependence) and how to
export the geometry to GDML, suitable for a general Geant4 simulation application.

## Quickstart for Development
```console
# Create, activate a virtualenv for local development
$ python3 -m venv env
$ source ./env/bin/activate
# Create editable install with development packages
(env) $ python3 -m pip install -e '.[all]'
...
# (For now) import/run to test/etc
(env) $ python3 -c "import pylegendgeom"
... edit/test ...
# Run checks before commiting
(env) $ pre-commit run --all-files
# Build/Check docs
(env) $ cd docs
(env) $ make
(env) $ make allver
```
