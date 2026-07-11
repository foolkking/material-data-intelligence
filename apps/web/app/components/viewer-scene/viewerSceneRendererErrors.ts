export type ViewerRendererErrorCode =
  | "VIEWER_RENDERER_UNSUPPORTED"
  | "VIEWER_RENDERER_VALIDATION_FAILED"
  | "VIEWER_RENDERER_INITIALIZATION_FAILED"
  | "VIEWER_RENDERER_CONTEXT_LOST"
  | "VIEWER_RENDERER_INVALID_GEOMETRY"
  | "VIEWER_RENDERER_RESOURCE_LIMIT"
  | "VIEWER_RENDERER_DISPOSE_FAILED";

export class ViewerRendererError extends Error {
  readonly code: ViewerRendererErrorCode;

  constructor(code: ViewerRendererErrorCode, message: string) {
    super(message);
    this.name = "ViewerRendererError";
    this.code = code;
  }
}
