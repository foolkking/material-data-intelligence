import type { ReactNode } from "react";

export default function ProjectsLayout({ children }: Readonly<{ children: ReactNode }>) {
  // RootLayout owns the persistent authenticated ProductRouteFrame. Keeping
  // a second client frame here duplicates route/auth lifecycle work on every
  // project transition even though ProductShell later short-circuits it.
  return children;
}
