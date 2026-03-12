# i18n: Add German and French

**Status**: planned
**Milestone**: M4a-Feed-Infrastructure
**Priority**: nice-to-have
**Depends on**: (none)

## Summary

Add German (de) and French (fr) translation files to the existing i18n system. Currently supports Italian (default) and English.

## Requirements

- [ ] Create `frontend/src/i18n/de.json` with German translations
- [ ] Create `frontend/src/i18n/fr.json` with French translations
- [ ] Add language options to the settings page language selector
- [ ] Verify all UI strings are covered (use Italian file as reference)

## Technical Notes

- i18n system is JSON-based, one file per language
- Language selector is in the Settings page
- Preference stored in localStorage
