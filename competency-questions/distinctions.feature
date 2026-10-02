Feature: Distinctions the methodology insists on
  The most important thing the Meta Work vocabulary does is keep three
  near-homonyms apart. A tool that cannot tell them apart does not support
  Meta Work, whatever its marketing says.

  @CQ-01
  Scenario: Meta Work and meta-work are distinct, related, and not synonyms
    Given the Meta Work ontology
    When I look up the concepts labelled "Meta Work" and "meta-work (escapist)"
    Then they are two different concepts
    And each is marked as related to the other
    And neither is a broader or narrower term of the other

  @CQ-02
  Scenario: Meta-Task is recorded but is not part of the methodology
    Given the Meta Work ontology
    When I look up the concept labelled "Meta-Task"
    Then it exists in the core scheme
    And it is not narrower than "Meta Work"
    And its definition says it is unrelated to the methodology
