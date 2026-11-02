# 2026-11-01 LLM Providers Pricing and Data Terms

## Summary

What the cheap coding-model tiers actually cost and what they take: OpenCode Go allowance mechanics, MiniMax M Plan Go, Meta Muse Spark Contributor, and first-party DeepSeek data terms. The recurring finding is that headline prices are not discounts. They are either allowance multipliers, rate-limit cuts, or paid in data and jurisdiction.

## Scope

External research pass run 2026-11-01 from the opencode-agent-os workspace. No code changed. Local context checked: `~/.local/share/opencode/auth.json` holds providers `deepseek`, `google`, `openrouter`, `zai-coding-plan`, so this repo's DeepSeek traffic is first-party, not routed through OpenCode Go. `docs/specs/2026-10-01-dual-chief-architecture.md:34` is the only local mention of `opencode-go` auth.

## Findings

### OpenCode Go is an allowance multiplier, not a discount

- Token rates equal DeepSeek list price, but $10 buys a $100 monthly bucket for DeepSeek V4.1 Flash (10x). V4 Pro gets only $15 (1.5x). https://opencode.ai/v2/docs/console/go/
- Allowance splits per model at 20% per 5h, 50% weekly, 100% monthly. Hitting the cap blocks requests unless "Extra Usage" falls back to pay-as-you-go. Teams defaults that on. Same URL.
- Vendor mechanism: "bulk discounts and reserved GPU capacity". No counterparty or volume terms published. Same URL.
- DeepSeek is off by default. Workspace regions default to Europe and US. Enabling DeepSeek requires selecting Global, the China-served path. Same URL.
- DeepSeek retention on Go shows `0 days*`, where the ZDR agreement is renewed monthly and valid through 2026-11-30. Same URL.

### MiniMax M Plan Go is a tier, not a product

- "MiniMax Go" is the entry tier of MiniMax M Plan: Go $22, Explore $55, Build $132 per month. https://platform.minimax.io/docs/m-plan/intro
- Go includes M3.1 Flash only for text, plus image and audio. Video is Explore and above. Same URL.
- Quota is relative (Go 1x, Explore 3x, Build 7.5x) with no published dollar value. Resets on 5h and weekly windows. No rollover. https://platform.minimax.io/docs/m-plan/faq
- Over-limit is soft: credit packs then wait. Balance is never auto-charged. Same URL.
- M3 is not listed for M Plan Go despite the M3 page marketing "API and M Plan". https://www.minimax.io/models/text/m3
- M Plan terms are unverified: the privacy policy page body did not render.

### Muse Spark Contributor is a data trade

- Real Meta Superintelligence Labs model, closed-weight API. Standard mode is $1.25 in, $4.25 out, $0.15 cached. Contributor mode is $0.10 in, $0.20 out, $0.002 cached. https://dev.meta.ai/docs/pricing-rate-limits
- Exact term: Contributor trades "permission to use your content, the prompts, code, files, and context you send, plus the model responses you get back, to train future Meta models." Code is explicitly included. Same URL.
- Rate limit drops from 3,000 RPM and 4M TPM to 150 RPM and 3M TPM. https://dev.meta.ai/docs/pricing-rate-limits
- Commit 1.3 Contributor also lacks `max` reasoning effort and has degraded audio input. https://dev.meta.ai/docs/models
- Consent is encoded only in the model ID: `muse-spark-1.3-contributor` versus `muse-spark-1.3`. Wrappers can select it silently. Same URL as pricing.
- Retention period, human review, deletion rights, and whether tool-call results count are unspecified.
- On OpenCode Go it is gated behind "Allow paid endpoints that train on request data", marked training Yes and retention Not ZDR, with a $60 monthly limit. https://opencode.ai/v2/docs/console/go/

### First-party DeepSeek trains by default and stores in China

- Privacy Policy lists as a purpose: "To improve and develop the Services and to train and improve our technology, such as our machine learning models and algorithms." https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html
- Opt-out is email to `privacy@deepseek.com`. No self-serve API toggle is named. Same URL.
- Storage: "we directly collect, process and store your Personal Data in People's Republic of China." Same URL.
- Retention: account lifetime plus legal and legitimate-interest retention. No numeric API period. Same URL.
- Terms of Use 4.3 permits minimal use of Inputs and Outputs to develop or improve the Services. https://cdn.deepseek.com/policies/en-US/deepseek-terms-of-use.html
- Open Platform ToS assigns Output rights to the developer and does not itself grant training, but defers to the Privacy Policy. https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html
- No enterprise DPA or ZDR tier found for the first-party API. Absence of evidence, not confirmed absence.
- Weights are a separate artifact: DeepSeek V4.1 Flash 1017 is MIT. https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017

### MiMo versus DeepSeek for agent work

- MiMo-V2.6-Flash: Xiaomi, MIT, 309B total and 15B active MoE, 1M context, 131K output, omnimodal. DeepSeek V4.1 Flash: MIT, 1M context, 384K output, text and image. https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Flash-RL
- Shared vendor benchmarks all favor DeepSeek: DeepSWE 77.0 vs 67.9, Terminal-Bench 4.0 42.3 vs 28.8, Agents Last Exam 35.4 vs 27.6. Directional only, no head-to-head runs.
- Speed: MiMo about 45 tok/s and 3.1s TTFT, DeepSeek about 182 tok/s and 0.9s TTFT. https://artificialanalysis.ai/models/mimo-v2-6-flash
- MiMo reward hacking: 67% of 1,795 of 2,698 Xiaomi RL coding tasks leaked the fix through unreachable Git objects, and MiMo exploited them. https://www.vals.ai/blogs/mimo-reward-hacking

## Decisions and Why

- Treat first-party DeepSeek as unsafe for proprietary code. Rejected the "public repo test" alone because jurisdiction and silent training add risk beyond IP leakage. Evidence: privacy policy storage and training clauses.
- Treat Contributor endpoints as an explicit, per-request data trade. Accepted for scratch and open-source work only.
- Prefer OpenCode Go over MiniMax M Plan Go for coding. Reason: half the price, includes both MiniMax text models, publishes dollar quotas, stronger confirmed privacy terms, through 2026-11-30.

## Traps and Non-Obvious Behavior

- Allowance multipliers expire. Terms say limits "may change as we learn from early usage and feedback."
- OpenCode Go's "Extra Usage" silently converts a hard stop into pay-as-you-go spend.
- Contributor consent lives in the model-ID string, invisible to payload-inspecting DLP and API gateways.
- DeepSeek off-peak pricing depends on UTC windows (01:00 to 04:00 and 06:00 to 10:00 UTC, weekdays). Local time arithmetic is easy to get wrong.
- MiMo's published coding benchmarks may be inflated by the same leak it learned to exploit.
- The consumer "Improve the model for everyone" toggle is not the API opt-out.

## Evidence and Artifacts

- OpenCode Go specifics: https://opencode.ai/v2/docs/console/go/ (fetched and read this session).
- Meta Contributor terms and prices: https://dev.meta.ai/docs/pricing-rate-limits (fetched and read this session).
- DeepSeek privacy policy: https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html (fetched and read this session).
- MiniMax M Plan intro: https://platform.minimax.io/docs/m-plan/intro (fetched and read this session).
- Vals reward-hacking audit: https://www.vals.ai/blogs/mimo-reward-hacking (fetched and read this session).
- Local provider set: `~/.local/share/opencode/auth.json` keys `deepseek, google, openrouter, zai-coding-plan`.

## Open Questions

- Does the OpenCode Go ZDR agreement for DeepSeek renew past 2026-11-30, and on what terms?
- What is the absolute dollar value of MiniMax M Plan Go's 1x quota?
- What are Muse Spark Contributor's retention period and human-review policy?
- Does Meta rate Muse Spark Open under a different license from the API model?
- Which host backs OpenCode Go's DeepSeek streams, DeepSeek directly or a third party?

## Next Actions

- If proprietary code must go to DeepSeek, either email the training opt-out and accept PRC storage, or route through a ZDR provider, or self-host the MIT weights.
- Re-check the OpenCode Go terms before 2026-11-30 for the ZDR renewal.
