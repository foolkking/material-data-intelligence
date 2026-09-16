"use client";

import { useEffect, useState } from "react";

import {
  listTurnLiteratureEvidence,
  searchScientificLiterature,
  selectLiteratureEvidence,
  type LiteratureCandidate,
  type LiteratureEvidenceRow,
} from "../../app/lib/scientific-knowledge-api";

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

export function LiteratureEvidencePanel({
  projectId,
  turnId,
}: {
  projectId: string;
  turnId: string;
}) {
  const [used, setUsed] = useState<LiteratureEvidenceRow[]>([]);
  const [candidates, setCandidates] = useState<LiteratureCandidate[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    void listTurnLiteratureEvidence(turnId)
      .then((value) => {
        if (active) setUsed(value.literatureEvidence || []);
      })
      .catch(() => {
        if (active) setUsed([]);
      });
    return () => {
      active = false;
    };
  }, [turnId]);

  async function runSearch() {
    const value = question.trim();
    if (!value) return;
    setLoading(true);
    setError("");
    try {
      const response = await searchScientificLiterature(
        projectId,
        turnId,
        value,
      );
      setCandidates(response.candidates || []);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "文献检索未完成。");
    } finally {
      setLoading(false);
    }
  }

  async function useCandidate(candidate: LiteratureCandidate) {
    setLoading(true);
    setError("");
    try {
      await selectLiteratureEvidence(projectId, turnId, candidate);
      const response = await listTurnLiteratureEvidence(turnId);
      setUsed(response.literatureEvidence || []);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "文献证据未能加入研究。");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section
      className="literature-evidence-panel"
      aria-labelledby="literature-evidence-title"
    >
      <header>
        <div>
          <p className="product-kicker">外部科学知识</p>
          <h3 id="literature-evidence-title">已发表文献</h3>
        </div>
        <span>不同于“根据你的数据计算”</span>
      </header>
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
      ) : (
        <p>当前研究尚未使用外部文献。已有科学结果仍是首要证据。</p>
      )}
      <details>
        <summary>搜索科学文献</summary>
        <p>
          仅在你明确提交后，系统才会向受限的 OpenAlex/Crossref
          元数据服务发送这段科学查询；不会发送项目名、内部 ID 或完整研究历史。
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
          {loading ? "正在检索…" : "搜索文献"}
        </button>
      </details>
      {error ? (
        <p className="literature-error" role="alert">
          {error}
        </p>
      ) : null}
      {candidates.length ? (
        <ul className="literature-candidates" aria-label="候选文献">
          {candidates.map((candidate) => {
            const snapshot =
              candidate.snapshots.find((item) => Boolean(item.abstract)) ||
              candidate.snapshots[0];
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
                      loading || snapshot.publication_status === "RETRACTED"
                    }
                    onClick={() => void useCandidate(candidate)}
                  >
                    {snapshot.publication_status === "RETRACTED"
                      ? "撤稿来源不可作为普通支持"
                      : "用于本研究"}
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
    </section>
  );
}
