Feature: Multi-axial scope
  A Meta Work Group is positioned on three first-class axes and up to two
  optional classifiers (ADR-0004, metawork-claude-plugin).

  @CQ-03
  Scenario: The three first-class axes are named
    Given the Meta Work ontology
    When I ask for the narrower concepts of "Scope (multi-axial)"
    Then they include "Horizons of Focus", "System Strata", and "Vertical Development Stage"

  @CQ-04
  Scenario: The two optional classifiers are named
    Given the Meta Work ontology
    When I ask for the narrower concepts of "Scope (multi-axial)"
    Then they include "Cynefin Domain" and "Neurological Level"

  @CQ-05
  Scenario: Horizons of Focus has six values with a cited source
    Given the Meta Work ontology
    When I list the concepts in the "Horizons of Focus" scheme
    Then there are exactly 6
    And their notations are 50000ft-purpose-principles, 40000ft-vision, 30000ft-goals-objectives, 20000ft-areas-focus-responsibility, 10000ft-projects, runway
    And the scheme cites David Allen as its source

  @CQ-06
  Scenario: Vertical Development Stage has eight values
    Given the Meta Work ontology
    When I list the concepts in the "Vertical Development Stage" scheme
    Then there are exactly 8
    And the first is "Self-Centric" and the last is "Unitive"

  @CQ-07
  Scenario: Life Domain is related to Scope but is not an axis of it
    Given the Meta Work ontology
    When I look up "Life domain"
    Then it is not narrower than "Scope (multi-axial)"
    And it is related to "Scope (multi-axial)"
