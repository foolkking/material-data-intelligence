"use client";

import { useId } from "react";
import { preferredLiteratureSnapshot } from "../../app/lib/scientific-knowledge-api";
import { useLiteratureEvidence } from "./use-literature-evidence";

const scopeLabel: Record<string, string> = {
  METADATA_ONLY: "仅元数据",
  ABSTRACT_ONLY: "仅摘要",
  OPEN_FULL_TEXT: "开放全文",
  USER_PROVIDED_FULL_TEXT: "用户提供全文",
  STRUCTURED_REPOSITORY_FULL_TEXT: "可信仓储全文",
  REFERENCE_ONLY: "仅作为参考",
};

const statusLabel: Record<string, string> = {
  PEER_REVIEWED_ARTICLE: "期刊文章",
  PREPRINT: "预印本",
  REVIEW: "综述",
  CORRECTION: "更正",
  RETRACTED: "已撤稿",
  WITHDRAWN: "已撤回",
  EXPRESSION_OF_CONCERN: "关注声明",
  UNKNOWN: "状态未确认",
};

export function LiteratureEvidencePanel(props: { projectId: string; turnId: string }) {
  return <LiteraturePanel key={`${props.projectId}:${props.turnId}`} {...props} />;
}

function LiteraturePanel({ projectId, turnId }: { projectId: string; turnId: string }) {
  const { used, candidates, question, setQuestion, searchedQuestion, readState, operation, pendingCandidateId, unconfirmed, error, refreshUsed, runSearch, useCandidate, alreadyUsed } = useLiteratureEvidence(projectId, turnId);
  const loading = operation !== null || unconfirmed;
  const headingId = `literature-${useId()}`;
  return (
    <details className="literature-evidence-panel" aria-labelledby={headingId}>
      <summary id={headingId}>参考文献{used.length ? ` · ${used.length} 项` : ""}<small>{unconfirmed ? "等待确认" : readState === "error" ? "暂时无法读取" : readState === "loading" ? "正在读取…" : ""}</small></summary>
      <div className="literature-evidence-body">
      {readState === "error" || unconfirmed ? <div className="literature-read-error" role="status">
        {readState === "error" ? <p>已用文献暂时无法读取，请重试。</p> : null}
        <button type="button" className="product-secondary-action" disabled={readState === "loading"} onClick={() => void refreshUsed()}>{readState === "loading" ? "正在读取…" : "重新读取已用文献"}</button>
      </div> : null}
      {used.length ? (
        <div className="literature-used">
          <strong>本研究已使用 · {used.length} 项</strong>
          <ul>
            {used.map((item) => (
              <li key={item.id}>
                <span>{item.title || "文献证据"}</span>
                <small>
                  {scopeLabel[item.scope] || item.scope} ·{" "}
                  {item.support_type === "CONTRADICTING"
                    ? "相反证据"
                    : "支持/背景证据"}
                </small>
                {item.passage ? <p>{item.passage}</p> : null}
                {item.citation ? <small>{item.citation}</small> : null}
                {item.source_url ? (
                  <a
                    className="product-link-button"
                    href={item.source_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    打开来源
                  </a>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      ) : readState === "ready" ? <p>本次研究尚未引用文献。</p> : null}
      <details>
        <summary>搜索科学文献</summary>
        <p>
          搜索会将你输入的检索词发送到 OpenAlex/Crossref，查询公开文献信息。引用文献的内容会与本次数据分析结果区分展示。
        </p>
        <label>
          要检索的科学问题
          <textarea
            value={question}
            maxLength={1000}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="例如：锂离子晶体中扩散系数的常见测量条件"
          />
        </label>
        <button
          type="button"
          className="product-secondary-action"
          disabled={loading || !question.trim()}
          onClick={() => void runSearch()}
        >
          {operation === "search" ? "正在检索…" : "搜索文献"}
        </button>
      </details>
      {error ? (
        <p className={unconfirmed ? "scientific-presentation-action-status" : "literature-error"} role={unconfirmed ? "status" : "alert"}>
          {error}
        </p>
      ) : null}
      {searchedQuestion ? <p className="literature-search-summary">检索“{searchedQuestion}” · {candidates.length ? `${candidates.length} 项结果` : "未找到匹配文献，请调整检索词。"}</p> : null}
      {candidates.length ? (
        <ul className="literature-candidates" aria-label="候选文献">
          {candidates.map((candidate) => {
            const snapshot = preferredLiteratureSnapshot(candidate);
            const unavailable = ["RETRACTED", "WITHDRAWN"].includes(snapshot.publication_status);
            return (
              <li key={candidate.candidate_id}>
                <div>
                  <strong>{snapshot.title}</strong>
                  <small>
                    {snapshot.authors.slice(0, 3).join("、") ||
                      "作者信息不可用"}
                    {snapshot.publication_date
                      ? ` · ${snapshot.publication_date.slice(0, 4)}`
                      : ""}
                    {snapshot.venue ? ` · ${snapshot.venue}` : ""}
                  </small>
                  <span>
                    {statusLabel[snapshot.publication_status] ||
                      snapshot.publication_status}
                    {" · "}
                    {snapshot.abstract ? "摘要可用" : "仅元数据"}
                  </span>
                </div>
                {snapshot.abstract ? <p>{snapshot.abstract}</p> : null}
                <div className="product-row-actions">
                  <button
                    type="button"
                    className="product-secondary-action"
                    disabled={
                      loading || readState !== "ready" || unavailable || alreadyUsed(candidate)
                    }
                    onClick={() => void useCandidate(candidate)}
                  >
                    {unavailable ? "撤稿或撤回来源不可作为普通支持" : alreadyUsed(candidate) ? "已用于本研究" : operation === "select" && pendingCandidateId === candidate.candidate_id ? "正在加入…" : "用于本研究"}
                  </button>
                  {snapshot.source_url ? (
                    <a
                      className="product-link-button"
                      href={snapshot.source_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      打开来源
                    </a>
                  ) : null}
                </div>
                <details>
                  <summary>来源与访问范围</summary>
                  <dl>
                    <div>
                      <dt>证据范围</dt>
                      <dd>{snapshot.abstract ? "仅摘要" : "仅元数据"}</dd>
                    </div>
                    <div>
                      <dt>出版状态</dt>
                      <dd>
                        {statusLabel[snapshot.publication_status] ||
                          snapshot.publication_status}
                      </dd>
                    </div>
                    <div>
                      <dt>学术标识</dt>
                      <dd>
                        {snapshot.doi
                          ? `DOI ${snapshot.doi}`
                          : snapshot.arxiv_id
                            ? `arXiv ${snapshot.arxiv_id}`
                            : "提供方记录"}
                      </dd>
                    </div>
                  </dl>
                </details>
              </li>
            );
          })}
        </ul>
      ) : null}
      </div>
    </details>
  );
}
