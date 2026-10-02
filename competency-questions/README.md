# Competency questions

A competency question (Grüninger & Fox, 1995) is a question the ontology must
be able to answer. They are the ontology's acceptance tests: if a question
here cannot be answered from `ontology/metawork.ttl` plus conforming instance
data, the ontology is incomplete.

Each `.feature` file holds the questions for one concern, written as Gherkin
so that the same text serves three readers:

- a practitioner, who reads the `Scenario:` lines as plain statements of what
  Meta Work distinguishes;
- a maintainer, who treats a failing scenario as a modeling bug;
- a tool (plugin, skill, MCP server), which can check that it honors the
  distinction before claiming to "support Meta Work".

`tests/test_competency_questions.py` executes every scenario tagged with a
`@CQ-nn` id by running a SPARQL query against the ontology. A scenario
without an executable step is marked `@pending` and counts as a known gap.

## Index

| Id | Question | File |
|---|---|---|
| CQ-01 | What is the difference between Meta Work and meta-work? | distinctions.feature |
| CQ-02 | Is "Meta-Task" part of the Meta Work methodology? | distinctions.feature |
| CQ-03 | What are the first-class scope axes of a Meta Work Group? | scope.feature |
| CQ-04 | What are the optional scope classifiers? | scope.feature |
| CQ-05 | What values may `horizons_of_focus` take, and what source defines them? | scope.feature |
| CQ-06 | What values may `vertical_development_stage` take? | scope.feature |
| CQ-07 | Is Life Domain a scope axis? | scope.feature |
| CQ-08 | Which pillars does Meta Work v1 integrate, and who authored each? | pillars.feature |
| CQ-09 | Which pillar do the daily perspective checks come from? | pillars.feature |
| CQ-10 | Can a Meta Work Group nest under another? Under what constraint? | groups.feature |
| CQ-11 | Must a Meta Work Group declare all three first-class axes? | groups.feature |
| CQ-12 | Can a classifier value be used where an axis value belongs? | groups.feature |
| CQ-13 | Which backends can hold a Meta Work Group? | groups.feature |
| CQ-14 | Where does each concept's definition come from (provenance)? | provenance.feature |
| CQ-15 | Does the plugin's YAML schema use exactly the ontology's vocabulary? | provenance.feature |
| CQ-16 | Is a group being used at a different altitude than it is scoped at (scope-axis mismatch)? | groups.feature |
