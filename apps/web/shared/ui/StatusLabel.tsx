export type StatusVariant =
  | "neutral"
  | "info"
  | "progress"
  | "success"
  | "partial"
  | "warning"
  | "danger"
  | "unsupported"
  | "stale"
  | "read-only";

type StatusLabelProps = Readonly<{
  label: string;
  variant: StatusVariant;
  className?: string;
  testId?: string;
}>;

/** Presentation-only status primitive. The caller retains domain-state authority. */
export function StatusLabel({ label, variant, className = "", testId }: StatusLabelProps) {
  return (
    <span className={`ds-status ${className}`.trim()} data-status={variant} data-testid={testId}>
      {label}
    </span>
  );
}
