# Phase 10F-14 Renderer Threat Model

## Untrusted

Uploaded structure content, species labels, filenames, metadata, warnings, style hints, unknown JSON fields and artifact files.

## Trusted

Application code, pinned Three.js package, canonical validators, whitelist mapper, application palette and geometry settings.

## Threats

JavaScript/DOM/CSS injection, network exfiltration, remote assets, dynamic modules, prototype pollution, oversized scenes, GPU exhaustion, lifecycle leaks and error disclosure.

## Boundary

Untrusted artifact data must pass contract validation and whitelist mapping before any renderer initialization. No trust is granted to old schemas or artifact styling beyond bounded hex/radius hints.
