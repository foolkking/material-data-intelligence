import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
const mocks = vi.hoisted(() => ({ getUserModels: vi.fn(), saveUserConnection: vi.fn(), discoverUserModels: vi.fn(), saveUserModelSelection: vi.fn() }));
vi.mock("../lib/user-models-api", async (original) => ({ ...(await original<typeof import("../lib/user-models-api")>()), ...mocks }));
import { ModelSettingsDialog } from "./ModelSettingsPage";
const base = { label: "我的模型服务", baseUrl: "https://example.com/v1", protocol: "openai_chat_json", secretConfigured: true, catalog: [], selected: [], revision: 1 };
beforeEach(() => { vi.clearAllMocks(); mocks.getUserModels.mockResolvedValue({ ...base }); });

const secondId = "00000000-0000-4000-8000-000000000002";
function multipleSettings() {
  const firstModel = { provider: "personal", model: "same-model" };
  const secondModel = { provider: `personal:${secondId}`, model: "same-model" };
  const connections = [
    { ...base, connectionId: "personal", provider: "personal", label: "原连接", catalog: [firstModel], selected: [firstModel] },
    { ...base, connectionId: secondId, provider: secondModel.provider, label: "备用连接", baseUrl: "https://second.example.com/v1", catalog: [secondModel], selected: [], revision: 7 },
  ];
  return { ...connections[0], catalog: [firstModel, secondModel], selected: [firstModel], connections };
}

it("keeps each connection's unsaved fields and selections while switching, then clears keys on close", async () => {
  const user = userEvent.setup();
  mocks.getUserModels.mockResolvedValue(multipleSettings());
  const view = render(<ModelSettingsDialog open onClose={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "编辑连接" }));
  await user.type(screen.getByLabelText("服务密钥（API Key）"), "first-draft-key");
  await user.click(screen.getByRole("checkbox", { name: "same-model" }));
  await user.selectOptions(screen.getByLabelText("已保存的连接"), secondId);
  expect(screen.getByRole("checkbox", { name: "same-model" })).not.toBeChecked();
  await user.click(screen.getByRole("button", { name: "编辑连接" }));
  expect(screen.getByLabelText("服务地址")).toHaveValue("https://second.example.com/v1");
  expect(screen.getByLabelText("服务密钥（API Key）")).toHaveValue("");
  await user.selectOptions(screen.getByLabelText("已保存的连接"), "personal");
  expect(screen.getByLabelText("服务密钥（API Key）")).toHaveValue("first-draft-key");
  expect(screen.getByRole("checkbox", { name: "same-model" })).not.toBeChecked();
  view.rerender(<ModelSettingsDialog open={false} onClose={vi.fn()} />);
  view.rerender(<ModelSettingsDialog open onClose={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "编辑连接" }));
  expect(screen.getByLabelText("服务密钥（API Key）")).toHaveValue("");
  expect(screen.getByRole("checkbox", { name: "same-model" })).toBeChecked();
});

it("saves and discovers only the chosen connection and locks switching during writes", async () => {
  const user = userEvent.setup();
  const account = multipleSettings();
  mocks.getUserModels.mockResolvedValue(account);
  let finish!: (value: unknown) => void;
  mocks.saveUserModelSelection.mockReturnValueOnce(new Promise((resolve) => { finish = resolve; }));
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  await user.selectOptions(await screen.findByLabelText("已保存的连接"), secondId);
  await user.click(screen.getByRole("checkbox", { name: "same-model" }));
  await user.click(screen.getByRole("button", { name: "保存模型选择" }));
  expect(mocks.saveUserModelSelection).toHaveBeenCalledWith([account.catalog[1]], 7, secondId);
  expect(screen.getByLabelText("已保存的连接")).toBeDisabled();
  const updated = { ...account, connectionId: secondId, connections: [account.connections[0], { ...account.connections[1], selected: [account.catalog[1]], revision: 8 }] };
  await act(async () => finish(updated));
  expect(screen.getByRole("checkbox", { name: "same-model" })).toBeChecked();
  mocks.discoverUserModels.mockResolvedValue(updated);
  await user.click(screen.getByRole("button", { name: "获取模型列表" }));
  expect(mocks.discoverUserModels).toHaveBeenCalledWith(secondId);
  await user.selectOptions(screen.getByLabelText("已保存的连接"), "personal");
  expect(screen.getByRole("checkbox", { name: "same-model" })).toBeChecked();
});

it("creates a new connection with its own retry identity and reconciles an uncertain save", async () => {
  const user = userEvent.setup();
  const account = multipleSettings();
  mocks.getUserModels.mockResolvedValue(account);
  mocks.saveUserConnection.mockRejectedValueOnce(new Error("连接超时，请重新读取配置确认保存状态后重试。"));
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "新增连接" }));
  expect(screen.getByLabelText("服务地址")).toHaveValue("");
  await user.type(screen.getByLabelText("服务地址"), "https://third.example.com/v1");
  await user.type(screen.getByLabelText("服务密钥（API Key）"), "third-draft-key");
  await user.click(screen.getByRole("button", { name: "保存连接" }));
  await screen.findByRole("alert");
  const sent = mocks.saveUserConnection.mock.calls[0][0];
  expect(screen.getByRole("button", { name: "保存连接" })).toBeDisabled();
  expect(sent.connectionId).not.toBe("personal");
  expect(sent.revision).toBe(0);
  const created = { ...base, label: "新连接", baseUrl: sent.baseUrl, connectionId: sent.connectionId, provider: `personal:${sent.connectionId}`, revision: 1 };
  mocks.getUserModels.mockResolvedValue({ ...account, connections: [...account.connections, created] });
  await user.click(screen.getByRole("button", { name: "重新读取配置" }));
  await screen.findByText("配置已更新，你正在编辑的内容仍保留。请核对后保存。");
  expect(screen.getByLabelText("服务密钥（API Key）")).toHaveValue("third-draft-key");
  mocks.saveUserConnection.mockResolvedValue({ ...created, connections: [...account.connections, created] });
  await user.click(screen.getByRole("button", { name: "保存连接" }));
  expect(mocks.saveUserConnection).toHaveBeenLastCalledWith(expect.objectContaining({ connectionId: sent.connectionId, revision: 1 }));
  await screen.findByText("连接已保存。现在可以获取模型列表。");
  await user.selectOptions(screen.getByLabelText("已保存的连接"), "personal");
  expect(screen.getByRole("checkbox", { name: "same-model" })).toBeChecked();
});

it("keeps uncertain writes locked per connection through switching and failed reconciliation", async () => {
  const user = userEvent.setup();
  const account = multipleSettings();
  mocks.getUserModels.mockResolvedValue(account);
  mocks.saveUserModelSelection.mockRejectedValueOnce(new Error("连接超时"));
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  await user.click(await screen.findByRole("checkbox", { name: "same-model" }));
  await user.click(screen.getByRole("button", { name: "保存模型选择" }));
  await screen.findByText(/上次保存状态尚未确认/);
  expect(screen.getByRole("button", { name: "保存模型选择" })).toBeDisabled();
  expect(screen.getByRole("button", { name: "获取模型列表" })).toBeDisabled();
  await user.selectOptions(screen.getByLabelText("已保存的连接"), secondId);
  expect(screen.queryByText(/上次保存状态尚未确认/)).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: "获取模型列表" })).toBeEnabled();
  await user.selectOptions(screen.getByLabelText("已保存的连接"), "personal");
  expect(screen.getByRole("checkbox", { name: "same-model" })).not.toBeChecked();
  expect(screen.getByRole("button", { name: "保存模型选择" })).toBeDisabled();
  mocks.getUserModels.mockRejectedValueOnce(new Error("读取失败"));
  await user.click(screen.getByRole("button", { name: "重新读取配置" }));
  await screen.findByText(/读取失败/);
  expect(screen.getByRole("button", { name: "保存模型选择" })).toBeDisabled();
  const updated = { ...account, connections: [{ ...account.connections[0], revision: 2 }, account.connections[1]] };
  mocks.getUserModels.mockResolvedValue(updated);
  await user.click(screen.getByRole("button", { name: "重新读取配置" }));
  await screen.findByText(/配置已更新/);
  await waitFor(() => expect(screen.getByRole("heading", { name: "原连接" })).toHaveFocus());
  expect(screen.getByRole("button", { name: "保存模型选择" })).toBeEnabled();
  mocks.saveUserModelSelection.mockResolvedValue({ ...updated, connections: [{ ...updated.connections[0], selected: [], revision: 3 }, updated.connections[1]] });
  await user.click(screen.getByRole("button", { name: "保存模型选择" }));
  await screen.findByText("已清空个人模型选择。");
  expect(mocks.saveUserModelSelection).toHaveBeenLastCalledWith([], 2);
});

it("locks background scrolling only while open and restores prior styles", async () => {
  document.body.style.overflow = "auto";
  document.documentElement.style.overflow = "scroll";
  const view = render(<ModelSettingsDialog open onClose={vi.fn()} />);
  await screen.findByRole("button", { name: "编辑连接" });
  expect(document.body.style.overflow).toBe("hidden");
  expect(document.documentElement.style.overflow).toBe("hidden");
  view.rerender(<ModelSettingsDialog open={false} onClose={vi.fn()} />);
  expect(document.body.style.overflow).toBe("auto");
  expect(document.documentElement.style.overflow).toBe("scroll");
  document.body.style.overflow = "";
  document.documentElement.style.overflow = "";
});
it("lets an ordinary account edit a private connection and choose a protocol", async () => {
  const user = userEvent.setup();
  mocks.saveUserConnection.mockResolvedValue({ ...base, protocol: "anthropic", revision: 2 });
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "编辑连接" }));
  await user.click(screen.getByText("高级设置"));
  const key = screen.getByLabelText("服务密钥（API Key）");
  expect(key).toHaveAttribute("type", "password");
  expect(key).toHaveValue("");
  await user.selectOptions(screen.getByLabelText("请求协议"), "anthropic");
  await user.type(key, "test-secret");
  await user.click(screen.getByRole("button", { name: "保存连接" }));
  expect(mocks.saveUserConnection).toHaveBeenCalledWith(expect.objectContaining({ protocol: "anthropic", apiKey: "test-secret", revision: 1 }));
  await user.click(await screen.findByRole("button", { name: "编辑连接" }));
  expect(screen.getByLabelText("服务密钥（API Key）")).toHaveValue("");
  expect(screen.queryByText(/平台管理员/)).not.toBeInTheDocument();
});

it("saves only personal selections and keeps platform models immediately available", async () => {
  const user = userEvent.setup();
  const catalog = [{ provider: "personal", model: "model-a" }, { provider: "personal", model: "model-b" }, { provider: "platform:shared", model: "system-model" }];
  mocks.discoverUserModels.mockResolvedValue({ ...base, catalog, revision: 2 });
  mocks.saveUserModelSelection.mockResolvedValue({ ...base, catalog, selected: [catalog[1]], revision: 3 });
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "获取模型列表" }));
  const model = await screen.findByRole("checkbox", { name: /model-b/ });
  expect(model).not.toBeChecked();
  expect(screen.queryByRole("checkbox", { name: /system-model/ })).not.toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "平台提供" })).toBeInTheDocument();
  await user.click(model);
  await user.click(screen.getByRole("button", { name: "保存模型选择" }));
  expect(mocks.saveUserModelSelection).toHaveBeenCalledWith([catalog[1]], 2);
  expect(await screen.findByText("已保存 1 个模型，可在研究中选择。")).toBeInTheDocument();
});

it("keeps secrets out of storage and clears them when the dialog closes", async () => {
  const user = userEvent.setup();
  const close = vi.fn();
  const view = render(<ModelSettingsDialog open onClose={close} />);
  await user.click(await screen.findByRole("button", { name: "编辑连接" }));
  await user.type(screen.getByLabelText("服务密钥（API Key）"), "unsaved-secret");
  await user.keyboard("{Escape}");
  expect(close).toHaveBeenCalledTimes(1);
  view.rerender(<ModelSettingsDialog open={false} onClose={close} />);
  view.rerender(<ModelSettingsDialog open onClose={close} />);
  await user.click(await screen.findByRole("button", { name: "编辑连接" }));
  expect(screen.getByLabelText("服务密钥（API Key）")).toHaveValue("");
  expect(JSON.stringify(window.sessionStorage)).not.toContain("unsaved-secret");
  expect(JSON.stringify(window.localStorage)).not.toContain("unsaved-secret");
});

it("does not invent fixed models when discovery returns no service", async () => {
  const user = userEvent.setup();
  mocks.discoverUserModels.mockResolvedValue({ ...base, revision: 2 });
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "获取模型列表" }));
  expect(await screen.findByText("未获取到个人模型。请检查连接后重试。")).toBeInTheDocument();
  expect(screen.queryByRole("checkbox")).not.toBeInTheDocument();
});

it("retries failed discovery without relabeling its retained catalog as a fresh success or losing draft choices", async () => {
  const user = userEvent.setup();
  const catalog = [{provider: "personal", model: "deepseek-v4-pro"}, {provider: "personal", model: "other-model"}];
  mocks.getUserModels.mockResolvedValue({...base, catalog, selected: [catalog[1]]});
  mocks.discoverUserModels.mockResolvedValueOnce({...base, catalog, selected: [catalog[1]], revision: 2, warnings: ["个人服务探测失败，请重试。"]})
    .mockResolvedValueOnce({...base, catalog, selected: [catalog[1]], revision: 3});
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  await user.click(await screen.findByRole("checkbox", {name: /deepseek-v4-pro/u}));
  await user.click(screen.getByRole("button", {name: "获取模型列表"}));
  expect(await screen.findByRole("alert")).toHaveTextContent("个人服务探测失败");
  expect(screen.queryByText("已获取 2 个模型，请勾选要使用的模型。")).not.toBeInTheDocument();
  expect(screen.getByRole("checkbox", {name: /deepseek-v4-pro/u})).toBeChecked();
  expect(screen.getByText("下方保留上次获取的 2 个模型，本次未能更新。")).toBeInTheDocument();
  await user.click(screen.getByRole("button", {name: "重新获取模型列表"}));
  expect(mocks.discoverUserModels).toHaveBeenCalledTimes(2);
  expect(mocks.getUserModels).toHaveBeenCalledTimes(1);
  expect(await screen.findByText("已获取 2 个模型，请勾选要使用的模型。")).toBeInTheDocument();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  expect(screen.getByRole("checkbox", {name: /deepseek-v4-pro/u})).toBeChecked();
});

it("keeps the draft on a failed save and requires saving changed connection details before discovery", async () => {
  const user = userEvent.setup();
  mocks.saveUserConnection.mockRejectedValue(new Error("配置已更新，请重新读取后再保存。"));
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "编辑连接" }));
  await user.type(screen.getByLabelText("服务密钥（API Key）"), "draft-key");
  expect(screen.getByRole("button", { name: "获取模型列表" })).toBeDisabled();
  await user.click(screen.getByRole("button", { name: "保存连接" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("配置已更新");
  expect(screen.getByLabelText("服务密钥（API Key）")).toHaveValue("draft-key");
});

it("shows granted platform models without personal setup and hides an absent platform section", async () => {
  const platform = { provider: "platform:shared", model: "exact-model-id", label: "平台模型" };
  mocks.getUserModels.mockResolvedValue({ ...base, secretConfigured: false, baseUrl: "", catalog: [platform], selected: [platform] });
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  expect(await screen.findByText("exact-model-id")).toBeInTheDocument();
  expect(screen.getByText("可直接使用")).toBeInTheDocument();
  expect(screen.queryByRole("checkbox")).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: "获取模型列表" })).toBeDisabled();
  expect(mocks.discoverUserModels).not.toHaveBeenCalled();
  expect(screen.queryByLabelText("服务地址")).not.toBeInTheDocument();
});

it("puts configured models before optional connection fields and avoids unchanged saves", async () => {
  const catalog = [{ provider: "personal", model: "deepseek-v4-pro" }];
  mocks.getUserModels.mockResolvedValue({ ...base, catalog, selected: catalog });
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  expect(await screen.findByRole("checkbox", { name: "deepseek-v4-pro" })).toBeChecked();
  expect(screen.queryByLabelText("服务地址")).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: "保存模型选择" })).toBeDisabled();
});

it("reconciles the latest revision after save failure without discarding draft selections or search", async () => {
  const user = userEvent.setup();
  const catalog = [{ provider: "personal", model: "deepseek-v4-pro" }, { provider: "personal", model: "other-model" }];
  mocks.getUserModels.mockResolvedValueOnce({ ...base, catalog, selected: [catalog[1]] }).mockResolvedValueOnce({ ...base, catalog, selected: [catalog[1]], revision: 4 });
  mocks.saveUserModelSelection.mockRejectedValueOnce(new Error("配置已更新，请重新读取后再保存。"))
    .mockResolvedValueOnce({ ...base, catalog, selected: catalog, revision: 5 });
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  await user.click(await screen.findByRole("checkbox", { name: "deepseek-v4-pro" }));
  await user.type(screen.getByLabelText("搜索模型"), "deepseek");
  await user.click(screen.getByRole("button", { name: "保存模型选择" }));
  await user.click(await screen.findByRole("button", { name: "重新读取配置" }));
  await screen.findByText("配置已更新，你正在编辑的内容仍保留。请核对后保存。");
  expect(screen.getByRole("checkbox", { name: "deepseek-v4-pro" })).toBeChecked();
  expect(screen.getByLabelText("搜索模型")).toHaveValue("deepseek");
  await user.click(screen.getByRole("button", { name: "保存模型选择" }));
  expect(mocks.saveUserModelSelection).toHaveBeenLastCalledWith(catalog, 4);
});

it("retains connection drafts and the secret when re-reading a failed save", async () => {
  const user = userEvent.setup();
  mocks.getUserModels.mockResolvedValueOnce({ ...base }).mockResolvedValueOnce({ ...base, revision: 9 });
  mocks.saveUserConnection.mockRejectedValueOnce(new Error("配置已更新，请重新读取后再保存。"));
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  await user.click(await screen.findByRole("button", { name: "编辑连接" }));
  await user.clear(screen.getByLabelText("服务地址"));
  await user.type(screen.getByLabelText("服务地址"), "https://new.example.invalid/v1");
  await user.type(screen.getByLabelText("服务密钥（API Key）"), "example-draft-secret");
  await user.click(screen.getByRole("button", { name: "保存连接" }));
  await user.click(await screen.findByRole("button", { name: "重新读取配置" }));
  await screen.findByText("配置已更新，你正在编辑的内容仍保留。请核对后保存。");
  expect(screen.getByLabelText("服务地址")).toHaveValue("https://new.example.invalid/v1");
  expect(screen.getByLabelText("服务密钥（API Key）")).toHaveValue("example-draft-secret");
  expect(screen.getByRole("button", { name: "获取模型列表" })).toBeDisabled();
});

it("restores the actual opener, or a surviving fallback for a removed menu item", async () => {
  const trigger = document.createElement("button");
  document.body.appendChild(trigger); trigger.focus();
  const fallback = document.createElement("button"); document.body.appendChild(fallback);
  const view = render(<ModelSettingsDialog open onClose={vi.fn()} fallbackFocus={fallback} />);
  await screen.findByRole("button", { name: "编辑连接" });
  view.rerender(<ModelSettingsDialog open={false} onClose={vi.fn()} fallbackFocus={fallback} />);
  expect(trigger).toHaveFocus();
  view.rerender(<ModelSettingsDialog open onClose={vi.fn()} fallbackFocus={fallback} />);
  await screen.findByRole("button", { name: "编辑连接" });
  trigger.remove();
  view.rerender(<ModelSettingsDialog open={false} onClose={vi.fn()} fallbackFocus={fallback} />);
  expect(fallback).toHaveFocus(); fallback.remove();
});

it("aborts a closed read and ignores its late response after reopening", async () => {
  let resolveLate!: (value: unknown) => void;
  mocks.getUserModels.mockReturnValueOnce(new Promise((resolve) => { resolveLate = resolve; }));
  const view = render(<ModelSettingsDialog open onClose={vi.fn()} />);
  const signal = mocks.getUserModels.mock.calls[0][0].signal;
  view.rerender(<ModelSettingsDialog open={false} onClose={vi.fn()} />);
  expect(signal.aborted).toBe(true);
  view.rerender(<ModelSettingsDialog open onClose={vi.fn()} />);
  await screen.findByRole("button", { name: "编辑连接" });
  await act(async () => { resolveLate({ ...base, label: "迟到的服务", catalog: [{ provider: "personal", model: "late-model" }] }); });
  expect(screen.queryByText("迟到的服务")).not.toBeInTheDocument();
  expect(screen.queryByRole("checkbox", { name: "late-model" })).not.toBeInTheDocument();
});

it("guards duplicate selection saves until the pending operation settles", async () => {
  const catalog = [{ provider: "personal", model: "deepseek-v4-pro" }];
  mocks.getUserModels.mockResolvedValue({ ...base, catalog });
  let resolve!: (value: unknown) => void;
  mocks.saveUserModelSelection.mockReturnValueOnce(new Promise((done) => { resolve = done; }));
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  fireEvent.click(await screen.findByRole("checkbox", { name: "deepseek-v4-pro" }));
  const save = screen.getByRole("button", { name: "保存模型选择" });
  fireEvent.click(save); fireEvent.click(save);
  expect(mocks.saveUserModelSelection).toHaveBeenCalledTimes(1);
  await act(async () => { resolve({ ...base, catalog, selected: catalog }); });
});

it("explains when a draft model disappears while re-reading the catalogue", async () => {
  const user = userEvent.setup();
  const pro = { provider: "personal", model: "deepseek-v4-pro" };
  mocks.getUserModels.mockResolvedValueOnce({ ...base, catalog: [pro] }).mockResolvedValueOnce({ ...base, catalog: [], revision: 2 });
  mocks.saveUserModelSelection.mockRejectedValueOnce(new Error("请重新读取配置。"));
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  await user.click(await screen.findByRole("checkbox", { name: "deepseek-v4-pro" }));
  await user.click(screen.getByRole("button", { name: "保存模型选择" }));
  await user.click(await screen.findByRole("button", { name: "重新读取配置" }));
  expect(await screen.findByText("配置已更新，1 个已选模型已不再可用，其余编辑仍保留。请核对后保存。")).toBeInTheDocument();
  expect(screen.queryByRole("checkbox")).not.toBeInTheDocument();
});
