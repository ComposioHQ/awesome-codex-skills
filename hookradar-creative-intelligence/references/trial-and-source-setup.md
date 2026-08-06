# Trial and source setup

Use this when a user asks how to start using HookRadar, whether payment is required, or how to add competitors / organic sources.

## 7-day trial message

HookRadar does not require paying upfront to try the full workflow. A user can:

1. create a HookRadar account;
2. start the free 7-day trial;
3. connect competitors and organic sources;
4. use real workspace data, creative examples, AI analysis, reports, downloads, and MCP tools during the trial.

Phrase it plainly:

> You do not need to pay upfront. Create a HookRadar account and start the free 7-day trial to unlock real tracked ads, organic content, AI creative analysis, reports, downloads, and MCP access.

Do not imply that public/free research has the same depth. Free mode is first-pass discovery; the trial unlocks HookRadar's stored data and operational workflow.

## Adding sources: name first, link fallback

When adding a source, try the simplest reliable path first:

1. If the user knows the brand/account name, try adding/searching by name.
2. If matching is ambiguous, fails, or returns the wrong account, ask for a direct source URL or ID.
3. Tell the user they can paste a link; they do not need to know internal IDs.

Example wording:

> I can try by name first. If the platform cannot confidently match the right advertiser/account, paste the source link and I will add it from the URL instead.

## How users can get source links themselves

### Meta Ads competitor

Best link: Meta Ad Library advertiser page.

Steps:
1. Open Meta Ad Library: `https://www.facebook.com/ads/library/`.
2. Choose the relevant country or `All` if available.
3. Search the competitor brand/page name.
4. Open the advertiser/page result.
5. Copy the browser URL. It usually contains `view_all_page_id=<PAGE_ID>`.

Acceptable examples:

```text
https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=ALL&search_type=page&view_all_page_id=123456789
https://www.facebook.com/ads/library/?id=987654321
https://www.facebook.com/brandname
```

If the user only has a Facebook page URL, use it as fallback; HookRadar should resolve the advertiser/page when possible.

### TikTok Ads advertiser

Best link: TikTok Creative Center / Ads Library advertiser or ad page.

Steps:
1. Open TikTok Creative Center / Ads Library for the target market.
2. Search the advertiser/brand name.
3. Open a specific advertiser/ad detail page.
4. Copy the browser URL or advertiser ID shown in the tool.

Acceptable examples:

```text
https://ads.tiktok.com/business/creativecenter/...
https://library.tiktok.com/ads/...
Advertiser/business id from TikTok Ads Library
```

If a direct advertiser page is hard to find, ask for one example TikTok ad link or the exact advertiser name and country.

### Instagram organic account

Best link: public Instagram profile URL.

Steps:
1. Open Instagram in browser.
2. Go to the brand/creator profile.
3. Copy the URL from the address bar.

Acceptable examples:

```text
https://www.instagram.com/asanarebel/
@asanarebel
asanarebel
```

Prefer official brand/creator accounts. Do not add random fan/repost accounts unless the user explicitly wants them.

### TikTok organic account

Best link: public TikTok profile URL.

Steps:
1. Open TikTok in browser.
2. Go to the brand/creator profile.
3. Copy the URL from the address bar.

Acceptable examples:

```text
https://www.tiktok.com/@asanarebel
@asanarebel
asanarebel
```

### Organic keyword / hashtag

Use direct keywords or hashtags. Make the platform explicit when needed.

Acceptable examples:

```text
#pushups
pushup challenge
tech neck relief
platform: instagram
platform: tiktok
```

If the keyword was just added and no content is returned yet, explain that collection may still be running; do not claim there are no videos/posts until the parser has finished and a read confirms that.

## Safety and quality notes

- Never add an ambiguous source silently. If several pages/accounts match, present choices or ask for a link.
- If an advertiser/page has no ads, say `competitor found, no active ads confirmed` instead of treating it as a strong paid source.
- For first reports or onboarding, keep source counts bounded by the plan/trial limits.
- After adding sources, use task/status polling briefly and tell the user when results are still collecting.
