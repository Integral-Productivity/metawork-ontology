# 1. Record architecture decisions

Date: 2026-10-02

## Status

Accepted

## Context

This repository holds a formal ontology whose whole purpose is to make the
Meta Work methodology inspectable and contestable. Modeling choices (what is
a class, what is a concept, which relation a mapping asserts) are decisions
in exactly the sense that software architecture decisions are, and they need
the same provenance.

## Decision

Record architecture and modeling decisions as ADRs in `docs/adr/`, following
the format used in `metawork-claude-plugin` and `metawork-methodology`
(Nygard-style: Context / Decision / Consequences, with a "trigger to revisit").
`.adr-dir` points `adr-tools` at this directory.

## Consequences

- Every change to the ontology that alters a class, a scheme, or a
  constraint is accompanied by an ADR or a reference to the one that
  authorizes it.
- Contributors who disagree with a modeling choice argue against a specific
  ADR, not against the whole file.
