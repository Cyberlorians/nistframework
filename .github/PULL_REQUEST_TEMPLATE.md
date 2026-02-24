## What does this PR do?

<!-- Brief description of the change -->

## NIST Control(s) affected

<!-- e.g., 3.1.1, 3.14.2 -->

## Type of change

- [ ] New alignment (adding a KQL mapping to an existing control)
- [ ] New control (adding a new practice YAML file)
- [ ] Fix/improvement to an existing KQL query
- [ ] Metadata fix (control name, family, product name, table name)
- [ ] Documentation update

## Checklist

- [ ] I only edited files in `practices/` (outputs are auto-generated)
- [ ] My YAML passes `python scripts/validate.py` locally
- [ ] KQL follows the 5-part convention (Objective → Part 0–5)
- [ ] Dynamic targeting uses `dynamic([])` with `array_length() == 0` pattern
- [ ] I tested my KQL in a Sentinel workspace or MDE Advanced Hunting
- [ ] Schema field names are current (checked against Microsoft Learn)
- [ ] `workload_integration` and `event_reference` links are valid (if provided)

## KQL testing evidence

<!-- Optional: paste a screenshot or describe your test results -->

## References

<!-- Link to Microsoft Learn docs, schema references, or related issues -->
