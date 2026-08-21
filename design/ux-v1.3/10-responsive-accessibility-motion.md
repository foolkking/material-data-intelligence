# Responsive, Accessibility, and Motion

## Viewport decisions

| Range | Shell decision | Data decision | Research decision |
| --- | --- | --- | --- |
| 1920x1080 | full 56/44 shell; max content avoids excessive prose width | 264px Navigator, 344px Inspector, large primary canvas | 36/64 conversation/workbench; 224px Activity |
| 1440x900 | default desktop reference | table/canvas remains dominant; quick preview 68vw | simultaneous conversation/current work, scroll regions independent |
| 1280x800 | compact desktop | Navigator 236px, Inspector 320px; hide low-priority toolbar labels first | conversation 38%, Activity 204px; no loss of active step |
| 768-979 | transitional narrow layout | Inspector overlays/replaces secondary width | preserve workbench, reduce secondary chrome |
| 390x844 | mobile | Navigator becomes horizontal/context strip; Viewer is browser-scrollable; Inspector sheet | conversation first, workbench follows; no horizontal viewport overflow |

## Scroll ownership

| Surface | Scroll owner |
| --- | --- |
| Landing / Console / Overview / Report | Browser document |
| Data shell | fixed viewport workbench |
| Data Navigator | own vertical scroll |
| Table / viewer main | own data scroll |
| Inspector | own vertical scroll |
| Research shell | fixed viewport workbench |
| Conversation | own vertical scroll |
| Workbench result | own vertical scroll |

No view may create simultaneous browser, conversation, and workbench “main” scrollbars. Mobile deliberately relaxes fixed workbench ownership into linear browser reading rather than forcing unusable nested scroll areas.

## Keyboard and focus

- Skip link targets the main region.
- Tab order: global/local navigation -> active region -> contextual Inspector -> prototype-only controls last.
- Resizer supports Left/Right keyboard adjustment in 1% increments between 30-45%.
- Escape closes Inspector/Quick Preview; focus returns to the opening control.
- Buttons use accessible labels and tooltips/title where symbol-only.
- Table rows and scientific selections have keyboard-reachable roles in the prototype; production must implement semantic grid behavior where the data grid supports it.
- Login Modal receives focus on its email field, traps Tab/Shift+Tab, closes with Escape, and restores the Login trigger. The authentication mechanism itself remains a product/backend decision, not a prototype claim.

## Motion

- No decorative motion.
- Active real work may use a three-dot/outlined-node pulse. It signifies “currently active”, never temporal progress.
- Overlay transitions target 120-180ms.
- `prefers-reduced-motion: reduce` suppresses nonessential animation and smooth scrolling.

## Verification limit

Chrome validation covers visual viewport behavior, keyboard focus paths, Escape close, and visible reduced-motion CSS contract. Native screen reader output, true 200% browser zoom behavior, and touch hardware ergonomics remain **NOT VERIFIED** until production implementation and device validation.

## UX-V1.3.1 closure evidence limit

The current Chrome capability rendered the final prototype and allowed DOM geometry and keyboard interaction checks at its actual `1920x1200` viewport. Its viewport override did not change the window to `1440x900`, `1280x800`, or `390x844`; its screenshot request failed closed before capture because the browser security check did not complete. Therefore final 1440/1280/mobile **visual screenshot evidence is NOT VERIFIED**, and true 200% Chrome zoom remains **NOT VERIFIED**. This is release evidence debt, not a design-rule exception.
