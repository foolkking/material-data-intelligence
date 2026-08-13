"""Current Phase 13 canonical demo contracts.

Historical generators keep their sealed inputs immutable. Current rerun
authorities apply reviewer-approved contract corrections here.
"""

from __future__ import annotations

from typing import Any


DEMO1_CANONICAL_PROMPT = (
    "Explore this materials dataset, summarize its quality, and map its "
    "compositions in composition space."
)


CURRENT_DEMO_SPECS: tuple[dict[str, Any], ...] = (
    {
        "demoId": "P13-DEMO-01",
        "family": "Dataset Intelligence + Composition Space",
        "fixtures": (("P13-DEMO-01-FIX-01", "tests/fixtures/tables/formulas.csv", "parse"),),
        "prompt": DEMO1_CANONICAL_PROMPT,
        "alternatePrompt": "Summarize this materials dataset and show its composition-space embedding and bounded clusters.",
        "expectedTools": ("dataset.composition_space", "dataset.materials_explorer"),
    },
    {
        "demoId": "P13-DEMO-02",
        "family": "Materials ML",
        "fixtures": (("P13-DEMO-02-FIX-01", "tests/fixtures/tables/ml_results.csv", "parse"),),
        "prompt": "Evaluate these materials-model predictions and explain the largest errors and limitations.",
        "alternatePrompt": "How well does this model perform, and which samples deserve inspection?",
        "expectedTools": ("dataset.materials_explorer", "ml.regression_evaluation"),
    },
    {
        "demoId": "P13-DEMO-03",
        "family": "Structure + coordination + local environment + polyhedra + experimental XRD",
        "fixtures": (
            ("P13-DEMO-03-FIX-01", "tests/fixtures/structures/simple_cubic.cif", "parse"),
            ("P13-DEMO-03-FIX-02", "tests/fixtures/experimental_xrd/phase13_demo3_xrd.json", "parse"),
        ),
        "prompt": "Inspect this crystal structure, map its CrystalNN local environment and coordination polyhedra, then compare the supplied experimental XRD peaks with its theoretical pattern.",
        "alternatePrompt": "Map the CrystalNN local environment in this crystal and compare its supplied experimental XRD peaks with the theoretical pattern.",
        "expectedTools": ("structure.coordination_crystalnn", "structure.experimental_xrd_comparison", "structure.local_environment_polyhedra", "structure.xrd"),
    },
    {
        "demoId": "P13-DEMO-04",
        "family": "Trajectory + RDF + MSD + diffusion",
        "fixtures": (("P13-DEMO-04-FIX-01", "docs/phase10g/fixtures/trajectory_v1/fixed_lattice_md.json", "parse"),),
        "prompt": "Analyze this trajectory, show the RDF and MSD, and estimate diffusion over the full supplied time range with fit diagnostics.",
        "alternatePrompt": "What structural and transport behavior is visible in this trajectory, including RDF, MSD and diffusion over the full supplied time range?",
        "expectedTools": ("trajectory.diffusion", "trajectory.msd", "trajectory.rdf"),
    },
    {
        "demoId": "P13-DEMO-05",
        "family": "Phonon + Brillouin Zone",
        "fixtures": (
            (
                "P13-DEMO-05-FIX-01",
                "docs/phase10h/fixtures/phonon_contract/stable_band.json",
            "typed_phonon_band_import",
        ),
        (
            "P13-DEMO-05-FIX-02",
            "docs/phase10h/fixtures/phonon_contract/total_dos.json",
            "typed_phonon_dos_import",
            ),
            ("P13-DEMO-05-FIX-03", "tests/fixtures/structures/POSCAR", "parse"),
        ),
        "prompt": "Show the supplied phonon bands and density of states together with the matching Brillouin-zone context.",
        "alternatePrompt": "Help me inspect this supplied phonon result and its reciprocal-space path.",
        "expectedTools": ("phonon.band", "phonon.band_dos", "phonon.dos", "structure.brillouin_zone"),
    },
    {
        "demoId": "P13-DEMO-06",
        "family": "Volumetric",
        "fixtures": (("P13-DEMO-06-FIX-01", "docs/phase10j/fixtures/volumetric_parser/CHGCAR", "parse"),),
        "prompt": "Inspect this supplied volumetric grid and show its supported slice and volume views.",
        "alternatePrompt": "What does this supplied volumetric grid contain, and which bounded views are available?",
        "expectedTools": ("structure.volumetric_data",),
    },
    {
        "demoId": "P13-DEMO-07",
        "family": "Electronic Band + DOS",
        "fixtures": (
            ("P13-DEMO-07-FIX-01", "docs/phase10n/evidence/phase10n5_electronic_band_dos/electronic_resource_contracts/band.json", "parse"),
            ("P13-DEMO-07-FIX-02", "docs/phase10n/evidence/phase10n5_electronic_band_dos/electronic_resource_contracts/dos.json", "parse"),
        ),
        "prompt": "Inspect the supplied electronic band structure and DOS, including gap, spin, projection and compatibility limitations.",
        "alternatePrompt": "What electronic states are present in these supplied Band and DOS resources?",
        "expectedTools": ("electronic.band_structure", "electronic.dos"),
    },
)
