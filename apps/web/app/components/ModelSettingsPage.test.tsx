import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => ({
  getPlannerProviderStatus: vi.fn(),
  listPlannerProviders: vi.fn(),
  testPlannerProvider: vi.fn(),
  configurePlannerProvider: vi.fn(),
  listProviderModels: vi.fn(),
  removePlannerProvider: vi.fn(),
  updatePlannerProviderModels: vi.fn(),
}));

vi.mock("../lib/planner-api", () => mocks);

import { ModelSettingsDialog } from "./ModelSettingsPage";

beforeEach(() => {
  vi.clearAllMocks();
  mocks.getPlannerProviderStatus.mockResolvedValue({
    ok: true,
    provider: "custom-compatible",
    model: "model-a",
    status: "ready",
    allowedModels: ["model-a", "model-b"],
    configurationSource: "process_only",
  });
  mocks.listPlannerProviders.mockResolvedValue({ providers: [{ id: "custom-compatible", label: "兼容模型服务", provider: "custom-compatible", baseUrl: "https://api.example.com/v1", defaultModel: "model-a", allowedModels: ["model-a", "model-b"], models: ["model-a", "model-b"], secretConfigured: true, configurationSource: "process_only" }] });
  mocks.testPlannerProvider.mockResolvedValue({ ok: true, provider: "deepseek", model: "deepseek-v4-flash", latencyMs: 31, validated: true });
  mocks.configurePlannerProvider.mockResolvedValue({ ok: true, provider: { provider: "custom-compatible", label: "兼容模型服务", secretConfigured: true } });
  mocks.listProviderModels.mockResolvedValue({ ok: true, provider: "custom-compatible", models: ["model-a", "model-b"] });
  mocks.removePlannerProvider.mockResolvedValue({ ok: true, provider: "custom-compatible" });
  mocks.updatePlannerProviderModels.mockResolvedValue({ ok: true, provider: { provider: "custom-compatible", label: "兼容模型服务", secretConfigured: true } });
});

it("renders generic provider configuration without exposing a saved key", async () => {
  render(<ModelSettingsDialog open onClose={vi.fn()} />);

  expect(await screen.findByRole("heading", { name: "模型服务" })).toBeInTheDocument();
  expect(screen.getByText("当前服务")).toBeInTheDocument();
  expect(screen.getByText("已保存服务端连接；对话时可以选择模型和思考深度。")).toBeInTheDocument();
  expect(screen.getByLabelText("API Key")).toHaveAttribute("type", "password");
  expect(screen.getByText("安全与协议说明")).toBeInTheDocument();
});

it("clears the API key input after saving", async () => {
  const user = userEvent.setup();
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  const key = await screen.findByLabelText("API Key");
  await user.clear(key);
  await user.type(key, "temporary-test-key");
  await user.click(screen.getByRole("button", { name: "替换并保存密钥" }));
  expect(mocks.configurePlannerProvider).toHaveBeenCalledWith(expect.objectContaining({ apiKey: "temporary-test-key", baseUrl: "https://api.example.com/v1" }));
  expect(key).toHaveValue("");
});

it("runs a redacted provider connection test", async () => {
  const user = userEvent.setup();
  render(<ModelSettingsDialog open onClose={vi.fn()} />);

  await user.click(await screen.findByRole("button", { name: "测试连接" }));
  expect(mocks.testPlannerProvider).toHaveBeenCalledWith({ provider: "custom-compatible", model: "model-a" });
  expect(await screen.findByText("连接成功 · 31 ms")).toBeInTheDocument();
});

it("saves the selected model group without asking for the key again", async () => {
  const user = userEvent.setup();
  render(<ModelSettingsDialog open onClose={vi.fn()} />);
  await screen.findByRole("heading", { name: "模型服务" });
  const modelB = await screen.findByRole("checkbox", { name: "model-b" });
  await user.click(modelB);
  await user.click(screen.getByRole("button", { name: "保存模型组" }));
  expect(mocks.updatePlannerProviderModels).toHaveBeenCalledWith("custom-compatible", ["model-a"], "model-a");
});

it("closes from Escape", async () => {
  const user = userEvent.setup();
  const onClose = vi.fn();
  render(<ModelSettingsDialog open onClose={onClose} />);
  await screen.findByRole("heading", { name: "模型服务" });
  await user.keyboard("{Escape}");
  expect(onClose).toHaveBeenCalledTimes(1);
});
