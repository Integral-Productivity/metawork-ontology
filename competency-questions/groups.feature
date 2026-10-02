Feature: Meta Work Group conformance
  These questions are answered by SHACL validation of instance data, not by
  querying the vocabulary. They are the fitness functions a backend or plugin
  must pass to claim it stores Meta Work Groups.

  @CQ-10
  Scenario: Groups nest, but not under themselves
    Given the SHACL shapes and the ontology
    When I validate examples/valid-groups.ttl
    Then it conforms
    And the project-level group has the area-level group as parent
    When I validate examples/invalid-groups.ttl
    Then the group "Ouroboros" is reported for being its own parent

  @CQ-11
  Scenario: All three first-class axes are required
    Given the SHACL shapes and the ontology
    When I validate examples/invalid-groups.ttl
    Then the group "No strata" is reported for a missing system_strata

  @CQ-12
  Scenario: An axis rejects a value from another scheme
    Given the SHACL shapes and the ontology
    When I validate examples/invalid-groups.ttl
    Then the group "Wrong scheme" is reported because its horizons_of_focus is not in the Horizons of Focus scheme

  @CQ-13
  Scenario: Backends are enumerated
    Given the Meta Work ontology
    When I list the narrower concepts of "Backend"
    Then they are "OmniFocus backend" and "Markdown directory backend"

  @CQ-16
  Scenario: A group used at a different altitude than it is scoped at is flagged as a scope-axis mismatch
    Given the SHACL shapes and the ontology
    And a Decision records the Meta Work Group it is worked in and the Horizons of Focus altitude it is made at
    When I validate examples/valid-groups.ttl with examples/valid-decisions.ttl
    Then it conforms, because every decision is made at its group's horizons_of_focus
    When I validate examples/valid-groups.ttl with examples/invalid-decisions.ttl
    Then the 20,000 ft question in the 10,000 ft project group is reported as a scope-axis mismatch warning naming both altitudes
    And the 10,000 ft question in the 20,000 ft area group is reported the same way
    And a decision with no altitude is a violation, not a mismatch
