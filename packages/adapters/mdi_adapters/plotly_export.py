from __future__ import annotations

from typing import Any

import plotly.io as pio

from mdi_artifact_core import ArtifactPayload
from mdi_schemas import ArtifactType


_FALLBACK_PREVIEW_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xff"
    b"\xff?\x00\x05\xfe\x02\xfeA\xd9\x99\x1d\x00\x00\x00\x00IEND\xaeB`\x82"
)


def plotly_payloads(fig: Any, artifact_types: list[ArtifactType]) -> list[ArtifactPayload]:
    payloads: list[ArtifactPayload] = []
    requested = set(artifact_types)
    if ArtifactType.plotly_json in requested:
        payloads.append(
            ArtifactPayload(
                artifact_type=ArtifactType.plotly_json,
                file_name="figure.json",
                content=pio.to_json(fig, validate=False, pretty=True),
                media_type="application/json",
            )
        )
    if ArtifactType.plotly_html in requested:
        payloads.append(
            ArtifactPayload(
                artifact_type=ArtifactType.plotly_html,
                file_name="figure.html",
                content=fig.to_html(include_plotlyjs="cdn", full_html=True),
                media_type="text/html",
            )
        )
    if ArtifactType.preview_png in requested:
        try:
            content = fig.to_image(format="png")
        except Exception:
            content = _FALLBACK_PREVIEW_PNG
        finally:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.preview_png,
                    file_name="preview.png",
                    content=content,
                    media_type="image/png",
                )
            )
    return payloads
