"use client";

import { ProductLink as Link, useProductRouter } from "../../shared/layout/ProductNavigation";
import { useEffect, useState } from "react";

import { getPlannerJob } from "../../app/lib/planner-api";
import { getWorkspace } from "../../app/lib/workspace-api";
import { ProductShell, RequireProductAuth } from "../../shared/layout/ProductShell";

type CompatibilityState = "loading" | "missing";

export function LegacyAnalysisCompatibility({ jobId }: { jobId: string }) {
  const router = useProductRouter();
  const [state, setState] = useState<CompatibilityState>("loading");
  useEffect(() => {
    if (!jobId) { setState("missing"); return; }
    let active = true;
    void getPlannerJob(jobId).then((job) => {
      if (!active) return;
      if (!job.projectId) { setState("missing"); return; }
      router.replace(`/projects/${encodeURIComponent(job.projectId)}/research?run=${encodeURIComponent(jobId)}`);
    }).catch(() => { if (active) setState("missing"); });
    return () => { active = false; };
  }, [jobId, router]);
  return <CompatibilitySurface state={state} title="正在恢复历史分析" />;
}

export function LegacyWorkspaceCompatibility({ workspaceId }: { workspaceId: string }) {
  const router = useProductRouter();
  const [state, setState] = useState<CompatibilityState>("loading");
  useEffect(() => {
    const controller = new AbortController();
    void getWorkspace(workspaceId, { signal: controller.signal }).then((response) => {
      const workspace = response.data?.workspace;
      if (!workspace) { setState("missing"); return; }
      const selection = new URLSearchParams(window.location.search).get("selection");
      const destination = new URL(`/projects/${encodeURIComponent(workspace.projectId)}/research`, window.location.origin);
      destination.searchParams.set("run", workspace.sourceJobId);
      if (selection) destination.searchParams.set("selection", selection);
      router.replace(`${destination.pathname}${destination.search}`);
    }).catch(() => { if (!controller.signal.aborted) setState("missing"); });
    return () => controller.abort();
  }, [router, workspaceId]);
  return <CompatibilitySurface state={state} title="正在恢复历史研究结果" />;
}

function CompatibilitySurface({ state, title }: { state: CompatibilityState; title: string }) {
  return <RequireProductAuth><ProductShell><section className="document-page"><div className="product-state" role={state === "loading" ? "status" : "alert"}><h1>{state === "loading" ? title : "历史链接暂时无法解析"}</h1><p>{state === "loading" ? "正在将你带到新版项目研究页面。" : "记录没有被删除。可以从项目列表重新打开对应的研究结果。"}</p>{state === "missing" ? <Link className="product-primary-action" href="/projects">查看项目</Link> : null}</div></section></ProductShell></RequireProductAuth>;
}
