from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ProjectSummary(BaseModel):
    id: str
    projectId: str | None = None
    name: str
    role: str
    description: str | None = None
    status: str | None = None
    pinned: bool = False
    tags: list[str] = Field(default_factory=list)
    createdAt: str | None = None
    updatedAt: str | None = None


class CreateProjectRequest(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    projectType: str = "mixed_material_dataset"
    defaultUnits: dict[str, str] = Field(default_factory=dict)
    defaultDownloadFormats: list[str] = Field(default_factory=lambda: ["html", "json", "png", "markdown"])
    llmConfigRef: str | None = None


class UpdateProjectRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    archived: bool | None = None
    lifecycle: Literal["ACTIVE", "ARCHIVED", "TRASHED"] | None = None
    pinned: bool | None = None
    tags: list[str] | None = Field(default=None, max_length=12)

    @model_validator(mode="after")
    def require_change(self) -> "UpdateProjectRequest":
        if (
            self.name is None
            and self.description is None
            and self.archived is None
            and self.lifecycle is None
            and self.pinned is None
            and self.tags is None
        ):
            raise ValueError("At least one Project field is required.")
        if self.archived is not None and self.lifecycle is not None:
            raise ValueError("Use either archived compatibility input or lifecycle, not both.")
        if self.name is not None:
            self.name = self.name.strip()
            if not self.name:
                raise ValueError("Project name cannot be blank.")
        if self.tags is not None:
            normalized = []
            seen: set[str] = set()
            for value in self.tags:
                item = str(value).strip()
                if not item:
                    continue
                if len(item) > 40:
                    raise ValueError("Project tag cannot exceed 40 characters.")
                key = item.casefold()
                if key in seen:
                    continue
                seen.add(key)
                normalized.append(item)
            self.tags = normalized[:12]
        return self


class BulkProjectActionRequest(BaseModel):
    projectIds: list[str] = Field(min_length=1, max_length=100)
    action: Literal["archive", "trash", "restore", "pin", "unpin"]

    @model_validator(mode="after")
    def unique_projects(self) -> "BulkProjectActionRequest":
        self.projectIds = list(dict.fromkeys(item.strip() for item in self.projectIds if item.strip()))
        if not self.projectIds:
            raise ValueError("At least one Project is required.")
        return self


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
