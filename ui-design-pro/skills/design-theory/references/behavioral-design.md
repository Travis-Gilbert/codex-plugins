# Behavioral Design

## Default Effects

**The choice that requires no action is taken most often.** When you set a default, you've made a decision on behalf of most users. This is powerful — and carries responsibility.

### Choosing Defaults

| Situation | Default strategy |
|-----------|-----------------|
| Email notifications | Off by default (opt-in) — respects user attention |
| Auto-save | On by default — users expect it, loss of work is costly |
| Dark/light mode | Follow OS preference (`prefers-color-scheme`) |
| Form pre-fill | Use last-used value for power users; leave blank for novices |
| Settings | Sensible defaults that work for 80% of users without configuration |

**Anti-pattern:** Pre-checked opt-in for newsletters, data sharing, or any permission. This is a dark pattern that trades short-term metrics for long-term trust.

---

## Progressive Disclosure

Show only what the user needs right now. Reveal complexity as users are ready for it.

### Levels of Disclosure

1. **Zero state**: Before the user has done anything — show the most important single action
2. **First use**: Reveal core functionality; defer advanced options
3. **After first success**: Reveal related features contextually
4. **Power user**: Keyboard shortcuts, batch operations, developer features

### Implementation Patterns

**Expandable sections**: "Advanced options ▼" — hides less-common fields until requested
**Tabs**: Separates configuration into distinct concern areas
**Contextual menus**: Right-click or "..." reveals operations relevant to the current object
**Onboarding flows**: Walk users through core features once, then show the full UI

### What to Never Disclose by Default

- Bulk operations on initial load (too intimidating)
- Deletion without confirmation
- Technical configuration (API keys, webhooks, database URLs)
- Features that require upgrade — show a locked state, not the feature itself

---

## Commitment and Consistency

Users tend to follow through on commitments they've made, especially public or written ones. Use this to reduce abandonment.

### Multi-Step Forms

Break complex processes into steps. Show progress (Step 2 of 4). Each completed step creates commitment to continue.

**Rules:**
- Each step should have a clear deliverable: "Tell us about yourself" / "Set up your workspace"
- Never hide step count — users feel deceived when steps appear unexpectedly
- Allow going back without losing data
- Save progress automatically between steps

### Onboarding Completion

Show a progress bar for profile completion or onboarding tasks. "Your profile is 60% complete" motivates completion without mandating it.

---

## Social Proof and Trust Signals

Users look to others' behavior when uncertain about their own. Social proof reduces anxiety in new or high-stakes interactions.

### Trust Signal Types

| Signal | Appropriate context |
|--------|-------------------|
| User count / review count | Adoption confidence ("10,000+ teams") |
| Star ratings | Quality confidence (marketplace, app stores) |
| Testimonials | Value confidence (landing pages, pricing) |
| Activity indicators | Freshness confidence ("Last updated 2 days ago") |
| Security badges | Transaction confidence (payment flows) |
| Company logos | Enterprise credibility |

### Anti-patterns

- Fake review counts or user numbers — users notice, and the trust cost when discovered is permanent
- "As seen on" with logos the user cannot verify
- Urgency that isn't real ("Only 3 left!" when stock is plentiful)

---

## Scarcity and Urgency

**Real scarcity and urgency are legitimate design signals.** Manufactured scarcity is a dark pattern.

Legitimate use:
- "Offer ends December 31" — real deadline
- "Only 2 seats left at this price" — real constraint
- "Your free trial ends in 3 days" — factual timeline

Dark pattern:
- Countdown timers that reset when you refresh
- "Low stock" on unlimited digital goods
- "Viewing now: 47 people" fabricated numbers

When using legitimate urgency, be specific and verifiable. "Sale ends Sunday" > "Limited time offer."

---

## Loss Aversion

**Users feel losses more strongly than equivalent gains.** Framing matters.

| Loss framing | Gain framing |
|-------------|-------------|
| "You'll lose access to premium features" | "Keep your premium features" |
| "Don't miss this" | "Get this" |
| "Risk going over budget" | "Stay on budget" |

Loss framing is appropriate when:
- Communicating genuine consequences of inaction
- Warning about data that will be permanently deleted
- Highlighting what a user will lose by downgrading

Loss framing is manipulative when:
- The consequence is trivial or not actually a loss
- It creates anxiety without offering a solution
- It's designed to override a user's deliberate decision to leave

---

## Reducing Friction

Every step a user must take to complete a task reduces completion rate. Friction is sometimes intentional (confirming destructive actions), but usually it's accidental.

### Friction Audit

For any flow, count the number of steps and ask: does each step add value for the user or only for the system?

**Reduce friction by:**
- Auto-filling known data (name, email for signed-in users)
- Removing optional fields from primary path (move to "optional" section)
- Remembering last selections
- Allowing guest checkout before requiring account creation
- Using OAuth / social login to eliminate password friction

**Accept friction for:**
- Destructive operations (delete, cancel subscription)
- Irreversible transactions (publishing, sending to large groups)
- High-security operations (changing password, payment methods)

---

## Habit Formation and Trigger-Action-Reward

Well-designed products create habits through a trigger → action → reward loop.

| Component | Definition | Design application |
|-----------|-----------|-------------------|
| **External trigger** | Notification, email, badge | Push notification, email digest, badge count |
| **Internal trigger** | Emotion or thought that prompts action | Context-aware prompt: "It's been 3 days since your last entry" |
| **Action** | The simplest behavior in anticipation of reward | Make the action dead simple — one tap, not five |
| **Reward** | What the user gets from the action | Show the value immediately: summary, progress, response |
| **Investment** | Data or effort that makes the product more valuable | Profile photo, preferences, history |

### Ethical Guardrails

Habit loops are powerful. Only design them around behaviors that genuinely benefit users. Social media and gambling maximize engagement at the expense of wellbeing. Design productivity and communication tools to help users accomplish goals and get out — not to maximize time-in-app.

---

## Onboarding Philosophy

The goal of onboarding is not to show users every feature. The goal is to deliver the product's core value promise as quickly as possible.

### The Aha Moment

Every product has an "aha moment" — the first time the user directly experiences the value. All onboarding should be optimized to reach this moment as fast as possible.

| Product type | Aha moment |
|-------------|-----------|
| Task manager | Creating first task and checking it off |
| Design tool | Seeing a design render in real time |
| Analytics | Seeing the first chart populated with real data |
| Collaboration | Seeing a teammate's real-time cursor |

Minimize all steps between sign-up and the aha moment. Every additional step reduces the chance of reaching it.

### Empty States as Onboarding

The first time a user opens an empty view, show them the value of what it could look like — not a blank slate.

```
Empty state structure:
  [Illustration]           ← Not decorative; shows the filled state
  [Headline]               ← What this space is for
  [Description]            ← One sentence on the value
  [Primary CTA]            ← The exact action to fill it
```

Never show an empty container with no guidance. That's a failure state, not a design.
