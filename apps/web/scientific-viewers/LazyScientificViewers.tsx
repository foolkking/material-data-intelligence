"use client";

import dynamic from "next/dynamic";

function ViewerLoading({ label }: Readonly<{ label: string }>) {
  return (
    <div className="scientific-viewer-deferred-loading" role="status" aria-live="polite">
      <span aria-hidden="true" />
      <div>
        <strong>{label}</strong>
        <small>正在读取已持久化科学数据，不会重新执行分析。</small>
      </div>
    </div>
  );
}

export const LazyScientificResultViewer = dynamic(
  () =>
    import("./ScientificViewerAdapter").then(
      (module) => module.ScientificResultViewer,
    ),
  {
    ssr: false,
    loading: () => <ViewerLoading label="正在打开科学结果" />,
  },
);

export const LazyScientificSourceViewer = dynamic(
  () =>
    import("./ScientificViewerAdapter").then(
      (module) => module.ScientificSourceViewer,
    ),
  {
    ssr: false,
    loading: () => <ViewerLoading label="正在打开科学数据" />,
  },
);

export const LazyScientificObjectViewer = dynamic(
  () =>
    import("./scientific-viewer/ScientificObjectViewer").then(
      (module) => module.ScientificObjectViewer,
    ),
  {
    ssr: false,
    loading: () => <ViewerLoading label="正在解析精确对象版本" />,
  },
);
