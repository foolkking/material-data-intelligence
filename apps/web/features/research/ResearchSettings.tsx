"use client";

import { ProductModal } from "../../shared/ui/ObjectManagement";
import { ProductLink as Link } from "../../shared/layout/ProductNavigation";
import { modelIdentity, type UserModel } from "../../app/lib/user-models-api";

export function ResearchSettings({ models, provider, model, thinkingMode, autonomyMode, busy, loadState, onModel, onThinking, onAutonomy, onRetry, onClose }: {
  models: UserModel[]; provider: string; model: string;
  thinkingMode: "quick" | "standard" | "deep";
  autonomyMode: "STANDARD" | "BOUNDED_AUTONOMOUS";
  busy: boolean; loadState: "loading" | "ready" | "error";
  onModel: (model: UserModel) => void;
  onThinking: (mode: "quick" | "standard" | "deep") => void;
  onAutonomy: (mode: "STANDARD" | "BOUNDED_AUTONOMOUS") => void;
  onRetry: () => void; onClose: () => void;
}) {
  const selected = models.some((item) => item.provider === provider && item.model === model);
  return <ProductModal title="研究设置" eyebrow="下一次分析" description="设置用于下一次提交的问题。" onClose={onClose}
    footer={<button type="button" className="product-primary-action" onClick={onClose}>完成</button>}>
    <div className="research-settings-fields">
      <label className="research-settings-field"><span>分析模型</span>
        <select aria-label="本次分析模型" value={selected ? modelIdentity({ provider, model }) : ""} disabled={busy || !models.length} onChange={(event) => {
          const choice = models.find((item) => modelIdentity(item) === event.target.value);
          if (choice) onModel(choice);
        }}>
          {!selected ? <option value="" disabled>{loadState === "loading" ? "正在读取模型…" : "请选择模型"}</option> : null}
          {models.map((item) => <option key={modelIdentity(item)} value={modelIdentity(item)}>{item.model}{item.provider.startsWith("platform:") ? " · 平台提供" : item.label ? ` · ${item.label}` : ""}</option>)}
        </select>
      </label>
      {loadState === "error" ? <div className="research-settings-feedback" role="alert"><p>{models.length ? "模型列表暂未更新，当前选择仍保留。" : "模型暂时无法读取，请重试。"}</p><button className="product-secondary-action" type="button" onClick={onRetry}>重新读取模型</button></div> : loadState === "ready" && !models.length ? <p className="research-settings-feedback">还没有可用模型。<Link href="/console?settings=models">前往模型设置</Link></p> : loadState === "loading" ? <p role="status">正在更新可用模型…</p> : !selected ? <p className="research-settings-feedback" role="status">之前的模型已不可用，请重新选择。</p> : null}
      <label className="research-settings-field"><span>思考深度</span>
        <select aria-label="思考深度" value={thinkingMode} disabled={busy} onChange={(event) => onThinking(event.target.value as "quick" | "standard" | "deep")}>
          <option value="quick">快速</option><option value="standard">标准</option><option value="deep">深入</option>
        </select>
        <small>{thinkingMode === "quick" ? "优先快速响应。" : thinkingMode === "deep" ? "投入更多思考，可能需要更久。" : "平衡响应速度与思考深度。"}</small>
      </label>
      <div className="research-settings-exploration">
        <label><input type="checkbox" checked={autonomyMode === "BOUNDED_AUTONOMOUS"} disabled={busy} onChange={(event) => onAutonomy(event.target.checked ? "BOUNDED_AUTONOMOUS" : "STANDARD")} aria-describedby="research-exploration-help"/><span>允许继续探索</span></label>
        <p id="research-exploration-help">根据已有结果补充分析；问题得到回答、证据不足或达到本次研究上限时停止。你也可以随时停止。</p>
      </div>
      {busy ? <p role="note">当前研究进行中，结束后可修改设置。</p> : null}
    </div>
  </ProductModal>;
}
