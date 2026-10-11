"use client";

import { createDeferredScientificViewer } from "./DeferredScientificViewer";

export const LazyScientificResultViewer = createDeferredScientificViewer(
  () => import("./ScientificViewerAdapter").then((module) => ({ default: module.ScientificResultViewer })),
  { label: "正在打开科学结果…", sourceKey: (props) => JSON.stringify([
    props.projectId, props.datasetId, props.jobId,
    props.selected.artifactId || props.selected.id, props.selected.type, props.selected.version,
    props.selected.sha256 || props.selected.contentHash,
  ]) },
);

export const LazyScientificSourceViewer = createDeferredScientificViewer(
  () => import("./ScientificViewerAdapter").then((module) => ({ default: module.ScientificSourceViewer })),
  { label: "正在打开科学数据…", sourceKey: (props) => JSON.stringify([
    props.projectId, props.resource.datasetId, props.resource.objectId, props.resource.versionId, props.resource.objectHash,
  ]) },
);

export const LazyScientificObjectViewer = createDeferredScientificViewer(
  () => import("./scientific-viewer/ScientificObjectViewer").then((module) => ({ default: module.ScientificObjectViewer })),
  { label: "正在打开对象版本…", sourceKey: (props) => JSON.stringify([props.projectId, props.objectId, props.versionId]) },
);
