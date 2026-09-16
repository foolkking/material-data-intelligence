from __future__ import annotations

from mdi_api.scientific_viewers.schemas import ScientificViewerDescriptor


# These renderer contracts are produced by Result/Artifact pipelines and do
# not represent persisted ScientificObject types. Keeping them explicit avoids
# advertising object-level version/archive routes that cannot be resolved.
RESULT_ONLY_VIEWER_TYPES = frozenset({
    "analysis.rdf",
    "reciprocal.brillouin_zone",
})


class ScientificViewerRegistry:
    def __init__(self, descriptors: list[ScientificViewerDescriptor]) -> None:
        self._descriptors = {item.object_type: item for item in descriptors}
        if len(self._descriptors) != len(descriptors):
            raise ValueError("SCIENTIFIC_VIEWER_REGISTRY_DUPLICATE")

    def resolve(self, object_type: str) -> ScientificViewerDescriptor:
        return self._descriptors.get(object_type) or ScientificViewerDescriptor(
            viewer_id="scientific.generic",
            object_type=object_type,
            renderer_key="generic-safe-fallback",
            support="FALLBACK",
            interaction_capabilities=["inspect_metadata", "download"],
            selection_capabilities=[],
            maximum_payload_bytes=2 * 1024 * 1024,
            fallback_policy="METADATA_AND_AUTHORIZED_DOWNLOAD",
        )

    def list(self) -> list[ScientificViewerDescriptor]:
        return sorted(self._descriptors.values(), key=lambda item: item.object_type)


def _descriptor(
    object_type: str,
    renderer_key: str,
    *,
    interactions: list[str],
    selections: list[str],
    maximum_payload_bytes: int = 8 * 1024 * 1024,
    support: str = "PROFESSIONAL",
) -> ScientificViewerDescriptor:
    return ScientificViewerDescriptor(
        viewer_id=f"scientific.{renderer_key}",
        object_type=object_type,
        renderer_key=renderer_key,
        support=support,
        interaction_capabilities=interactions,
        selection_capabilities=selections,
        maximum_payload_bytes=maximum_payload_bytes,
        fallback_policy="SCIENTIFIC_METADATA_THEN_SAFE_DOWNLOAD",
    )


def build_scientific_viewer_registry() -> ScientificViewerRegistry:
    mib = 1024 * 1024
    return ScientificViewerRegistry([
        _descriptor("materials.dataset", "scientific-table", interactions=["sort", "filter", "inspect_units"], selections=["TABLE_ROW", "TABLE_COLUMN"], maximum_payload_bytes=8 * mib),
        _descriptor("materials.table", "scientific-table", interactions=["sort", "filter", "inspect_units"], selections=["TABLE_ROW", "TABLE_COLUMN"], maximum_payload_bytes=8 * mib),
        _descriptor("structure.crystal", "structure-3d", interactions=["rotate", "zoom", "reset", "inspect_cell"], selections=["STRUCTURE_SITE"], maximum_payload_bytes=8 * mib),
        _descriptor("trajectory.atomic", "trajectory", interactions=["frame_navigation", "playback", "inspect_time"], selections=["TRAJECTORY_FRAME", "TRAJECTORY_ATOM"], maximum_payload_bytes=32 * mib),
        _descriptor("diffraction.xrd.experimental", "xrd", interactions=["zoom", "inspect_series", "inspect_peaks"], selections=["XRD_PEAK"], maximum_payload_bytes=8 * mib),
        _descriptor("diffraction.xrd.theoretical", "xrd", interactions=["zoom", "inspect_series", "inspect_peaks"], selections=["XRD_PEAK"], maximum_payload_bytes=8 * mib),
        _descriptor("electronic.band_structure", "band-structure", interactions=["zoom", "inspect_k_path", "inspect_energy"], selections=["BAND_POINT", "BAND_SEGMENT"], maximum_payload_bytes=16 * mib),
        _descriptor("electronic.dos", "density-of-states", interactions=["zoom", "inspect_series", "inspect_energy"], selections=["DOS_SERIES", "ENERGY_INTERVAL"], maximum_payload_bytes=16 * mib),
        _descriptor("phonon.band_structure", "phonon-band", interactions=["zoom", "inspect_q_path"], selections=["PHONON_Q_POINT", "PHONON_BRANCH"], maximum_payload_bytes=16 * mib),
        _descriptor("phonon.dos", "phonon-dos", interactions=["zoom", "inspect_series"], selections=["PHONON_BRANCH", "ENERGY_INTERVAL"], maximum_payload_bytes=16 * mib),
        _descriptor("volumetric.field", "volumetric", interactions=["isosurface", "slice", "inspect_field"], selections=["VOLUMETRIC_REGION"], maximum_payload_bytes=16 * mib),
        _descriptor("volumetric.charge_density", "volumetric", interactions=["isosurface", "slice", "inspect_field"], selections=["VOLUMETRIC_REGION"], maximum_payload_bytes=16 * mib),
    ])


__all__ = ["RESULT_ONLY_VIEWER_TYPES", "ScientificViewerRegistry", "build_scientific_viewer_registry"]
