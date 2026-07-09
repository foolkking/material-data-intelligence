# Phase 10F-3 Expected Contract Templates

These templates are not real expected outputs and are not official PASS evidence. They define future `expected_contract.json` shapes for direct-uploadable static physics fixtures.

## 1. Coordination Histogram Template

```json
{
  "case_id": "coordination_hist_small_crystal",
  "target_tool": "structure.coordination_hist",
  "provenance": {
    "label": "official_like_curated",
    "source": null,
    "official_pass_eligible": false
  },
  "input": {
    "type": "cif_or_poscar",
    "direct_uploadable": true,
    "max_sites": 64
  },
  "expected_artifacts": [
    "coordination_hist.json",
    "coordination_hist_plot.json",
    "summary.md",
    "recipe.json"
  ],
  "exact_checks": {
    "tool_id": "structure.coordination_hist",
    "security.contains_javascript": false,
    "security.external_urls": [],
    "security.external_urls_allowed": false
  },
  "numeric_checks": {
    "site_count": {
      "mode": "exact"
    },
    "histogram_counts": {
      "mode": "exact"
    }
  },
  "metadata_checks": {
    "schema_version": "required",
    "limits": "required",
    "warnings": "allowed"
  },
  "pass_claim_policy": {
    "official_pass_claimed": false,
    "requires_direct_replay": true
  }
}
```

## 2. XRD Template

```json
{
  "case_id": "xrd_small_crystal",
  "target_tool": "structure.xrd",
  "provenance": {
    "label": "official_like_curated",
    "source": null,
    "official_pass_eligible": false
  },
  "input": {
    "type": "cif_or_poscar",
    "direct_uploadable": true,
    "max_sites": 128
  },
  "expected_artifacts": [
    "xrd_pattern.json",
    "xrd_plot.json",
    "summary.md",
    "recipe.json"
  ],
  "exact_checks": {
    "tool_id": "structure.xrd",
    "radiation": "CuKa",
    "security.contains_javascript": false,
    "security.external_urls": [],
    "security.external_urls_allowed": false
  },
  "numeric_checks": {
    "peak_count": {
      "mode": "range_or_exact"
    },
    "selected_two_theta_deg": {
      "mode": "tolerance",
      "tolerance": 0.02
    },
    "relative_intensity": {
      "mode": "tolerance",
      "tolerance": 0.5
    }
  },
  "metadata_checks": {
    "schema_version": "required",
    "limits": "required",
    "warnings": "allowed"
  },
  "pass_claim_policy": {
    "official_pass_claimed": false,
    "requires_direct_replay": true
  }
}
```

## 3. RDF Template

```json
{
  "case_id": "rdf_small_crystal",
  "target_tool": "structure.rdf",
  "provenance": {
    "label": "official_like_curated",
    "source": null,
    "official_pass_eligible": false
  },
  "input": {
    "type": "cif_or_poscar_or_structure_json",
    "direct_uploadable": true,
    "max_sites": 128,
    "requires_pbc": [true, true, true]
  },
  "expected_artifacts": [
    "rdf.json",
    "rdf_plot.json",
    "summary.md",
    "recipe.json"
  ],
  "exact_checks": {
    "tool_id": "structure.rdf",
    "normalization": "number_density",
    "security.contains_javascript": false,
    "security.external_urls": [],
    "security.external_urls_allowed": false
  },
  "numeric_checks": {
    "bin_count": {
      "mode": "exact"
    },
    "r_grid": {
      "mode": "tolerance",
      "tolerance": 0.000001
    },
    "selected_g_r_values": {
      "mode": "tolerance",
      "tolerance": 0.000001
    }
  },
  "metadata_checks": {
    "schema_version": "required",
    "limits": "required",
    "warnings": "allowed"
  },
  "pass_claim_policy": {
    "official_pass_claimed": false,
    "requires_direct_replay": true
  }
}
```

## 4. Template Rules

- Security fields are exact and mandatory.
- Tool id, schema version, artifact filenames, and chart type are exact.
- Metadata such as local job ids, artifact ids, storage keys, timestamps, and content hashes are metadata-only unless a later phase pins them.
- Numeric tolerances must be justified per case.
- No template is a PASS claim.
