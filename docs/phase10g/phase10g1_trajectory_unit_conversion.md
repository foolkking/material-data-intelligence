# Unit Conversion

Approved conversions are explicit: angstrom/nanometer/bohr positions to angstrom; femtosecond/picosecond to femtosecond; angstrom/fs, angstrom/ps, or nm/ps velocity to angstrom/fs; eV/angstrom or hartree/bohr force to eV/angstrom; eV or hartree energy to eV; kelvin temperature remains kelvin.

EXTXYZ positions use its documented angstrom default unless an approved metadata override is present. Velocity, force, time, energy and temperature require exact unit metadata when present. Unknown or ambiguous units fail. Bare `energy` is ignored with a warning unless `energy_scope` is exactly potential or total.
