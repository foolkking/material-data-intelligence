import type { AnchorHTMLAttributes, ReactNode } from "react";

const ARTIFACT_CONTENT_PATH =
  /^\/api\/planner\/jobs\/[^/?#]+\/artifacts\/[^/?#]+\/content(?:\?[^#]*)?$/u;

export function isTrustedArtifactDownloadHref(href: string): boolean {
  return ARTIFACT_CONTENT_PATH.test(href);
}

export function sanitizeArtifactDownloadName(downloadName?: string): string | undefined {
  if (!downloadName) return undefined;
  const normalized = downloadName
    .replace(/[\u0000-\u001f\u007f]/gu, "")
    .replace(/[\\/]+/gu, "-")
    .replace(/^\.+/u, "")
    .trim()
    .slice(0, 120);
  if (!normalized || normalized === "." || normalized === "..") return undefined;
  return normalized;
}

export function artifactDownloadHref(href: string): string {
  return `${href}${href.includes("?") ? "&" : "?"}download=true`;
}

export function ArtifactDownloadLink({
  href,
  children,
  downloadName,
  ...props
}: Readonly<{
  href: string;
  children: ReactNode;
  downloadName?: string;
}> &
  Omit<
    AnchorHTMLAttributes<HTMLAnchorElement>,
    "children" | "href" | "rel" | "target" | "download"
  >) {
  if (!isTrustedArtifactDownloadHref(href)) return null;
  const safeDownloadName = sanitizeArtifactDownloadName(downloadName);

  return (
    <a
      {...props}
      href={artifactDownloadHref(href)}
      download={safeDownloadName || true}
      rel="noopener"
    >
      {children}
    </a>
  );
}
