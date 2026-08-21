# Design System Specification

The full durable system is `.interface-design/system.md`. This document translates it into implementation-facing choices for the UX-V1.3 production handoff.

## Token reference

```text
Canvas #F5F7F6       Surface #FFFFFF       Surface subtle #EFF2F0
Border #D9DFDC       Border strong #AEB9B3
Text #18211D         Secondary #59655F     Tertiary #78837D
Mineral Green #0B6B57  Mineral soft #E3F0EC
Warning #8A5B0D      Danger #A64034        Information #315E78
```

Use existing production tokens where their semantic role and contrast meet this specification; do not duplicate a second visual token system without a migration decision.

## Component contracts

| Component | Geometry | Hierarchy | Required behavior |
| --- | --- | --- |
| GlobalBar | 56px | Product + current context | Sticky on document views; fixed workbench parent on workbench views. |
| ProjectNav | 44px | Four user concepts only | Active underline is 2px Mineral Green. |
| Data Navigator | 264px desktop | Contextual inventory | Own vertical scroll; search; selected source uses soft green. |
| Viewer Toolbar | 52px | Object title, tools | Keep object name and context visible; controls adjacent to object. |
| Inspector | 344px desktop | Selected-object details | Dismissible, selection-driven, own scroll; Details / Evidence / Source & process. |
| Conversation | 36% default | Question continuity | Desktop resize 30-45%; own scroll and composer. |
| Activity | 224px | Observable work state | Ordered discrete steps, no percent. |
| Figure | flexible / document width | Primary result | Variables, units, caption, scope, accessible name. |
| Quick Preview | 68vw | Temporary object focus | Modal-like right viewer; Escape/close returns focus. |
| Login modal | 440px max | Authentication entry | Modal focus trap; Escape closes and restores trigger focus. |

## States

State color uses a semantic triad: `text + glyph + restrained color`. Success is green/check, active is green outlined node/pulse, warning is amber/exclamation, failure is red/cross. Do not make status a standalone badge when the state needs explanatory copy.

## Content density

- 15px body and 13px utility are the floor for default desktop UI.
- Tables use 40px rows and headers by default: 13px column text, 12px units, readable contrast, and horizontal scan behavior. A 42px comfortable mode is optional, never the default density.
- Scientific content has room to breathe: no decorative padding around irrelevant card shells.
- In Review/Result prose, limitation is as readable as the headline finding.

## Language and action ownership

Product chrome is Simplified Chinese. Canonical identifiers, material formulas, units, and user-created names retain their source language; technical English is progressively disclosed only. GlobalBar is limited to brand/current context/search/identity. Page actions remain beside their owned object: Data owns upload/research-this-data, Research owns scope/data reference, and Reports owns report actions.
