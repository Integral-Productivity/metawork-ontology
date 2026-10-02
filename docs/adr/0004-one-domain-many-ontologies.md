# 4. One domain for many ontologies: path registry, routing, versioning, persistence

Date: 2026-10-02

## Status

Accepted

## Context

`metawork-ontology` publishes at `https://ontology.integralproductivity.com/metawork/`
from GitHub Pages. More ontologies are planned (Holacracy, Theory of Positive
Disintegration, framework-to-framework mappings), each in its own repository
per ADR-0002. Three facts shape what happens next.

**A GitHub Pages custom domain binds to one repository.** Today that is this
repository. A second repository cannot also answer at the domain root.

**IRIs are permanent once published.** The namespace
`https://ontology.integralproductivity.com/metawork#` and the vocabulary
prefix `…/metawork/vocab/` are already in a public `.ttl` and in the plugin's
sync test. Changing them later breaks every consumer. So the naming scheme
must be settled before the second ontology, not after.

**The domain belongs to a company; the ontologies are meant to outlive any
one entity.** The stewardship decision of 2026-10-02 moves the repositories
to the Integral Productivity Institute once it exists. A hostname tied to
`integralproductivity.com` is a dependency the Institute would inherit.

### Terms, for readers new to them

- **Path namespace.** All ontologies share one host and differ by path
  prefix (`/metawork/`, `/holacracy/`). This is the W3C convention
  (`w3.org/ns/prov`, `w3.org/ns/shacl`). The alternative, one subdomain per
  ontology, would change IRIs already minted and is rejected.
- **Content negotiation.** The same IRI returns HTML to a browser and Turtle
  to a program, based on the request's `Accept` header. Static hosting cannot
  do this; a small program in front of it can. The usual response for a
  non-HTML request is `303 See Other` to the machine-readable file.
- **Cloudflare Worker.** A small JavaScript function that runs at Cloudflare's
  edge in front of the origin. Because this zone is already on Cloudflare and
  the record is proxied, a Worker can be attached to the hostname with a
  route and no DNS change.
- **Unversioned IRI plus dated snapshots.** The IRI without a version always
  means "current". Each release is also frozen at a dated path. Consumers
  who need stability pin the snapshot; everyone else follows current.
- **Persistent identifier (w3id.org, PURL).** A community-run redirect
  service: `https://w3id.org/<prefix>/…` forwards to wherever the ontology
  lives today. Entries are managed by pull request. If the host, the domain,
  or the steward changes, only the redirect changes and every published IRI
  keeps working.

## Decision

1. **Path registry.** One registry maps path prefixes to repositories. It
   lives in the router (`infra/ontology-router/registry.json` in this
   repository for now; it moves to a hub repository when the second ontology
   starts — see Consequences). Prefixes are never reused or renamed. Reserved
   now: `/metawork/` (this repo), `/holacracy/`, `/tpd/`, `/mappings/`.

2. **Routing by Cloudflare Worker, not by a hub build.** A Worker on
   `ontology.integralproductivity.com/*`:
   - passes requests for the prefix that owns the custom domain straight to
     GitHub Pages (today: `/metawork/` and `/`);
   - for every other registered prefix, fetches from that repository's
     project site at `integral-productivity.github.io/<repo>/<path>` so each
     repository publishes independently;
   - performs content negotiation: a `GET` on a registered prefix whose
     `Accept` prefers an RDF media type over HTML receives `303 See Other`
     to that ontology's `.ttl`, with `Vary: Accept`.
   A hub build that aggregates every repository's site was considered and
   rejected: it is the same sync machinery ADR-0003 already carries between
   methodology and plugin, and it couples every ontology's release to one
   pipeline.

3. **Versioning.** The unversioned IRI (`/metawork/`) is "current". Each
   tagged release is additionally published at `/metawork/v/<version>/`
   (reserved now, populated from the next release). `owl:versionInfo` and a
   git tag carry the version; the IRI namespace itself never changes.

4. **Persistence is deferred, with a dated trigger.** Re-minting the
   namespace under `w3id.org` is the right long-term answer and is cheap
   only while there is one consumer. It is deferred because the Institute
   does not yet exist to own the w3id entry, and because an org-level
   decision (which entity owns which identifiers) should not be made inside
   one ontology's ADR. **Trigger:** the earlier of (a) the Institute's
   formation, or (b) the second ontology's first public release. At that
   point, decide w3id once for all prefixes.

## Consequences

**Positive**

- Each ontology repository stays independent: build, test, release, publish
  on its own cadence. Adding one is a registry line plus a project site.
- Linked Data clients get Turtle from the same IRIs humans read.
- The namespace scheme is written down before it is contested.

**Negative**

- A Worker is infrastructure outside GitHub. It must be versioned (it is,
  here) and owned (Marketing's domain-naming authority today; the Institute
  later).
- The router's registry lives in one ontology's repo until a hub exists,
  which is a known wrong-place-for-now.
- Dated snapshots double the published surface per release.

**Trigger to revisit**

- Second ontology starts → create `Integral-Productivity/ontology-hub`
  (registry, router source, root index page), move `infra/ontology-router/`
  there, and transfer the custom domain to the hub repo so no single
  ontology is privileged.
- Institute formed or second release → the persistence decision above.
