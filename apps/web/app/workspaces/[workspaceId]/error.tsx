"use client";

import { ProductLink as Link } from "../../components/ProductNavigation";

export default function ScientificWorkspaceError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <main className="workspace-route-state"><section role="alert"><span className="eyebrow">Scientific Workspace</span><h1>科学工作区暂时无法打开</h1><p>页面未能完成渲染；科学来源、结果和历史记录均未被修改。</p><div className="workspace-route-actions"><button type="button" className="product-primary-action" onClick={reset}>重试</button><Link className="product-secondary-action" href="/projects">查看项目</Link><Link className="product-secondary-action" href="/console">返回控制台</Link></div></section></main>;
}
