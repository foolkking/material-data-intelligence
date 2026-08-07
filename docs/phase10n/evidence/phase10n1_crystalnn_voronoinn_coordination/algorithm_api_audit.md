# Algorithm API Audit

The implementation imports CrystalNN and VoronoiNN from `pymatgen.core.local_env` and invokes `get_nn_info(structure, site_index)`. Only the checked bounded parameter subset is exposed; upstream arbitrary kwargs are rejected.
