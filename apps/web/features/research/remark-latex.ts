/// <reference types="micromark-extension-math" />
/// <reference types="remark-parse" />

import type { Root, RootContent } from "mdast";
import type { Construct, State, Token } from "micromark-util-types";
import type { Plugin } from "unified";

// Extend Markdown's text tokenizer so code, escapes and link destinations
// retain their normal meaning. A global replacement would rewrite them.
const latexText: Construct = {
  name: "latexText",
  tokenize(effects, ok, nok) {
    let closing: number;
    let sequence: Token;
    const start: State = code => {
      effects.enter("mathText");
      effects.enter("mathTextSequence");
      effects.consume(code);
      return open;
    };
    const open: State = code => {
      if (code !== 40 && code !== 91) return nok(code);
      closing = code === 40 ? 41 : 93;
      effects.consume(code);
      effects.exit("mathTextSequence");
      return between;
    };
    const between: State = code => {
      if (code === null) return nok(code);
      if (code === 92) {
        sequence = effects.enter("mathTextSequence");
        effects.consume(code);
        return close;
      }
      if (code === -5 || code === -4 || code === -3) {
        effects.enter("lineEnding");
        effects.consume(code);
        effects.exit("lineEnding");
        return between;
      }
      effects.enter("mathTextData");
      return data(code);
    };
    const data: State = code => {
      if (code === null || code === 92 || code === -5 || code === -4 || code === -3) {
        effects.exit("mathTextData");
        return between(code);
      }
      effects.consume(code);
      return data;
    };
    const close: State = code => {
      if (code === closing) {
        effects.consume(code);
        effects.exit("mathTextSequence");
        effects.exit("mathText");
        return ok;
      }
      // A new math opener cannot belong to this formula. Stop here instead
      // of swallowing the next formula or repeatedly scanning an open draft.
      if (code === 40 || code === 91) return nok(code);
      sequence.type = "mathTextData";
      // A doubled backslash belongs to the formula (for example a matrix
      // row separator); its second slash cannot begin a closing delimiter.
      if (code === 92) {
        effects.consume(code);
        return data;
      }
      return data(code);
    };
    return start;
  },
};

/** Accept common LaTeX delimiters alongside remark-math's dollar syntax. */
export const remarkLatex: Plugin<[], Root> = function () {
  const options = this.data();
  (options.micromarkExtensions ||= []).push({ text: { 92: latexText } });
  return (tree, file) => {
    const source = String(file.value);
    function visit(node: Root | RootContent) {
      const start = node.position?.start.offset;
      if (node.type === "inlineMath" && start !== undefined && source.slice(start, start + 2) === "\\[") {
        node.data = { ...node.data, hProperties: { className: ["language-math", "math-display"] } };
      }
      if ("children" in node) node.children.forEach(visit);
    }
    visit(tree);
  };
};
