from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectSummary(BaseModel):
    id: str
    name: str
    role: str


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    projectType: str = "mixed_material_dataset"
    defaultUnits: dict[str, str] = Field(default_factory=dict)
    defaultDownloadFormats: list[str] = Field(default_factory=lambda: ["html", "json", "png", "markdown"])
    llmConfigRef: str | None = None


def list_projects_stub() -> list[ProjectSummary]:
    return [
        ProjectSummary(
            id="project_local",
            name="Local Materials Project",
            role="owner",
        )
    ]


def create_project_stub(request: CreateProjectRequest) -> dict[str, object]:
    return {
        "id": "project_local",
        "name": request.name,
        "projectType": request.projectType,
        "defaultUnits": request.defaultUnits,
        "defaultDownloadFormats": request.defaultDownloadFormats,
        "llmConfigRef": request.llmConfigRef,
        "role": "owner",
        "status": "created",
    }
