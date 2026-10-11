import { inputOriginNames, projectParameterNames, projectParameterValues } from "./project-science-labels";
import { presentationMetricUnit } from "./scientific-presentation";

export const projectInputRecord = (value: unknown): Record<string, unknown> => value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : {};

export type ProjectParameterInput = {
  tool_call_id: string; tool_id: string; input_origin: string;
  content_hash: string; resolved_parameters: Record<string, unknown>;
};

const parameterOrigins: Readonly<Record<string, string>> = {
  "reference.convert_units": "USER_PARAMETERS", "generation.function_curve": "USER_PARAMETERS",
  "composition.from_formula": "USER_PARAMETERS", "viz.inline_xy": "USER_TEXT_DATA",
  "generation.ideal_crystal": "IDEAL_MODEL",
};

export function projectInputOrigin(provenance: unknown): string | undefined {
  const source = projectInputRecord(provenance);
  return source.execution_scope === "PROJECT" ? inputOriginNames[String(source.input_origin)] : undefined;
}

export function projectParameterInputs(provenance: unknown): ProjectParameterInput[] {
  const source = projectInputRecord(provenance);
  if (!projectInputOrigin(source) || !Array.isArray(source.parameter_inputs) || source.parameter_inputs.length > 8) return [];
  const inputs = source.parameter_inputs.map(projectInputRecord);
  return inputs.filter((item): item is ProjectParameterInput => typeof item.tool_call_id === "string" && !!item.tool_call_id
    && inputs.filter(other => other.tool_call_id === item.tool_call_id).length === 1
    && parameterOrigins[String(item.tool_id)] === item.input_origin
    && (source.input_origin === "MIXED" || item.input_origin === source.input_origin)
    && typeof item.content_hash === "string" && /^[a-f0-9]{64}$/.test(item.content_hash)
    && !!item.resolved_parameters && typeof item.resolved_parameters === "object" && !Array.isArray(item.resolved_parameters));
}

function parameterText(key: string, value: unknown): string {
  if (Array.isArray(value)) return value.map(item => parameterText(key, item)).join("、");
  if (typeof value === "string") {
    if (["from_unit", "to_unit"].includes(key)) return presentationMetricUnit(value);
    return ["kind", "quantity", "style", "prototype"].includes(key) ? projectParameterValues[value] || value : value;
  }
  return value == null ? "未指定" : typeof value === "object" ? JSON.stringify(value) : String(value);
}

export type ProjectParameterRow = { key: string; label: string } & (
  { kind: "value" | "text"; text: string } | { kind: "functions"; groups: ProjectParameterRow[][] }
);

/** Shared display projection; saved parameters and verbatim table text stay unchanged. */
export function projectParameterRows(values: unknown): ProjectParameterRow[] {
  return Object.entries(projectInputRecord(values)).map(([key, value]) => ({
    key, label: projectParameterNames[key] || key,
    ...(key === "data_text" && typeof value === "string" ? { kind: "text" as const, text: value }
      : key === "functions" && Array.isArray(value) ? { kind: "functions" as const, groups: value.map(projectParameterRows) }
        : { kind: "value" as const, text: parameterText(key, value) }),
  }));
}
