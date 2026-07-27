# Findings: {plan_name}

<!--
findings.md schema — Main agent sole writer. All workers read via prompt injection.
Init: include only sections required by the active patterns (see table below).
Do NOT invent custom section names. Pattern → section mapping is fixed.

| Pattern                  | Required sections (in addition to [Shared Variables/Paths])               |
|--------------------------|---------------------------------------------------------------------------|
| pipeline / hierarchical  | [Next Step Instructions]                                                  |
| fan_out / fan_out_fan_in | [Key Insights], [Key Keywords], [Data Conflicts]                          |
| producer_reviewer        | [Change Requests]                                                         |
| supervisor / handoff     | [Data Conflicts]                                                          |
| expert_pool              | [Routing Rationale]  (format: "- {agent}: {reason} (matching: {keyword})")|

All patterns share: [Shared Variables/Paths].
-->

## [Shared Variables/Paths]
<!-- Required for all patterns. Workspace paths, API contracts, persistence resume points. -->
- Working directory:
- Output paths:

## [Key Insights]
<!-- fan_out / fan_out_fan_in only. Worker outputs synthesized by main. -->

## [Key Keywords]
<!-- fan_out / fan_out_fan_in only. Common keywords injected into worker prompts. -->

## [Data Conflicts]
<!-- fan_out / supervisor / handoff. Conflicting outputs with sources cited. Never delete a side. -->

## [Change Requests]
<!-- producer_reviewer only. Reviewer's REJECT feedback for next producer iteration. -->

## [Next Step Instructions]
<!-- pipeline / hierarchical only. Hand-off guidance to next agent. -->

## [Routing Rationale]
<!-- expert_pool only. Format: "- @agent-name: {reason} (matching: {keyword})" -->
