# Phase 12-6 Keyboard and Focus Accessibility

Canonical keyboard journeys `K1` through `K10` cover skip navigation, global
navigation, Planner input and run controls, tab selection, Workspace panels,
context drawer, Inspector, Report confirmation, and recovery. Shared controls
retain semantic elements and `focus-visible`; dialogs trap focus, close with
Escape, and restore focus to their trigger.

The Planner data-context separator supports Arrow Left/Right and Home/End with
exact bounded values from 240 to 520 CSS pixels. This changes presentation
layout only.
