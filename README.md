# LegendGeom
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/warwick-legend/LegendGeom?logo=git)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/warwick-legend/LegendGeom/pkgplaceholder/main?label=main%20branch&logo=github)](https://github.com/warwick-legend/LegendGeom/actions)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Codecov](https://img.shields.io/codecov/c/github/warwick-legend/LegendGeom?logo=codecov)](https://app.codecov.io/gh/warwick-legend/LegendGeom)
![GitHub issues](https://img.shields.io/github/issues/warwick-legend/LegendGeom?logo=github)
![GitHub pull requests](https://img.shields.io/github/issues-pr/warwick-legend/LegendGeom?logo=github)
![License](https://img.shields.io/github/license/warwick-legend/LegendGeom)
[![Read the Docs](https://img.shields.io/readthedocs/LegendGeom?logo=readthedocs)](https://LegendGeom.readthedocs.io)

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

# Run tests, coverage
(env) $ pytest
...
(env) $ pytest --cov=pylegendgeom
... edit/test/repeat ...

# Build/Check docs
(env) $ cd docs
(env) $ make
... open build/html/index.html in browser of your choice ..

# Run checks before committing
(env) $ pre-commit run --all-files
```

TODO: Looking at providing a [`noxfile`](https://nox.thea.codes/en/stable/) to
help basic use, but [see SciKit-HEP's guidelines on this tool](https://scikit-hep.org/developer/tasks).
Note also that pyg4ometry is only packaged for Python 3.8-3.10 and limited platforms
across that. Nox runs with the python it was installed with, so may not always
match and configuration needed to do this is not totally obvious at the moment.
