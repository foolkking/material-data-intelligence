# Materials Intelligence Platform — Continuous Product Maturity Closure

Source objective: `goal-objective.md`, authorized 2026-09-01.

## Execution mode

This task runs continuously and autonomously until the complete Materials
Intelligence Platform satisfies mature-product completion. Internal phases,
batches and tracks are organizational tools, not stopping points.

Unless a genuine external blocker exists:

- do not wait for approval after each phase;
- do not ask whether to continue;
- do not stop after audit, planning or documentation;
- do not stop because a local test passes;
- do not narrow the requested product scope;
- do not ignore newly discovered product defects because Phase 14-R has a
  historical COMPLETE record.

Required loop:

```text
audit
→ screenshots
→ find defects
→ group root causes
→ unified design
→ conflict check
→ design correction
→ implementation
→ browser verification
→ automated tests
→ after screenshots
→ visual review
→ remaining-defect discovery
→ continue
```

Continue until no P0/P1 defect blocks real user or administrator operation.

## Autonomous decision authority

The agent may implement reasonable improvements not itemized below when they
clearly help real users or administrators use the system more safely, easily,
clearly or efficiently, and do not break scientific authority, provenance,
authorization or data integrity.

This includes bounded changes to:

- user and administrator workflows;
- information architecture and navigation;
- shared UI;
- APIs and database schemas;
- authorization and audit;
- onboarding, account, security and management;
- removal or consolidation of redundant interaction.

Do not add complexity merely to create more features.

## Global-first UI rule

Do not continue page-by-page patching. First complete a screenshot audit of all
major pages. For every major page identify at least ten concrete UI/UX issues,
then combine them under shared roots:

```text
Global Shell
Navigation
Breadcrumb
Page Header
Sidebar
Scroll Ownership
Typography
Spacing
Button Hierarchy
Filters / Tabs
Tables / Lists
Forms
Dialogs
Loading
Empty / Error
Viewer Controls
Research Layout
Report Layout
Account
Admin
Responsive
Accessibility
```

Resolve design conflicts before implementation. Apply the stable unified
solution through shared components and affected pages. Re-audit every page
after implementation. Automated tests alone cannot close UI work.

## Never stop on first pass

After the first implementation pass, perform a complete post-implementation
product audit:

- traverse all major routes again;
- recapture desktop and mobile;
- retest scrolling, navigation, user/admin journeys;
- retest loading, error, empty, offline and authorization states;
- review visual consistency.

Fix forward and re-audit until the product converges.

## Blocking policy

Only stop for:

1. a required external account, secret, domain, email service or third-party
   authorization;
2. an incompatible business choice with no safe default;
3. infrastructure failure that repository work cannot resolve;
4. irreversible data risk without user authority;
5. required data that is missing and unrecoverable.

Tests, UI, migrations, routes, permissions, browser issues, performance and
design conflicts are not blockers.

## Product-level completion conditions

The task completes only when the entire product simultaneously has:

- a complete user account lifecycle;
- a complete platform administrator system;
- a complete User Center;
- unified Global / Project / Entity information architecture;
- reasonable entry and exit points on every major page;
- natural deep-page return to Console and Project;
- fully reachable/scrollable content;
- no meaningless desktop whole-page horizontal scrolling;
- usable desktop and mobile;
- a unified UI system;
- before/after screenshot review for every major page;
- no obvious P0/P1 usability defect;
- passing real user and administrator journeys;
- passing cross-project authorization;
- preserved Result, provenance and version authority;
- passing backend/frontend/service-backed regression;
- a final audit with no new blocking issue.

Final evidence must truthfully report:

```text
PRODUCT_PLATFORM_MATURITY = COMPLETE / PARTIAL
USER_ACCOUNT_LIFECYCLE = COMPLETE / PARTIAL
ADMIN_PLATFORM = COMPLETE / PARTIAL
USER_CENTER = COMPLETE / PARTIAL
GLOBAL_INFORMATION_ARCHITECTURE = PASS / PARTIAL
UI_UX_SYSTEM = PASS / PARTIAL
PAGE_REACHABILITY = PASS / FAIL
ROUTE_CONTINUITY = PASS / PARTIAL
REAL_USER_ACCEPTANCE = PASS / FAIL
REAL_ADMIN_ACCEPTANCE = PASS / FAIL
REMAINING_P0 = <count>
REMAINING_P1 = <count>
READY_FOR_REAL_MULTI_USER_PRODUCTION = YES / NO
```

If `REMAINING_P0 > 0` or `REMAINING_P1 > 0`, continue fixing. Do not create a
new Phase to defer work.

## 1. Product Reality Audit

Before implementation inventory:

- every frontend route;
- every user-reachable and administrator page;
- logged-out and logged-in global surfaces;
- Project, Data, Viewer, Research, Report, Tasks, Notifications, Search, Trash;
- User, Account, Settings, Admin, User Management, System Management;
- loading, empty, error, unauthorized and offline states;
- desktop/mobile states;
- page entry, exit and return relationships;
- API-to-route mappings;
- current identities, roles, permissions and ownership.

Classify each item:

```text
IMPLEMENTED
PARTIAL
MISSING
BROKEN
NEEDS_REDESIGN
```

Existing components or APIs alone do not prove mature functionality.

## 2. Whole-product UI/UX audit

For every real user/admin major page:

1. capture a real browser screenshot;
2. inspect desktop and mobile;
3. record at least ten concrete UI/UX/IA issues;
4. inspect hierarchy, navigation, scrolling, spacing, typography, button
   priority, filters/tabs, sidebars, states, responsiveness, accessibility,
   density, destructive actions and workflow continuity;
5. finish the complete audit before implementing.

Combine page findings into shared root causes and resolve conflicts before
batch implementation.

## 3. Scroll and reachability

Every page must:

- expose all content through real scrolling;
- avoid meaningless desktop whole-page horizontal scrolling;
- have one clear primary vertical scroll owner;
- keep sticky/fixed content from hiding body content;
- expose all mobile actions;
- prove long lists, reports and Viewers reach their real bottom.

Do not rely only on `scrollWidth`; physically scroll real pages.

## 4. Unified information architecture and navigation

Use three levels:

```text
Global Product
→ Project
→ Scientific Entity / Research / Report / Viewer
```

Global surfaces include Console/Home, Projects, Tasks, Notifications, Search
and user menu; administrators additionally see Admin.

Project surfaces retain Overview, Data, Research and Reports. Deep pages must
identify the Project, current entity, entry source, return to Project, return to
Console, and source Research/Dataset/Report. Browser Back is not the primary
navigation.

## 5. User account lifecycle

Determine whether the deployment should use public registration or
administrator invitation, then implement:

- register/invite;
- activation/verification;
- login/logout;
- forgot/reset password;
- session management;
- user status;
- disable/restore;
- account deactivation;
- basic security;
- useful errors;
- first-use onboarding.

Account deletion/deactivation must not break scientific provenance; historical
actor identity remains auditable.

## 6. Platform administrator system

Distinguish:

```text
Platform Admin
Project Owner
Project Member / Researcher
Viewer / Read-only
```

Admin Center must provide the useful subset of:

- user list/search/status/enable/disable;
- role and Project membership/ownership management;
- permissions;
- system audit and user activity;
- quotas/usage;
- Jobs/workers/provider/storage status;
- security/governance operations.

Dangerous actions are server-authoritative, confirmed, audited and
provenance-safe.

## 7. User Center

Provide appropriate:

- Profile, Account, Security and Sessions;
- notification and personal preferences;
- My Projects / Shared Projects;
- recent work and pinned items;
- user activity and personal data/work entry points.

Keep ownership clear between user, Project, organization/platform and
scientific authority.

## 8. Unified UI system

Preserve the existing product language while unifying hierarchy, density,
typography, spacing, actions, destructive semantics, filters, sidebars,
breadcrumbs, lists/tables, forms, modals/drawers, badges/status, loading,
empty/error/offline, responsiveness, accessibility and keyboard behavior.

Reinspect Data, Viewer, Trajectory, Research, Presentation, Report, Tasks,
Notifications, Search, Trash, Projects, Account and Admin. Group Viewer
controls and distinguish filters from primary actions.

## 9. Route and interaction continuity

Maintain a route/interaction matrix:

```text
current page
→ action
→ API
→ success state
→ new page/update
→ return path
```

Cover Project→Data, Data→Research, Research→Result, Result→Evidence/Viewer/
Report, Report→Research/Viewer, Task/Notification→Research, Search→exact
entity, Trash→original entity, Admin→User/Project, User→My Projects, and every
deep page→Console.

No wrong entity/project, guessed ID, obsolete page, 404, dead-end, full reload
or missing return.

## 10. Autonomous additions

Add useful, architecture-consistent capabilities discovered during audit when
they reduce user/admin effort, improve safety, clarity, governance or
continuity. Document why. Do not add feature theatre.

## 11. Real user and administrator acceptance

Use the real same-stack product:

User:

```text
new user
→ register/invite
→ login
→ onboarding
→ create/join Project
→ Data
→ Research
→ Result
→ Viewer
→ Report
→ Tasks/Notifications
→ User settings
→ logout/login recovery
```

Administrator:

```text
Admin login
→ user management
→ role/permission
→ Project management
→ system status
→ audit
→ disable/restore user
→ verify ordinary-user permission change
```

Also run desktop/mobile, keyboard/accessibility, scroll/reachability,
navigation continuity, loading/error/offline, authorization, cross-project
isolation and complete frontend/backend/service-backed regressions. Retain
before/after screenshots and visually review them.

## Final definition

Complete only when account lifecycle, Admin, User Center, global/project
navigation, route reachability, unified UI, desktop/mobile, user/admin
journeys, authorization, scientific provenance and full regression are all
proven, with no P0/P1 product defect.
