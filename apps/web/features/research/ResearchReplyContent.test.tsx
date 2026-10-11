import { fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { ResearchReplyContent } from "./ResearchReplyContent";

it("renders the saved density ranking as readable paragraphs and an ordered list", () => {
  const text = "三个合成晶体按数密度排序：\n\n1. **NaCl_derived.cif** — 0.043419 Å⁻³\n2. **Si_diamond_synthetic.cif** — 0.049968 Å⁻³\n3. **Cu_fcc_synthetic.cif** — 0.085023 Å⁻³\n\n来源：已保存的 RDF 结果 result_1。";
  const { container } = render(<ResearchReplyContent text={text} />);
  expect(within(screen.getByRole("list")).getAllByRole("listitem").map(item => item.textContent)).toEqual([
    "NaCl_derived.cif — 0.043419 Å⁻³",
    "Si_diamond_synthetic.cif — 0.049968 Å⁻³",
    "Cu_fcc_synthetic.cif — 0.085023 Å⁻³",
  ]);
  expect(screen.getByText("NaCl_derived.cif").tagName).toBe("STRONG");
  expect(container.querySelectorAll("p")).toHaveLength(2);
});

it("repairs incomplete formatting only while streaming and settles to the saved Markdown", () => {
  const { rerender } = render(<ResearchReplyContent text={"1. **NaCl"} streaming />);
  expect(screen.getByText("NaCl").tagName).toBe("STRONG");
  const complete = "1. **NaCl_derived.cif** — 0.043419 Å⁻³\n2. **Si_diamond_synthetic.cif** — 0.049968 Å⁻³";
  rerender(<ResearchReplyContent text={complete} streaming />);
  expect(screen.getAllByRole("listitem")).toHaveLength(2);
  rerender(<ResearchReplyContent text={complete} />);
  expect(screen.getByText("NaCl_derived.cif").tagName).toBe("STRONG");
  expect(screen.queryByText("**NaCl_derived.cif**")).toBeNull();
  rerender(<ResearchReplyContent text="最终原文有 **未闭合" />);
  expect(screen.getByText("最终原文有 **未闭合")).toBeVisible();
});

it("renders GFM tables in an independently focusable region", () => {
  render(<ResearchReplyContent text={"## 密度\n\n| 材料 | 数密度 / Å⁻³ |\n| --- | --- |\n| NaCl | 0.043419 |\n| Si | 0.049968 |"} />);
  expect(screen.getByRole("heading", { name: "密度" })).toBeVisible();
  const region = screen.getByRole("region", { name: "回答表格" });
  expect(region).toHaveAttribute("tabindex", "0");
  expect(within(region).getByRole("cell", { name: "0.043419" })).toBeVisible();
  expect(within(region).getAllByRole("row")).toHaveLength(3);
});

it("renders scientific math and code without changing formulas or requesting external assets", () => {
  const { container } = render(<ResearchReplyContent text={"$\\rho = 0.043419\\,\\mathrm{\\AA}^{-3}$\n\n`E**2 + v**2` 和 Si_diamond_synthetic.cif\n\n![远程图](https://example.invalid/private)"} />);
  expect(container.querySelector("math")).not.toBeNull();
  expect(container.querySelector("annotation")?.textContent).toBe("\\rho = 0.043419\\,\\mathrm{\\AA}^{-3}");
  expect(container.querySelector("code")?.textContent).toBe("E**2 + v**2");
  expect(container.textContent).toContain("Si_diamond_synthetic.cif");
  expect(container.querySelector("img")).toBeNull();
});

it("renders parenthesized and bracketed LaTeX alongside dollar formulas", () => {
  const { container } = render(<ResearchReplyContent text={String.raw`行内 \(g(r)=\frac{n(r)}{4\pi r^2\rho\Delta r}\)。

\[
N=4\pi\rho\int_0^{r_c}g(r)r^2\,dr
\]

1. **密度**：\(\rho=0.043419\,\mathrm{\AA}^{-3}\)
2. $r_c=5$`} />);
  const formulas = Array.from(container.querySelectorAll("annotation")).map(node => node.textContent?.trim());
  expect(formulas).toEqual([
    String.raw`g(r)=\frac{n(r)}{4\pi r^2\rho\Delta r}`,
    String.raw`N=4\pi\rho\int_0^{r_c}g(r)r^2\,dr`,
    String.raw`\rho=0.043419\,\mathrm{\AA}^{-3}`,
    "r_c=5",
  ]);
  expect(container.querySelectorAll(".katex-display")).toHaveLength(1);
  expect(screen.getAllByRole("listitem")).toHaveLength(2);
});

it("preserves LaTeX examples in code, escaped text and link destinations", () => {
  const literal = String.raw`\(r\) and \[\rho\]`;
  const text = "```latex\n" + literal + "\n```\n\n`" + literal + "`\n\n" +
    String.raw`\\(not math\\) and \\[literal\\]` + "\n\n" + String.raw`[source](https://example.invalid/\(path\))`;
  const { container } = render(<ResearchReplyContent text={text} streaming />);
  expect(container.querySelector("math")).toBeNull();
  expect(Array.from(container.querySelectorAll("code")).map(node => node.textContent)).toEqual([literal + "\n", literal]);
  expect(container.textContent).toContain(String.raw`\(not math\) and \[literal\]`);
  expect(screen.getByRole("link", { name: "source" })).toHaveAttribute("href", "https://example.invalid/(path)");
});

it("retains matrix row separators inside display math", () => {
  const body = String.raw`\begin{pmatrix}1 & 2 \\ 3 & 4\end{pmatrix}`;
  const { container } = render(<ResearchReplyContent text={"\\[" + body + "\\]"} />);
  expect(container.querySelector("annotation")?.textContent).toBe(body);
  expect(container.querySelector(".katex-error")).toBeNull();
  expect(container.querySelector(".katex-display")).not.toBeNull();
});

it("does not let an unclosed opener swallow the next complete formula", () => {
  const { container } = render(<ResearchReplyContent text={String.raw`前缀 \(未闭合，后面是 \(g(r)\)。`} />);
  expect(container.querySelectorAll("math")).toHaveLength(1);
  expect(container.querySelector("annotation")?.textContent).toBe("g(r)");
  expect(container.textContent).toContain("前缀 (未闭合，后面是");
});

it("renders a backslash formula when its closing delimiter arrives and preserves the completed value", () => {
  const { container, rerender } = render(<ResearchReplyContent text={String.raw`密度 \(\rho=0.043`} streaming />);
  expect(container.querySelector("math")).toBeNull();
  expect(container.textContent).toContain("0.043");
  const completed = String.raw`密度 \(\rho=0.043419\)`;
  rerender(<ResearchReplyContent text={completed} streaming />);
  expect(container.querySelector("annotation")?.textContent).toBe(String.raw`\rho=0.043419`);
  rerender(<ResearchReplyContent text={completed} />);
  expect(container.querySelectorAll("math")).toHaveLength(1);
  expect(container.querySelector("annotation")?.textContent).toBe(String.raw`\rho=0.043419`);
});

it("keeps backslash math under the same untrusted KaTeX policy", () => {
  const { container } = render(<ResearchReplyContent text={String.raw`\(\href{javascript:alert(1)}{x}\) \[\includegraphics{https://example.invalid/private}\]`} />);
  expect(container.querySelector("a,img,script,iframe")).toBeNull();
});

it("does not make incomplete, dangerous or credential-bearing URLs clickable", () => {
  const { rerender, container } = render(<ResearchReplyContent text="[来源](https://exampl" streaming />);
  expect(screen.queryByRole("link")).toBeNull();
  rerender(<ResearchReplyContent text={'<script>alert(1)</script>\n\n<img src="https://example.invalid/collect" onerror="alert(1)">\n\n[危险](javascript:alert(1)) [本地](file:///C:/secret) [凭据](https://user:password@example.invalid)'} />);
  expect(container.querySelector("script,img,iframe,svg,a")).toBeNull();
  rerender(<ResearchReplyContent text="[公开文献](https://example.invalid/paper)" />);
  expect(screen.getByRole("link", { name: "公开文献" })).toHaveAttribute("rel", "noopener noreferrer");
});

it("renders fenced source literally and copies the current code only", async () => {
  const writeText = vi.fn().mockResolvedValue(undefined);
  const original = Object.getOwnPropertyDescriptor(navigator, "clipboard");
  Object.defineProperty(navigator, "clipboard", { configurable: true, value: { writeText } });
  try {
    const { container } = render(<ResearchReplyContent text={'```text\nE**2 + v**2\n<script>example</script>\n```'} />);
    expect(screen.getByLabelText("代码块")).toHaveTextContent("E**2 + v**2");
    expect(container.querySelector("script,strong")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "复制代码" }));
    await screen.findByText("已复制");
    expect(writeText).toHaveBeenCalledWith("E**2 + v**2\n<script>example</script>\n");
  } finally {
    if (original) Object.defineProperty(navigator, "clipboard", original);
    else Reflect.deleteProperty(navigator, "clipboard");
  }
});

it("keeps an oversized response complete without unbounded Markdown processing", () => {
  const text = "**" + "完整原文".repeat(9000) + "**\n末尾";
  const { container } = render(<ResearchReplyContent text={text} streaming />);
  expect(container.textContent).toBe(text);
  expect(container.querySelector("strong")).toBeNull();
});

it.each([false, true])("localizes scientific prose while preserving literal Markdown data (streaming: %s)", streaming => {
  const limitation = "The result projector does not infer peaks or coordination shells from the RDF curve.";
  const code = '{"statistics_authority":"computed_from_payload","value":0.0499677265116949}';
  const text = `${limitation}\n\nstatistics_authority：computed_from_payload\n\n\`ScientificResult\`\n\n\`\`\`json\n${code}\n\`\`\`\n\n[ScientificResult](https://example.invalid/ScientificResult)\n\n$\\mathrm{ScientificResult}$`;
  const { container, rerender } = render(<ResearchReplyContent text={text} scientific streaming={streaming} />);
  expect(screen.getByText("不据 RDF 曲线推断峰位或配位壳层。")).toBeVisible();
  expect(screen.getByText("统计依据：由保存的场数据计算")).toBeVisible();
  expect(container.querySelector("pre code")?.textContent).toBe(code + "\n");
  expect(screen.getByRole("link", { name: "ScientificResult" })).toHaveAttribute("href", "https://example.invalid/ScientificResult");
  expect(container.querySelector("annotation")?.textContent).toBe("\\mathrm{ScientificResult}");
  rerender(<ResearchReplyContent text={limitation} />);
  expect(screen.getByText(limitation)).toBeVisible();
});

it("keeps the code visible and offers retry when clipboard access is unavailable", async () => {
  const original = Object.getOwnPropertyDescriptor(navigator, "clipboard");
  Object.defineProperty(navigator, "clipboard", { configurable: true, value: undefined });
  try {
    render(<ResearchReplyContent text={'```text\n完整代码\n```'} />);
    fireEvent.click(screen.getByRole("button", { name: "复制代码" }));
    expect(await screen.findByText("重试复制")).toBeVisible();
    expect(screen.getByLabelText("代码块")).toHaveTextContent("完整代码");
  } finally {
    if (original) Object.defineProperty(navigator, "clipboard", original);
    else Reflect.deleteProperty(navigator, "clipboard");
  }
});
