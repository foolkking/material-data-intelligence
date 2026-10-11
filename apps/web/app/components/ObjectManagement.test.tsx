import React, { StrictMode, useState } from "react";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import { ManagedObjectRow, ProductModal } from "./ObjectManagement";

function Example() {
  const [open, setOpen] = useState(false);
  return <><button onClick={() => setOpen(true)}>编辑设置</button>{open ? <ProductModal title="设置" onClose={() => setOpen(false)} footer={<button onClick={() => setOpen(false)}>完成</button>}><label>名称<input /></label></ProductModal> : null}</>;
}

it("keeps focus inside a Strict Mode dialog and restores its original trigger after close", async () => {
  const user = userEvent.setup();
  render(<StrictMode><Example /></StrictMode>);
  const trigger = screen.getByRole("button", { name: "编辑设置" });
  await user.click(trigger);
  const field = screen.getByRole("textbox", { name: "名称" });
  await waitFor(() => expect(field).toHaveFocus());
  // Allow the effect replay's animation frame to run before checking again.
  await new Promise((resolve) => requestAnimationFrame(resolve));
  expect(field).toHaveFocus();
  await user.keyboard("{Escape}");
  await waitFor(() => expect(trigger).toHaveFocus());
  expect(screen.queryByRole("dialog")).toBeNull();
  await user.click(trigger);
  await user.click(screen.getByRole("button", { name: "完成" }));
  await waitFor(() => expect(trigger).toHaveFocus());
});

it("closes a row menu before its surrounding panel and returns focus to the menu trigger", async () => {
  const user = userEvent.setup();
  const outerEscape = vi.fn();
  document.addEventListener("keydown", outerEscape);
  try {
    render(<ManagedObjectRow href="#sample" title="材料分析" description="可继续" actions={[{ label: "重命名", onSelect: vi.fn() }]} />);
    const trigger = screen.getByRole("button", { name: "管理 材料分析" });
    await user.click(trigger);
    expect(screen.getByRole("menuitem", { name: "重命名" })).toHaveFocus();
    await user.keyboard("{Escape}");
    await waitFor(() => expect(trigger).toHaveFocus());
    expect(screen.queryByRole("menu")).toBeNull();
    expect(outerEscape).not.toHaveBeenCalled();
    await user.keyboard("{Escape}");
    expect(outerEscape).toHaveBeenCalledTimes(1);
  } finally {
    document.removeEventListener("keydown", outerEscape);
  }
});

it("does not move focus away from a new input after closing a dialog", async () => {
  const frames: FrameRequestCallback[] = [];
  const frame = vi.spyOn(window, "requestAnimationFrame").mockImplementation(callback => { frames.push(callback); return frames.length; });
  try {
    render(<><Example /><label>研究问题<textarea /></label></>);
    const trigger = screen.getByRole("button", { name: "编辑设置" });
    trigger.focus();
    fireEvent.click(trigger);
    expect(screen.getByRole("textbox", { name: "名称" })).toHaveFocus();
    fireEvent.keyDown(document, { key: "Escape" });
    const composer = screen.getByRole("textbox", { name: "研究问题" });
    composer.focus();
    await act(async () => frames.forEach(callback => callback(0)));
    expect(composer).toHaveFocus();
  } finally { frame.mockRestore(); }
});

it("does not return focus to a row menu after another control receives it", async () => {
  const frames: FrameRequestCallback[] = [];
  const frame = vi.spyOn(window, "requestAnimationFrame").mockImplementation(callback => { frames.push(callback); return frames.length; });
  try {
    render(<><ManagedObjectRow href="#sample" title="材料" description="" actions={[{ label: "重命名", onSelect: vi.fn() }]} /><label>搜索<input /></label></>);
    const trigger = screen.getByRole("button", { name: "管理 材料" });
    trigger.focus();
    fireEvent.click(trigger);
    fireEvent.keyDown(document, { key: "Escape" });
    const search = screen.getByRole("textbox", { name: "搜索" });
    search.focus();
    await act(async () => frames.forEach(callback => callback(0)));
    expect(search).toHaveFocus();
  } finally { frame.mockRestore(); }
});

it("skips disabled actions when entering and navigating a row menu", async () => {
  const user = userEvent.setup();
  render(<ManagedObjectRow href="#sample" title="报告" description="" actions={[
    { label: "正在重命名", disabled: true },
    { label: "打开报告", href: "#report" },
    { label: "不可导出", href: "#export", disabled: true },
    { label: "归档", onSelect: vi.fn() },
  ]} />);
  await user.click(screen.getByRole("button", { name: "管理 报告" }));
  expect(screen.getByRole("menuitem", { name: "打开报告" })).toHaveFocus();
  await user.keyboard("{ArrowDown}");
  expect(screen.getByRole("menuitem", { name: "归档" })).toHaveFocus();
  await user.keyboard("{ArrowDown}");
  expect(screen.getByRole("menuitem", { name: "打开报告" })).toHaveFocus();
  await user.keyboard("{End}{ArrowUp}");
  expect(screen.getByRole("menuitem", { name: "打开报告" })).toHaveFocus();
});

it("leaves focus in a replacement dialog when the previous dialog's close frame runs", async () => {
  const frames: FrameRequestCallback[] = [];
  const frame = vi.spyOn(window, "requestAnimationFrame").mockImplementation(callback => { frames.push(callback); return frames.length; });
  try {
    function Replacement() {
      const [step, setStep] = useState(0);
      return <><button onClick={() => setStep(1)}>打开</button>{step ? <ProductModal key={step} title={`弹窗 ${step}`} onClose={() => setStep(0)} footer={<button onClick={() => setStep(2)}>下一步</button>}><label>当前输入<input /></label></ProductModal> : null}</>;
    }
    render(<Replacement />);
    screen.getByRole("button", { name: "打开" }).focus();
    fireEvent.click(screen.getByRole("button", { name: "打开" }));
    fireEvent.click(screen.getByRole("button", { name: "下一步" }));
    await act(async () => frames.forEach(callback => callback(0)));
    expect(screen.getByRole("dialog", { name: "弹窗 2" })).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "当前输入" })).toHaveFocus();
  } finally { frame.mockRestore(); }
});

it("keeps an all-disabled row menu escapable without focusing unavailable actions", async () => {
  const user = userEvent.setup();
  render(<ManagedObjectRow href="#sample" title="归档材料" description="" actions={[{ label: "暂不可编辑", disabled: true }]} />);
  const trigger = screen.getByRole("button", { name: "管理 归档材料" });
  await user.click(trigger);
  expect(trigger).toHaveFocus();
  await user.keyboard("{ArrowDown}{End}{Escape}");
  expect(screen.queryByRole("menu")).not.toBeInTheDocument();
  expect(trigger).toHaveFocus();
});
