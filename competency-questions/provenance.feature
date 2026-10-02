Feature: Provenance and synchronization
  An ontology that cannot say where its definitions came from cannot be
  inspected or contested. And an ontology the plugin does not actually use is
  decoration.

  @CQ-14
  Scenario: The ontology declares what it was derived from
    Given the Meta Work ontology
    When I read the ontology header
    Then it names metawork-claude-plugin CONTEXT.md and metawork-methodology as derivation sources
    And it carries a license

  @CQ-15
  Scenario: The plugin's YAML schema enums equal the ontology's notations
    Given the Meta Work ontology
    And the plugin schema fixtures/metawork-group.schema.yaml
    When I compare each enum in the schema with the notations of the matching scheme
    Then horizons_of_focus, system_strata, vertical_development_stage, cynefin_domain, neurological_level and perspective_checks match exactly
