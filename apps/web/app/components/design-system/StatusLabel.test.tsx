import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StatusLabel } from "./StatusLabel";

describe("StatusLabel", () => {
  it("retains the supplied label and exposes a presentation-only semantic variant", () => {
    render(<StatusLabel label="PARTIAL" variant="partial" testId="status" />);
    const status = screen.getByTestId("status");
    expect(status).toHaveTextContent("PARTIAL");
    expect(status).toHaveAttribute("data-status", "partial");
    expect(status).toHaveClass("ds-status");
  });
});
