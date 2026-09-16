import { expect, it } from "vitest";

import {
  scientistDatasetLabel,
  scientistProjectLabel,
} from "../../shared/product-labels";

it("uses scientist-facing fallbacks for identity-shaped project and dataset names", () => {
  expect(scientistProjectLabel("project_fixture", "project_fixture")).toBe(
    "材料研究项目",
  );
  expect(scientistDatasetLabel("dataset_fixture", "dataset_fixture")).toBe(
    "当前项目材料数据",
  );
  expect(scientistProjectLabel("锂离子扩散研究", "project_fixture")).toBe(
    "锂离子扩散研究",
  );
  expect(scientistDatasetLabel("500 K 扩散轨迹", "dataset_fixture")).toBe(
    "500 K 扩散轨迹",
  );
});
