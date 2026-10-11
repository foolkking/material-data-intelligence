import { readPlatformReferences } from "../../app/lib/platform-reference";
import styles from "./PlatformReferenceSources.module.css";

export function PlatformReferenceSources({ sources }: { sources: unknown }) {
  const references = readPlatformReferences(sources);
  if (!references.length) return null;
  return <details className={styles.root}><summary>参考资料 · {references.length}</summary>
    <ul>{references.map(source => <li key={source.referenceId}>
      <strong>{source.name}</strong> · {source.version}
      <ul>{source.sources.map(publication => <li key={publication.url}>
        <a href={publication.url} target="_blank" rel="noopener noreferrer">{publication.name}</a>
        {publication.version ? ` · ${publication.version}` : ""}{publication.license ? ` · ${publication.license}` : ""}
      </li>)}</ul>
      {Object.values(source.properties).map((property, index) => <p key={index}><strong>{property.label}</strong>：{property.definition}{property.coverage ? ` ${property.coverage}` : ""}</p>)}
    </li>)}</ul>
  </details>;
}
