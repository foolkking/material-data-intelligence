# Format Scope

Supported: UTF-8 multi-frame `.extxyz`/content-confirmed `.xyz`, and canonical trajectory JSON with the exact schema marker. Detection combines allowlisted extension, bounded 4096-byte sniff, frame header, metadata markers, and canonical schema marker.

Deferred: plain XYZ trajectory, ASE traj, LAMMPS dump, XTC/TRR/DCD, NetCDF/HDF5, XDATCAR, vasprun.xml, PDB trajectory, compressed archive, URL, notebook object, pickle, and plugins. Existing plain XYZ remains a static nonperiodic Atoms parser path.
