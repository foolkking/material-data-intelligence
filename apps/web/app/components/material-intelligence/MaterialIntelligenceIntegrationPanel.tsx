"use client";

import { useMemo } from "react";

import type { Artifact } from "../../lib/planner-api";
import { validateCompositionSpacePayload } from "../composition-space/CompositionSpaceExplorerPanel";
import { validateDatasetExplorerPayload } from "../dataset-explorer/DatasetMaterialsExplorerPanel";
import { validateMaterialsMlProductPayload } from "../materials-ml/MaterialsMlEvaluationPanel";
import {
  inspectMaterialIntelligenceArtifacts,
  type JsonRecord,
  type MaterialIntelligenceAssessment,
  type MaterialIntelligenceProductId,
} from "./materialIntelligenceIntegration";

export function assessMaterialIntelligenceProducts(artifacts: readonly Artifact[]): MaterialIntelligenceAssessment {
  return inspectMaterialIntelligenceArtifacts(artifacts, validateProduct);
}

export function MaterialIntelligenceIntegrationPanel({ artifacts }: { artifacts: Artifact[] }) {
  const assessment = useMemo(() => assessMaterialIntelligenceProducts(artifacts), [artifacts]);
  if (!assessment.products.some((item) => item.artifact)) return null;
  const binding = assessment.authority?.binding;
  return <section className="panel material-intelligence" data-testid="material-intelligence-integration" aria-label="Material Intelligence product status">
    <header className="panel-heading">
      <div><span>Profile-authoritative product surface</span><h2>Material Intelligence</h2></div>
      <span className="badge">{assessment.authority ? "Bound" : "Partial"}</span>
    </header>
    {binding ? <dl className="mini-grid material-intelligence-identity">
      <Field label="Dataset" value={binding.datasetId} />
      <Field label="Dataset version" value={binding.datasetVersion} />
      <Field label="Profile" value={binding.profileId} />
      <Field label="Semantic hash" value={compactHash(binding.semanticHash)} />
    </dl> : <p className="empty-state" role="status">Profile authority is unavailable. Independently valid products remain accessible, but cross-artifact linking is disabled.</p>}
    <ul className="material-product-state-list" aria-label="Material Intelligence capability states">
      {assessment.products.map((product) => <li key={product.id} data-testid={`material-product-${product.id}`}>
        <span><strong>{product.label}</strong><small>{product.capability}</small></span>
        <span className={`badge material-product-state-${product.state.toLowerCase()}`}>{product.state}</span>
        {product.state !== "PRODUCED" ? <code>{product.reason}</code> : null}
      </li>)}
    </ul>
    <p className="dataset-method-note">Availability combines Material Data Profile 2.0 readiness with validated product artifacts. A filename alone never enables a capability.</p>
  </section>;
}

function validateProduct(id: MaterialIntelligenceProductId, payload: JsonRecord): string | null {
  if (id === "dataset_explorer") {
    const result = validateDatasetExplorerPayload(payload);
    return result.ok ? null : result.reason;
  }
  if (id === "composition_space") {
    const result = validateCompositionSpacePayload(payload);
    return result.ok ? null : result.reason;
  }
  const result = validateMaterialsMlProductPayload(id, payload);
  return result.ok ? null : result.reason;
}

function Field({ label, value }: { label: string; value: string }) { return <div><dt>{label}</dt><dd>{value || "-"}</dd></div>; }
function compactHash(value: string): string { return value.length > 16 ? `${value.slice(0, 8)}...${value.slice(-8)}` : value; }
