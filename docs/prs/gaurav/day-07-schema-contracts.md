# Day 07 - Team sync: shared schema contracts and join strategy for all four datasets

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-07-schema-contracts` |
| **Base** | `main` - stacked on `gaurav/day-06-completion-outliers` (merge PR 06 first) |
| **Roadmap** | Day 7 (Mon 03 Aug 2026) - *Team sync: review cleaned datasets, align schemas, and plan merge strategy.* |
| **Type** | `feat` |
| **Size** | 2 code files, +208 / -0 lines (docs excluded) |

## Summary

My deliverable for the week-1 team sync: `pipeline/schemas.py` defines one contract per dataset (grain, primary key, required and numeric columns, foreign keys) that every workstream validates against before merging.

## Why

- Onboarding (Gaurav), tool usage (Vedant) and support tickets (Aayush) are cleaned separately; they must agree on keys and columns before the week-2 merges.
- Merge strategy agreed: join on `employee_id`; aggregate the 1:N tables per employee *before* joining.

## What changed

- `CONTRACTS` for employees, onboarding, tool_usage and support_tickets.
- `check_contract()` (missing/extra columns, null or duplicate keys, non-numeric values) and `check_references()` (orphan foreign keys).
- CLI: `python -m pipeline.schemas` exits 1 on errors.
- `tests/test_schemas.py`: 7 tests.

## How to test

```bash
python -m pipeline.schemas
pytest tests/test_schemas.py
```

## Result

All four committed datasets satisfy their contracts: no orphan keys, no duplicate IDs.

## Diff highlight

`pipeline/schemas.py` (excerpt)

```diff
+def check_contract(df: pd.DataFrame, contract: DatasetContract) -> list[ContractIssue]:
+    def issue(check: str, detail: str, severity: str = "error") -> ContractIssue:
+        return ContractIssue(contract.name, check, detail, severity)
+
+    missing = [c for c in contract.required_columns if c not in df.columns]
+    if missing:  # nothing else can be checked reliably without the agreed columns
+        return [issue("required_columns", "missing " + ", ".join(missing))]
+
+    issues = []
+    extra = [str(c) for c in df.columns if c not in contract.required_columns]
+    if extra:
+        issues.append(issue("unexpected_columns", ", ".join(extra), "warning"))
+    key = list(contract.primary_key)
+    null_keys = int(df[key].isna().any(axis=1).sum())
+    if null_keys:
+        issues.append(issue("primary_key", f"{null_keys} rows with a null {'/'.join(key)}"))
+    duplicate_keys = int(df.dropna(subset=key).duplicated(subset=key).sum())
+    if duplicate_keys:
+        issues.append(issue("primary_key", f"{duplicate_keys} duplicate {'/'.join(key)} values"))
+    for col in contract.numeric_columns:
+        bad = int((df[col].notna() & pd.to_numeric(df[col], errors="coerce").isna()).sum())
+        if bad:
+            issues.append(issue("numeric", f"{bad} non-numeric values in {col}"))
+    return issues
+
+
+def check_references(frames: Mapping[str, pd.DataFrame]) -> list[ContractIssue]:
+    """Every foreign key must point at an existing parent row."""
+    issues = []
+    for name, contract in CONTRACTS.items():
+        if name not in frames:
+            continue
+        for column, target in contract.references:
+            table, target_column = target.split(".")
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pipeline/schemas.py` | 148 | 0 |
| `tests/test_schemas.py` | 60 | 0 |
| `docs/prs/gaurav/day-07-schema-contracts.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
