import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { StrictMode } from "react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  getAuthUser: vi.fn(),
  login: vi.fn(),
  logout: vi.fn(),
  replace: vi.fn(),
}));

vi.mock("../../shared/layout/ProductNavigation", () => ({
  ProductLink: ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode;
    href: string;
  }) => <a href={href} {...props}>{children}</a>,
  useProductRouter: () => ({ replace: mocks.replace }),
}));

vi.mock("../lib/product-api", () => ({
  getAuthUser: mocks.getAuthUser,
  login: mocks.login,
  logout: mocks.logout,
}));

import { LandingPage, safeProductReturnTo } from "./LandingPage";

afterEach(() => vi.useRealTimers());

beforeEach(() => {
  vi.clearAllMocks();
  window.history.replaceState({}, "", "/");
  mocks.getAuthUser.mockRejectedValue(new Error("unauthenticated"));
  mocks.login.mockResolvedValue({
    id: "user_1",
    displayName: "验收研究员",
    email: "acceptance.researcher@local.invalid",
  });
});

it("explains an expired session and returns to the exact authorized product URL after login", async () => {
  const returnTo =
    "/projects/project_1/research?session=session_1&turn=turn_1#evidence-result_1";
  window.history.replaceState(
    {},
    "",
    `/?login=1&reason=session-expired&returnTo=${encodeURIComponent(returnTo)}`,
  );
  window.sessionStorage.setItem(
    "mdi:research-composer-draft:project_1:session_1:turn_1",
    "保留这段草稿",
  );
  const user = userEvent.setup();
  render(<LandingPage />);

  expect(
    await screen.findByRole("heading", { name: "登录已过期" }),
  ).toBeInTheDocument();
  expect(
    screen.getByText(/尚未提交的研究草稿会保留/),
  ).toBeInTheDocument();
  const dialog = screen.getByRole("dialog", { name: "登录已过期" });

  await user.type(within(dialog).getByLabelText("邮箱"), "researcher@example.test");
  await user.type(within(dialog).getByLabelText("密码"), "not-stored-by-the-client");
  await user.click(within(dialog).getByRole("button", { name: "登录" }));

  await waitFor(() => expect(mocks.replace).toHaveBeenCalledWith(returnTo));
  expect(
    window.sessionStorage.getItem(
      "mdi:research-composer-draft:project_1:session_1:turn_1",
    ),
  ).toBe("保留这段草稿");
});

it("fails closed for external or ambiguous return URLs", () => {
  expect(safeProductReturnTo("https://attacker.invalid/project")).toBeNull();
  expect(safeProductReturnTo("//attacker.invalid/project")).toBeNull();
  expect(safeProductReturnTo("/projects\\attacker.invalid")).toBeNull();
  expect(
    safeProductReturnTo("/projects/project_1/research?turn=turn_1#result"),
  ).toBe("/projects/project_1/research?turn=turn_1#result");
});

it("keeps failed reauthentication on the login surface without losing the return target", async () => {
  const returnTo = "/projects/project_1/data?object=object_1#source";
  window.history.replaceState(
    {},
    "",
    `/?login=1&reason=session-expired&returnTo=${encodeURIComponent(returnTo)}`,
  );
  mocks.login.mockRejectedValue(new Error("登录凭据无效"));
  render(<LandingPage />);

  fireEvent.change(await screen.findByLabelText("邮箱"), {
    target: { value: "researcher@example.test" },
  });
  fireEvent.change(screen.getByLabelText("密码"), {
    target: { value: "wrong-password" },
  });
  const dialog = screen.getByRole("dialog", { name: "登录已过期" });
  fireEvent.submit(within(dialog).getByRole("button", { name: "登录" }).closest("form")!);

  expect(await screen.findByRole("alert")).toHaveTextContent("登录凭据无效");
  expect(mocks.replace).not.toHaveBeenCalled();
  expect(window.location.search).toContain(encodeURIComponent(returnTo));
});

it.each(["Escape", "close button", "backdrop"])("restores scrolling and the opener after dismissal by %s", async (dismissal) => {
  const user = userEvent.setup();
  const bodyOverflow = document.body.style.overflow;
  const rootOverflow = document.documentElement.style.overflow;
  document.body.style.overflow = "auto";
  document.documentElement.style.overflow = "scroll";
  const view = render(<StrictMode><LandingPage /></StrictMode>);
  try {
    const opener = screen.getByRole("button", { name: "登录并开始" });
    const background = screen.getByRole("button", { name: "登录" }).closest("header")!;
    const previouslyInert = screen.getByRole("region", { name: "工作方式" });
    previouslyInert.setAttribute("inert", "");
    await user.click(opener);
    const dialog = await screen.findByRole("dialog", { name: "登录" });
    expect(within(dialog).getByLabelText("邮箱")).toHaveFocus();
    expect(background).toHaveAttribute("inert");
    expect(document.body.style.overflow).toBe("hidden");
    expect(document.documentElement.style.overflow).toBe("hidden");

    if (dismissal === "Escape") await user.keyboard("{Escape}");
    else if (dismissal === "close button") await user.click(within(dialog).getByRole("button", { name: "关闭登录窗口" }));
    else fireEvent.mouseDown(dialog.parentElement!);

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    await waitFor(() => expect(opener).toHaveFocus());
    expect(background).not.toHaveAttribute("inert");
    expect(previouslyInert).toHaveAttribute("inert");
    expect(document.body.style.overflow).toBe("auto");
    expect(document.documentElement.style.overflow).toBe("scroll");
  } finally {
    view.unmount();
    document.body.style.overflow = bodyOverflow;
    document.documentElement.style.overflow = rootOverflow;
  }
});

it("keeps keyboard navigation inside the login dialog in both directions", async () => {
  const user = userEvent.setup();
  render(<StrictMode><LandingPage /></StrictMode>);
  await user.click(screen.getByRole("button", { name: "开始使用" }));
  const dialog = screen.getByRole("dialog");
  const close = within(dialog).getByRole("button", { name: "关闭登录窗口" });
  const submit = within(dialog).getByRole("button", { name: "登录" });
  await user.tab({ shift: true });
  expect(close).toHaveFocus();
  await user.tab({ shift: true });
  expect(submit).toHaveFocus();
  await user.tab();
  expect(close).toHaveFocus();
  await user.tab();
  expect(within(dialog).getByLabelText("邮箱")).toHaveFocus();
});

it("does not steal input focus when the initial account read settles", async () => {
  let resolveProfile!: (value: unknown) => void;
  mocks.getAuthUser.mockImplementation(() => new Promise((resolve) => { resolveProfile = resolve; }));
  const user = userEvent.setup();
  render(<LandingPage />);
  await user.click(screen.getByRole("button", { name: "开始使用" }));
  const email = screen.getByLabelText("邮箱");
  const password = screen.getByLabelText("密码");
  await user.type(email, "researcher@example.test");
  await user.click(password);
  await act(async () => resolveProfile({ id: "user_1", displayName: "研究员" }));
  expect(password).toHaveFocus();
  expect(email).toHaveValue("researcher@example.test");
  expect(document.body.style.overflow).toBe("hidden");
});

function prepareLoginForm() {
  window.history.replaceState({}, "", "/?login=1&returnTo=%2Fprojects%2Fproject_1%2Fresearch%3Fturn%3Dturn_1");
  const view = render(<LandingPage />);
  fireEvent.change(screen.getByLabelText("邮箱"), { target: { value: "researcher@example.test" } });
  fireEvent.change(screen.getByLabelText("密码"), { target: { value: "test-password-only" } });
  const form = screen.getByRole("dialog").querySelector("form")!;
  return { ...view, form };
}

it("admits one pending login even when the form submits twice before a render", async () => {
  mocks.login.mockReturnValue(new Promise(() => {}));
  const view = prepareLoginForm();
  await act(async () => {
    fireEvent.submit(view.form);
    fireEvent.submit(view.form);
  });
  expect(mocks.login).toHaveBeenCalledTimes(1);
  expect(screen.getByLabelText("邮箱")).toHaveAttribute("readonly");
  expect(screen.getByLabelText("密码")).toHaveAttribute("readonly");
  expect(screen.getByRole("button", { name: "正在登录…" })).toBeDisabled();
  view.unmount();
  await act(async () => {});
});

it("times out visibly, retains input, and ignores the old reply while a retry is pending", async () => {
  vi.useFakeTimers();
  let oldReply!: (value: unknown) => void;
  let retryReply!: (value: unknown) => void;
  mocks.login.mockReturnValueOnce(new Promise(resolve => { oldReply = resolve; }))
    .mockReturnValueOnce(new Promise(resolve => { retryReply = resolve; }));
  const view = prepareLoginForm();
  await act(async () => { fireEvent.submit(view.form); });
  await act(async () => { await vi.advanceTimersByTimeAsync(10_000); });
  expect(screen.getByRole("alert")).toHaveTextContent("登录响应超时，请重试。");
  expect(screen.getByRole("alert")).toHaveFocus();
  expect(screen.getByLabelText("邮箱")).toHaveValue("researcher@example.test");
  expect(screen.getByLabelText("密码")).toHaveValue("test-password-only");
  expect(mocks.login.mock.calls[0][2].signal.aborted).toBe(true);
  expect(within(screen.getByRole("dialog")).getByRole("button", { name: "登录" })).toBeEnabled();
  await act(async () => { fireEvent.submit(view.form); });
  await act(async () => { oldReply({ id: "old-user", displayName: "迟到的账户" }); });
  expect(mocks.replace).not.toHaveBeenCalled();
  expect(screen.getByRole("button", { name: "正在登录…" })).toBeDisabled();
  await act(async () => { retryReply({ id: "new-user", displayName: "当前账户" }); });
  expect(mocks.replace).toHaveBeenCalledTimes(1);
  expect(mocks.replace).toHaveBeenCalledWith("/projects/project_1/research?turn=turn_1");
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
});

it.each(["Escape", "close button", "backdrop", "unmount"])("abandons a pending login on %s without a late redirect", async dismissal => {
  let reply!: (value: unknown) => void;
  mocks.login.mockReturnValue(new Promise(resolve => { reply = resolve; }));
  const view = prepareLoginForm();
  await act(async () => { fireEvent.submit(view.form); });
  const dialog = screen.getByRole("dialog");
  if (dismissal === "Escape") fireEvent.keyDown(document, { key: "Escape" });
  else if (dismissal === "close button") fireEvent.click(within(dialog).getByRole("button", { name: "关闭登录窗口" }));
  else if (dismissal === "backdrop") fireEvent.mouseDown(dialog.parentElement!);
  else view.unmount();
  await act(async () => {});
  expect(mocks.login.mock.calls[0][2].signal.aborted).toBe(true);
  if (dismissal !== "unmount") {
    fireEvent.click(screen.getByRole("button", { name: "开始使用" }));
    expect(screen.getByLabelText("密码")).toHaveValue("");
  }
  await act(async () => { reply({ id: "late-user", displayName: "迟到的账户" }); });
  expect(mocks.replace).not.toHaveBeenCalled();
  if (dismissal !== "unmount") expect(screen.getByRole("dialog")).toBeInTheDocument();
});
