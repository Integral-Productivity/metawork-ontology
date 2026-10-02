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
