import type { ResearchSourceDataset } from "../../app/lib/research-display";
import { ProductLink as Link } from "../layout/ProductNavigation";

export function SourceDatasetList({ sources, projectId }: {
  sources: readonly ResearchSourceDataset[];
  projectId?: string;
}) {
  if (!sources.length) return null;
  return <ul className="source-dataset-list">
    {sources.map((source) => <li key={source.datasetId}>
      {projectId ? <Link href={`/projects/${encodeURIComponent(projectId)}/data?dataset=${encodeURIComponent(source.datasetId)}`}>
        {source.name.trim() || "未命名数据"}
      </Link> : source.name}
    </li>)}
  </ul>;
}
