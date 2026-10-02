Feature: Pillars
  Meta Work integrates eight bodies of practice in v1. Each must be traceable
  to its source so that users can inspect, test, and build on them.

  @CQ-08
  Scenario: Eight pillars, each with provenance
    Given the Meta Work ontology
    When I list the concepts in the "Pillar" scheme
    Then there are exactly 8
    And at least 7 of them cite a source

  @CQ-09
  Scenario: Perspective checks belong to the Living Forward pillar
    Given the Meta Work ontology
    When I look up the "Perspective check" scheme
    Then it is narrower than the "Living Forward Life Plan" pillar
    And it has exactly 4 concepts
