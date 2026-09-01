"use client";

import { ProductLink as Link } from "../../components/ProductNavigation";

export default function ScientificWorkspaceError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <main className="workspace-route-state"><section role="alert"><span className="eyebrow">Scientific Workspace</span><h1>Workspace page unavailable</h1><p>The route could not be rendered. No scientific source was modified.</p><button type="button" onClick={reset}>Retry</button><Link href="/">Back to planner</Link></section></main>;
}
