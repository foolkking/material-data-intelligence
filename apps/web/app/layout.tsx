import "./globals.css";
import type { ReactNode } from "react";
import type { Viewport } from "next";
import { ProductNavigationProvider } from "../shared/layout/ProductNavigation";
import { ProductRouteFrame } from "../shared/layout/ProductRouteFrame";
import { RouteTransitionProgress } from "../shared/layout/RouteTransitionProgress";
import { ClientObservability } from "../shared/observability/ClientObservability";

export const metadata = {
  title: "Material Data Intelligence",
  description: "材料数据、科学分析与可追溯研究结果"
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        <ClientObservability
          releaseSha={process.env.MDI_RELEASE_SHA || process.env.GITHUB_SHA}
        />
        <ProductNavigationProvider>
          <RouteTransitionProgress />
          <ProductRouteFrame>{children}</ProductRouteFrame>
        </ProductNavigationProvider>
      </body>
    </html>
  );
}
