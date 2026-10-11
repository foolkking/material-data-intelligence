import { expect, it } from "vitest";
import { validateSearchResponse } from "./search-request";
const item = { kind: "project" as const, projectId: "one", id: "one", title: "项目", subtitle: "", href: "/projects/one", status: "active" };
it.each(["https://outside.test/projects/one", "/projects/one/../../tasks", "/projects/two", "/projects/one/%2e%2e/two"])("rejects a result outside its declared project: %s", (href) => {
  expect(() => validateSearchResponse({ query: "", count: 1, items: [{ ...item, href }] })).toThrow();
});
it("keeps a project-scoped selection link and rejects duplicate identities", () => {
  const result = { query: "", count: 1, items: [{ ...item, href: "/projects/one/data?dataset=d&selection=source#sample" }] };
  expect(validateSearchResponse(result)).toBe(result);
  expect(() => validateSearchResponse({ ...result, items: [item, item] })).toThrow();
});
