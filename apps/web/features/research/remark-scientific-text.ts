import type { Nodes, Root } from "mdast";
import type { Plugin } from "unified";
import { scientificNarrativeText } from "../../app/lib/scientific-narrative-text";
import { presentationLimitationText } from "../../app/lib/scientific-limitation-text";

/** Localize reviewed prose after parsing, preserving code, math and references. */
export const remarkScientificText: Plugin<[], Root> = () => root => {
  function visit(node: Nodes) {
    if (["code", "inlineCode", "math", "inlineMath", "link", "linkReference", "image", "imageReference", "definition", "html"].includes(node.type)) return;
    if (node.type === "text") node.value = scientificNarrativeText(presentationLimitationText(node.value));
    if ("children" in node) node.children.forEach(visit);
  }
  visit(root);
};
