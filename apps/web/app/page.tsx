const timeline = [
  "upload.started",
  "file.detected",
  "file.parsed",
  "profile.ready",
  "analysis.requested",
  "plan.generated",
  "tool.started",
  "artifact.ready",
  "report.ready",
  "job.completed"
];

const artifacts = [
  "Plotly JSON",
  "Interactive HTML",
  "PNG preview",
  "MatterViz HTML",
  "metrics/table JSON",
  "Recipe JSON",
  "Markdown/HTML report"
];

export default function WorkspacePage() {
  return (
    <main className="workspace">
      <aside className="panel left-panel" aria-label="Data assets">
        <header>
          <p className="eyebrow">Dataset</p>
          <h1>Materials Workspace</h1>
        </header>
        <section>
          <h2>Assets</h2>
          <ul className="asset-list">
            <li>CIF / POSCAR / XYZ / EXTXYZ structures</li>
            <li>CSV / JSON limited / ZIP uploads</li>
            <li>Data Profile summary and field mapping</li>
            <li>Recommended tasks from structure and ML data</li>
          </ul>
        </section>
      </aside>

      <section className="canvas" aria-label="Visualization canvas">
        <div className="toolbar">
          <span>Overview</span>
          <span>Composition</span>
          <span>Structure</span>
          <span>ML Evaluation</span>
          <span>Artifacts</span>
        </div>
        <div className="artifact-grid">
          <article className="artifact-card">
            <h2>Composition Charts</h2>
            <p>ptable heatmap, element histogram, and chemical-system treemap.</p>
          </article>
          <article className="artifact-card">
            <h2>3D Viewer</h2>
            <p>MatterViz HTML loads in a sandboxed artifact frame.</p>
          </article>
          <article className="artifact-card">
            <h2>ML Evaluation</h2>
            <p>density scatter, error distribution, basic metrics, and outlier table.</p>
          </article>
          <article className="artifact-card">
            <h2>Report</h2>
            <p>Markdown and HTML report generated from auditable artifacts.</p>
          </article>
        </div>
        <footer className="bottom-panel">
          <span>Logs</span>
          <span>Artifacts</span>
          <span>Recipe</span>
          <span>Report</span>
          <span>Warnings</span>
        </footer>
      </section>

      <aside className="panel right-panel" aria-label="Agent timeline">
        <h2>Agent Timeline</h2>
        <ol>
          {timeline.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ol>
        <h2>Artifact Types</h2>
        <ul>
          {artifacts.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </aside>
    </main>
  );
}
