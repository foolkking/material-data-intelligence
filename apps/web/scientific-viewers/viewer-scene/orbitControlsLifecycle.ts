type OrbitControlsInternals = Readonly<{
  domElement?: Readonly<{ getRootNode?: () => EventTarget }>;
  _interceptControlDown?: EventListener;
}>;

export function captureOrbitControlsDisposer(controls: Readonly<{ dispose: () => void }>): () => void {
  const internals = controls as OrbitControlsInternals;
  const connectedRoot = internals.domElement?.getRootNode?.();
  const keyInterceptor = internals._interceptControlDown;
  let disposed = false;

  return () => {
    if (disposed) return;
    disposed = true;
    if (connectedRoot && keyInterceptor) connectedRoot.removeEventListener("keydown", keyInterceptor, { capture: true });
    controls.dispose();
  };
}
