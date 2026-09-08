import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

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
