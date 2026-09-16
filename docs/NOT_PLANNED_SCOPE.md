# Not Planned Scope

Status: CURRENT, NOT QUEUED

These capabilities do not fit the current Material Data Intelligence product.
They have no implementation plan unless the project definition changes.

## V0 Agent and Validation Exclusions

The V0 product does not include:

- a Secondary LLM critic, scientific reviewer or reviewer provider;
- an AI substitute for independent human expert validation;
- `STANDARD / RISK_AWARE / STRICT` scientific review modes;
- an Expert Mode in which a second model pretends to be a scientist;
- unlimited autonomous research or arbitrary workflow/code execution.

Workstream I is a deterministic/structured scientific reasoning guard.
Workstream J is offline independent-human-validation infrastructure.
Workstream K is conditional only on demonstrated real J defects. None of these
creates a runtime scientific reviewer.

If a later professional/expert control is authorized, it may only expose more
direct user control over method, parameters, scientific presets, viewers and
analysis scope. It must not mean a second LLM reviewer.

## Enterprise SaaS

No multi-tenancy, organization hierarchy, billing, subscriptions, enterprise
quota product, or enterprise admin portal.

## Enterprise Identity

No enterprise RBAC platform, SSO/SAML, or enterprise IAM program. Ordinary
application configuration and basic permissions are not prohibited.

## Enterprise Secret Infrastructure

No KMS/HSM project, secret-rotation service, or credential broker. API keys and
BYOK secrets must remain protected, undisclosed, absent from logs/prompts/
artifacts, and subject to the existing application security boundary.

## Deployment Productization

No Kubernetes, Helm, cluster autoscaling, multi-region, disaster-recovery/SLA,
or standalone deployment-platform phase. PostgreSQL, Redis, MinIO, Docker, and
CI may remain service-backed integration infrastructure.

## Enterprise Observability

No Prometheus/OpenTelemetry platform, PagerDuty integration, or SLO/SLA product.
Job events, logs, typed errors, duration, and basic health remain appropriate.

## Plugin Ecosystem

No marketplace, public plugin registry, third-party billing, signed marketplace
packages, or developer ecosystem platform. A narrowly scoped internal Adapter
extension interface may be reviewed only when a concrete need exists.

## Collaboration Product

No comments product, organization collaboration, approval workflow, or
enterprise review workflow under the current product definition.
