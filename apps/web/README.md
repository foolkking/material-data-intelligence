# Web application

The Next.js application provides the product shell and the project workspaces:

- Data: one scientific data workspace with saved viewer outputs and precise source selection.
- Research: one composer, branch-aware conversation, result workbench and on-demand context/provenance.
- Reports: document reading, saved figures/tables and authenticated Markdown/ZIP downloads.
- Projects, tasks, model settings, account and administration: durable product navigation and management.

Scientific viewers read validated saved payloads. They may prepare a browser rendering, but they do not create authoritative scientific results or silently infer chemistry from a visual connection.

Run from the repository root:

    npm --prefix apps/web ci
    npm --prefix apps/web run dev -- -p 3023 -H 127.0.0.1

Use the repository-root scripts/dev.ps1 for the normal full stack so the external runtime paths and proxy target are loaded consistently. Follow the [root README](../../README.md) for temporary environment variables, checks and isolated production builds while the frontend remains running.
