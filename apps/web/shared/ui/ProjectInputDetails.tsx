import { inputOriginNames, projectScienceNames } from "../../app/lib/project-science-labels";
import { projectInputOrigin, projectInputRecord, projectParameterInputs, projectParameterRows, type ProjectParameterRow } from "../../app/lib/project-input";
import { PlatformReferenceSources } from "./PlatformReferenceSources";
import styles from "./PlatformReferenceSources.module.css";

export { projectInputOrigin, projectParameterInputs } from "../../app/lib/project-input";

function Parameters({ rows }: { rows: ProjectParameterRow[] }) {
  return <dl className={styles.parameters}>{rows.map(row => <div key={row.key}>
    <dt>{row.label}</dt>
    <dd>{row.kind === "text" ? <pre tabIndex={0} aria-label="原始输入表格">{row.text}</pre>
      : row.kind === "functions" ? row.groups.map((group, index) => <Parameters key={index} rows={group} />)
        : row.text}</dd>
  </div>)}</dl>;
}

export function ProjectInputDetails({ provenance }: { provenance: unknown }) {
  const source = projectInputRecord(provenance);
  if (!projectInputOrigin(source)) return null;
  const inputs = projectParameterInputs(source);
  return <div className={styles.root}>
    {inputs.length ? <details><summary>输入参数与原始数据</summary>
      {inputs.map((item, index) => <section key={`${item.tool_call_id}:${index}`}>
        <strong>{projectScienceNames[String(item.tool_id)]} · {inputOriginNames[String(item.input_origin)]}</strong>
        <Parameters rows={projectParameterRows(item.resolved_parameters)} />
        <details><summary>输入标识</summary><code>{String(item.content_hash)}</code></details>
      </section>)}
    </details> : null}
    <PlatformReferenceSources sources={source.reference_sources} />
  </div>;
}
