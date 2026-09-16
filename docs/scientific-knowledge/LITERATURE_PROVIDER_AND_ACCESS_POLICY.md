# Literature Provider and Access Policy

## Initial providers

| Provider | Roles |
|---|---|
| OpenAlex | discovery, identity, bibliographic metadata, OA-location metadata |
| Crossref | DOI identity, registration metadata, publication relations, license metadata |
| User upload | exact Project-authorized document identity and parsed passage authority |

Provider fields retain their source. A normalized projection may combine exact
identities, but does not erase which provider supplied each snapshot.

## Network boundary

Backend retrieval is limited to fixed HTTPS hosts:

```text
api.openalex.org
api.crossref.org
```

The provider client:

- rejects any other scheme or host;
- does not follow redirects;
- accepts JSON only;
- caps a response at 4 MiB;
- uses a 12-second request timeout;
- bounds result count to 20;
- retries a `429`, `502`, `503`, or `504` response at most once, respecting a
  bounded `Retry-After` delay capped at five seconds;
- converts a persistent rate limit/outage into a typed unavailable outcome;
- never executes provider HTML, JavaScript, code, or instructions.

The Agent cannot provide a URL for the backend to fetch. Source links may be
shown to the scientist, but are not generic backend fetch authority.

## Explicit activation and privacy

External search requires:

```text
use_external_scientific_knowledge = true
```

The only outbound payload is a validated `LiteratureQuery` containing bounded
scientific question/terms, purpose, optional dates, provider scope, and result
limit. Validation rejects UUIDs, internal project/dataset/sample labels,
emails, local paths, and URLs. Project names, user identity, private notes,
Research history, file paths, secrets, and runtime identities are not sent.

Users must make an explicit search action in the current UI. Research does not
silently transmit every question to scholarly providers.

## Rights and full text

OA-location metadata alone is not proof that an arbitrary passage was read.
`OPEN_FULL_TEXT` and repository full-text evidence require:

1. an OA access status from a supported authority; and
2. the exact passage in the immutable snapshot's retrieved-passage set.

`USER_PROVIDED_FULL_TEXT` additionally requires a user-upload provider identity
and exact content hash. Uploaded paper text is not automatically transmitted
to DeepSeek or an external provider; only bounded selected passages may enter
Context.

Restricted/paywalled text is not scraped, authenticated publisher sessions are
not reused, and redirects do not bypass the provider allowlist.

## Caching and freshness

Equivalent public metadata queries may reuse a Project-scoped search record
for 24 hours. Cache identity includes the canonical query fingerprint. A new
research action can retrieve a newer snapshot; it does not mutate old evidence.
Correction/retraction freshness must be rechecked in later Research rather than
assuming cached status remains current forever.

## Failure behavior

Provider failure preserves all current Results, evidence, Research state, and
historical snapshots. The caller receives
`EXTERNAL_KNOWLEDGE_UNAVAILABLE` and may retry, continue without literature, or
stop with a limitation. Completed scientific computation is never restarted
merely because a scholarly provider failed.
