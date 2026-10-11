type Finding = {
  statement: string;
  reasoning_assessment?: { accepted: boolean; scope: string; limitations: string[] } | null;
};

/** Editorial grouping only: callers retain each full finding and its citations. */
export function reportFindingPresentation(findings: readonly Finding[]): {
  statements: string[];
  sharedLimitations: string[];
} {
  const statements = findings.map(item => item.statement);
  const unchanged = { statements, sharedLimitations: [] as string[] };
  if (findings.length < 2) return unchanged;
  const scope = findings[0].reasoning_assessment?.scope;
  if (!scope?.trim() || scope === "current ScientificResult scope" || findings.some(item =>
    item.reasoning_assessment?.accepted !== true || item.reasoning_assessment.scope !== scope
    || !Array.isArray(item.reasoning_assessment.limitations))) return unchanged;

  const candidates = [...new Set(findings[0].reasoning_assessment!.limitations)].filter(limit =>
    typeof limit === "string" && limit.trim() === limit && /[。！？.!?]$/u.test(limit)
    && findings.every(item => item.reasoning_assessment!.limitations.includes(limit)))
    .sort((a, b) => b.length - a.length);
  const sharedLimitations: string[] = [];
  // Move only exact complete suffix sentences, in their original order. A
  // mid-sentence qualifier or a limitation from another scope stays in place.
  while (candidates.length) {
    const index = candidates.findIndex(limit => statements.every(statement => {
      const text = statement.trimEnd();
      return text.endsWith(limit) && /[。！？.!?]\s*$/u.test(text.slice(0, -limit.length));
    }));
    if (index < 0) break;
    const [limit] = candidates.splice(index, 1);
    statements.forEach((statement, i) => { statements[i] = statement.trimEnd().slice(0, -limit.length).trimEnd(); });
    sharedLimitations.unshift(limit);
  }
  return { statements, sharedLimitations };
}
