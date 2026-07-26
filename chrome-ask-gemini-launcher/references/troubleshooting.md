# Troubleshooting

## What This Launcher Fixes

The launcher starts real Google Chrome with Gemini in Chrome / Glic feature flags. This can restore the Ask Gemini button when the local profile is eligible but Chrome's visible UI is gated by rollout, locale, country filtering, or a missing flag.

It does not make an ineligible Google account eligible. Gemini in Chrome can still depend on Google's server-side rollout, supported country or region, age/account requirements, and account verification state.

## Core Flags

Enable:

- `Glic`
- `GlicHorizontalTabToolbarButton`
- `GlicToolbarButtonLocation:glic-toolbar-button-location/RightOfOmnibox`
- `GlicActorUi`
- `GlicDefaultTabContextSetting`
- `GlicDefaultToLastActiveConversation`
- `GlicExperimentalTriggering`
- `GlicUseToolbarHeightSidePanel`
- `SyncGeminiThread`

Disable:

- `GlicCountryFiltering`
- `GlicUseSessionCountryForFiltering`
- `GlicLocaleFiltering`

Vertical tabs, when requested or already enabled:

- `VerticalTabsLaunch`
- `VerticalTabs`

## Common Findings

- `browser.gemini_settings = 0`: Gemini is allowed locally.
- `glic.pinned_to_tabstrip = true`: Gemini should be pinned if the feature is available.
- `profile.info_cache.<profile>.is_glic_eligible = true`: The profile has a local eligibility signal.
- `is_consented_primary_account = false`: Chrome may see the account as signed in but not fully consented/synced. This can correlate with verification prompts.

## Dock Limitations

macOS attributes the running process to Google Chrome, because the launcher starts the real Chrome app. The launcher can have a distinct Dock icon for launching, but the running indicator may appear under Chrome itself. Avoid modifying the official Chrome app bundle to force Dock identity; that can trigger account verification and breaks on Chrome updates.

## If "Verify It's You" Appears

Do not bypass it. Ask the user to complete verification manually in Chrome. If verification started after patching the Chrome app bundle, restore the official Chrome binary from backup or reinstall Chrome, then use this separate launcher approach.

## If Ask Gemini Still Does Not Appear

1. Ensure Chrome was fully closed before using the launcher.
2. Re-run diagnostics and confirm the Chrome process includes `--enable-features=...Glic...`.
3. Confirm the user is in the intended Chrome profile with `--profile-directory`.
4. Ask the user to complete Google verification if prompted.
5. Explain that Google server-side rollout or region/account gating may still hide the feature.
