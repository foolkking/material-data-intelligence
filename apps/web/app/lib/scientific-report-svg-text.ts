/** Conservative glyph widths for inert SVGs rendered without browser font metrics. */
export function reportSvgTextWidth(text: string, fontSize = 16): number {
  return Array.from(text).reduce((size, character) =>
    size + (character.codePointAt(0)! > 255 ? 1 : 0.65) * fontSize, 0);
}

export function wrapReportSvgText(text: string, width: number, fontSize = 16): string[] {
  return text.split("\n").flatMap(line => {
    const lines: string[] = [];
    let current = "", used = 0;
    for (const character of line) {
      const advance = reportSvgTextWidth(character, fontSize);
      if (current && used + advance > width) {
        lines.push(current); current = ""; used = 0;
      }
      current += character; used += advance;
    }
    if (current) lines.push(current);
    return lines;
  });
}
