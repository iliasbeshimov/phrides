# Experimental Code Archive

This directory contains experimental implementations and prototypes that were developed during the project evolution but are not currently used in production.

## Purpose

These files are preserved for:
- **Historical reference** - Understanding the evolution of the detection strategies
- **Learning** - Seeing different approaches that were attempted
- **Potential future use** - Ideas that might be valuable later
- **Code salvaging** - Specific functions or patterns that might be reused

## Directory Structure

### `form_detectors/`
Experimental form detection implementations:
- `simple_form_detector.py` - Early simple detection approach
- `smart_form_detector.py` - Experimental "smart" variant
- `stealth_form_detector.py` - Anti-detection focused variant

**Production form detector:** `src/automation/forms/enhanced_form_detector.py` (90%+ success rate)

### `contact_finders/`
Experimental contact page discovery implementations:
- `creative_contact_hunter.py` - Alternative contact page discovery
- `enhanced_intelligent_contact_finder.py` - Enhanced variant

**Production contact finder:** `src/automation/forms/intelligent_contact_finder.py`

## Important Notes

⚠️ **These files are NOT maintained and may be outdated**
- Dependencies may have changed
- APIs may have evolved
- Patterns may not reflect current best practices

✅ **Production code locations:**
- Form Detection: `src/automation/forms/enhanced_form_detector.py`
- Contact Finding: `src/automation/forms/intelligent_contact_finder.py`
- Form Submission: `src/automation/forms/form_submitter.py`
- Human-like Filling: `src/automation/forms/human_form_filler.py`

## When to Use These Files

- **Reference implementation details** that might be useful
- **Extract specific patterns or heuristics** that proved valuable
- **Understand design decisions** and why certain approaches were chosen

## When NOT to Use These Files

- ❌ Don't import these directly into production code
- ❌ Don't assume these work with current dependencies
- ❌ Don't base new features on outdated approaches

## Archival Date

**Archived:** October 30, 2025 (v1.0.0)
**Reason:** Code cleanup - consolidating to production implementations
**Context:** Phase 1 of refactoring plan based on code review feedback
