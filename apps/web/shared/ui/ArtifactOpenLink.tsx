import type { AnchorHTMLAttributes, ReactNode } from "react";

const ARTIFACT_CONTENT_PATH =
  /^\/api\/planner\/jobs\/[^/?#]+\/artifacts\/[^/?#]+\/content(?:\?[^#]*)?$/u;

export function isTrustedArtifactContentHref(href: string): boolean {
  return ARTIFACT_CONTENT_PATH.test(href);
}

export function ArtifactOpenLink({
  href,
  children,
  ...props
}: Readonly<{
  href: string;
  children: ReactNode;
}> &
  Omit<
    AnchorHTMLAttributes<HTMLAnchorElement>,
    "children" | "href" | "rel" | "target"
  >) {
  if (!isTrustedArtifactContentHref(href)) return null;

  return (
    <a
      {...props}
      href={href}
      target="_blank"
      rel="noopener noreferrer"
    >
      {children}
    </a>
  );
}
