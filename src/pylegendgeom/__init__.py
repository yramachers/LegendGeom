# __init__ - top level package initialization for LGeom
#
"""
pylegendgeom: a package to manage the LEGEND simulation geometry
================================================================

Package depends on pyG4ometry and its dependencies.

Contents
--------
LGeom provides the following modules:

Modules
-------

    LegendBaseline  --- World logical volume, build at underground laboratory of choice.
    L1000Baseline   --- L1000 Experiment setup
    L200Baseline    --- L200  Experiment setup
    coaxialTemplate --- General co-axial Germanium crystal template to build realistic diodes.
"""

from ._version import version as __version__

__all__ = ("__version__",)
