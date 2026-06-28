# Payments — by scenario

Activated when the project **sells something** (usually T3–T4).

## The governing fork — MoR vs PSP

**Who handles tax/VAT/GST compliance?**

- **Merchant of Record (MoR)** — the provider is the legal seller; they collect, file, and remit tax, and own chargebacks. Costs more (≈5–10%) but removes the compliance burden. **Default for a solo maker.**
- **Payment Service Provider (PSP)** — you are the merchant; the PSP only moves money; *you* calculate and file tax. Cheaper (≈2–3%) but you own compliance.

As a solo, India-based maker, **MoR-first** removes the biggest operational tax burden — and **Polar** is the standout: RBI-approved cross-border, pays out to Indian founders even without Stripe approval, developer-first React SDK.

## Default by scenario

| Scenario | Default | Why / alternative |
|---|---|---|
| Indie one-time digital product | **Polar** (MoR) | tax handled, ~10-min SDK embed; Lemon Squeezy if <$500K ARR (but its SDK is stale) |
| SaaS subscriptions (<$1M ARR) | **Polar** (MoR) | metering + tax included; Paddle if selling into 10+ countries |
| International scale ($1M+, B2B POs/VAT) | **Paddle** (MoR) | mature global VAT + B2B reverse-charge; Stripe if you have a tax team |
| India-domestic (UPI / RUPay) | **Razorpay** (PSP) | RBI-native; pair with Polar for international |
| Usage / metered (API credits) | **Stripe Billing** or **Polar** | Stripe has the richest metering; Polar is simpler + tax included |

## Rules

- **MoR by default** — only drop to a raw PSP when you have the tax tooling to handle compliance yourself.
- India-domestic sales need GST handling (18% above the turnover threshold) — Razorpay is native there; for international, let an MoR (Polar) absorb it.
- Don't build subscription/billing logic by hand — the provider owns proration, dunning, and tax.

**Deps** → always **import** (a hosted SDK). The doctrine choice is MoR-first, India-aware — not which package.
