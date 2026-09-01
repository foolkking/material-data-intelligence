import React from "react";
import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";

const push = vi.fn();
const prefetch = vi.fn();
const navigation = vi.hoisted(() => ({
  pathname: "/projects/project-1/research",
  search: "",
}));

vi.mock("next/navigation", () => ({
  usePathname: () => navigation.pathname,
  useRouter: () => ({ push, replace: vi.fn(), prefetch }),
  useSearchParams: () => new URLSearchParams(navigation.search),
}));
vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    onClick,
    prefetch,
    ...props
  }: {
    children: React.ReactNode;
    href: string;
    onClick?: React.MouseEventHandler<HTMLAnchorElement>;
    prefetch?: boolean | null;
  }) => (
    <a
      href={href}
      {...props}
      data-prefetch={prefetch === true ? "true" : prefetch === false ? "false" : "default"}
      onClick={(event) => {
        onClick?.(event);
        event.preventDefault();
      }}
    >
      {children}
    </a>
  ),
}));

import { RouteTransitionProgress } from "./RouteTransitionProgress";
import {
  ProductLink,
  ProductNavigationProvider,
  resolveClientNavigationTarget,
  useProductNavigation,
} from "./ProductNavigation";

function NavigationState() {
  const state = useProductNavigation();
  return <output data-testid="navigation-target">{state?.intent?.targetKey || ""}</output>;
}

beforeEach(() => {
  vi.useFakeTimers();
  push.mockReset();
  prefetch.mockReset();
  navigation.pathname = "/projects/project-1/research";
  navigation.search = "";
  window.history.replaceState({}, "", navigation.pathname);
  document.body.innerHTML = "";
});

afterEach(() => {
  vi.useRealTimers();
});

it("shows progress only after a slow same-origin navigation and clears after query-only commits", () => {
  const { rerender } = render(
    <ProductNavigationProvider>
      <RouteTransitionProgress />
      <ProductLink href="/projects/project-1/research?turn=turn-2">打开研究结果</ProductLink>
    </ProductNavigationProvider>,
  );

  fireEvent.click(screen.getByRole("link", { name: "打开研究结果" }));
  expect(push).not.toHaveBeenCalled();
  expect(screen.queryByRole("status")).toBeNull();
  act(() => vi.advanceTimersByTime(120));
  expect(screen.getByRole("status")).toHaveTextContent("正在切换工作区");

  navigation.search = "turn=turn-2";
  window.history.replaceState({}, "", `${navigation.pathname}?${navigation.search}`);
  rerender(
    <ProductNavigationProvider>
      <RouteTransitionProgress />
      <ProductLink href="/projects/project-1/research?turn=turn-2">打开研究结果</ProductLink>
    </ProductNavigationProvider>,
  );
  expect(screen.queryByRole("status")).toBeNull();
});

it("does not flash progress when the route commits within the delay", () => {
  const { rerender } = render(
    <ProductNavigationProvider>
      <RouteTransitionProgress />
      <ProductLink href="/projects/project-1/data">打开数据</ProductLink>
    </ProductNavigationProvider>,
  );

  fireEvent.click(screen.getByRole("link", { name: "打开数据" }));
  navigation.pathname = "/projects/project-1/data";
  window.history.replaceState({}, "", navigation.pathname);
  rerender(
    <ProductNavigationProvider>
      <RouteTransitionProgress />
      <ProductLink href="/projects/project-1/data">打开数据</ProductLink>
    </ProductNavigationProvider>,
  );
  act(() => vi.advanceTimersByTime(250));
  expect(screen.queryByRole("status")).toBeNull();
});

it("clears the pending target as soon as the committed route matches", () => {
  const { rerender } = render(
    <ProductNavigationProvider>
      <RouteTransitionProgress />
      <NavigationState />
      <ProductLink href="/projects/project-1/data">打开数据</ProductLink>
    </ProductNavigationProvider>,
  );

  fireEvent.click(screen.getByRole("link", { name: "打开数据" }));
  expect(screen.getByTestId("navigation-target")).toHaveTextContent("/projects/project-1/data");

  navigation.pathname = "/projects/project-1/data";
  window.history.replaceState({}, "", navigation.pathname);
  rerender(
    <ProductNavigationProvider>
      <RouteTransitionProgress />
      <NavigationState />
      <ProductLink href="/projects/project-1/data">打开数据</ProductLink>
    </ProductNavigationProvider>,
  );

  expect(screen.getByTestId("navigation-target")).toBeEmptyDOMElement();
});

it("ignores API links and disabled links", () => {
  render(
    <ProductNavigationProvider>
      <RouteTransitionProgress />
      <ProductLink href="/api/search?q=band" onClick={(event) => event.preventDefault()}>API</ProductLink>
      <ProductLink href="/projects/project-1/data" aria-disabled onClick={(event) => event.preventDefault()}>禁用</ProductLink>
    </ProductNavigationProvider>,
  );

  fireEvent.click(screen.getByRole("link", { name: "API" }));
  expect(screen.queryByRole("status")).toBeNull();
  fireEvent.click(screen.getByRole("link", { name: "禁用" }));
  expect(screen.queryByRole("status")).toBeNull();
  expect(push).not.toHaveBeenCalled();
});

it("keeps external, API, and same-document anchors out of client routing", () => {
  const current = "http://127.0.0.1:3000/projects/project-1/data";
  expect(resolveClientNavigationTarget("https://example.com", current)).toBeNull();
  expect(resolveClientNavigationTarget("/api/projects", current)).toBeNull();
  expect(resolveClientNavigationTarget("#table", current)).toBeNull();
  expect(resolveClientNavigationTarget("/projects/project-1/research", current)).toBe(
    "/projects/project-1/research",
  );
});

it("leaves dense links at framework-default prefetch unless a primary link opts in", () => {
  render(
    <ProductNavigationProvider>
      <ProductLink href="/projects/project-1/data">数据</ProductLink>
      <ProductLink href="/projects/project-1/research" prefetch>主要研究导航</ProductLink>
      <ProductLink href="/api/projects">API</ProductLink>
      <ProductLink href="https://example.com">外部</ProductLink>
    </ProductNavigationProvider>,
  );

  expect(screen.getByRole("link", { name: "数据" })).toHaveAttribute("data-prefetch", "default");
  expect(screen.getByRole("link", { name: "主要研究导航" })).toHaveAttribute("data-prefetch", "true");
  expect(screen.getByRole("link", { name: "API" })).toHaveAttribute("data-prefetch", "default");
  expect(screen.getByRole("link", { name: "外部" })).toHaveAttribute("data-prefetch", "default");
});

it("coalesces pointer and keyboard prefetch for the same internal route", () => {
  render(
    <ProductNavigationProvider>
      <ProductLink href="/projects/project-1/data">数据</ProductLink>
      <ProductLink href="/api/projects">API</ProductLink>
    </ProductNavigationProvider>,
  );

  fireEvent.mouseEnter(screen.getByRole("link", { name: "数据" }));
  fireEvent.focus(screen.getByRole("link", { name: "数据" }));
  fireEvent.mouseEnter(screen.getByRole("link", { name: "API" }));

  expect(prefetch).toHaveBeenCalledWith("/projects/project-1/data");
  expect(prefetch).toHaveBeenCalledTimes(1);

  act(() => vi.advanceTimersByTime(1_500));
  fireEvent.focus(screen.getByRole("link", { name: "数据" }));
  expect(prefetch).toHaveBeenCalledTimes(2);
});
