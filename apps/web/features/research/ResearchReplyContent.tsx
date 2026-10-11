import React, { memo, useEffect, useState, type ReactNode } from "react";
import Markdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import remend from "remend";
import { remarkLatex } from "./remark-latex";
import { remarkScientificText } from "./remark-scientific-text";
import "katex/dist/katex.min.css";
import styles from "./ResearchReplyContent.module.css";

function safeHref(href: string | undefined): string | undefined {
  if (!href || !/^https?:\/\//i.test(href)) return undefined;
  try {
    const url = new URL(href);
    return !url.username && !url.password ? url.href : undefined;
  } catch {
    return undefined;
  }
}

function ReplyCodeBlock({ children }: { children?: ReactNode }) {
  const code = React.isValidElement<{ children?: ReactNode }>(children) ? children.props.children : undefined;
  const text = typeof code === "string" ? code : "";
  const [copyState, setCopyState] = useState<"idle" | "copied" | "failed">("idle");
  useEffect(() => setCopyState("idle"), [text]);
  return <div className={styles.codeBlock}>
    <button type="button" aria-label="复制代码" onClick={async () => {
      try {
        await navigator.clipboard.writeText(text);
        setCopyState("copied");
      } catch {
        setCopyState("failed");
      }
    }}>{copyState === "copied" ? "已复制" : copyState === "failed" ? "重试复制" : "复制"}</button>
    <pre tabIndex={0} aria-label="代码块">{children}</pre>
  </div>;
}

const components: Components = {
  a: ({ href, children }) => {
    const safe = safeHref(href);
    return safe ? <a href={safe} target="_blank" rel="noopener noreferrer">{children}</a> : <>{children}</>;
  },
  // A model-authored URL cannot cause an automatic request for an image.
  // Verified scientific figures are rendered by the existing result viewer.
  img: ({ alt }) => <em>{alt || ""}</em>,
  pre: ReplyCodeBlock,
  table: ({ children }) => <div className={styles.tableScroll} role="region" aria-label="回答表格" tabIndex={0}><table>{children}</table></div>,
};
const remarkPlugins = [remarkGfm, remarkMath, remarkLatex];
const scientificRemarkPlugins = [...remarkPlugins, remarkScientificText];
const rehypePlugins: NonNullable<React.ComponentProps<typeof Markdown>["rehypePlugins"]> = [
  [rehypeKatex, { trust: false, strict: "ignore", throwOnError: false, maxExpand: 500, maxSize: 20 }],
];

/** Render only public prose; completion repair is a transient display operation. */
export const ResearchReplyContent = memo(function ResearchReplyContent({ text, streaming = false, scientific = false }: { text: string; streaming?: boolean; scientific?: boolean }) {
  const oversized = text.length > 32_768;
  const content = streaming && !oversized ? remend(text, { inlineKatex: true }) : text;
  return <div className={styles.content}>
    {oversized ? <p>{text}</p> : <Markdown components={components} remarkPlugins={scientific ? scientificRemarkPlugins : remarkPlugins} rehypePlugins={rehypePlugins}>{content}</Markdown>}
  </div>;
});
