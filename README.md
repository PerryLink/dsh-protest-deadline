# dsh-protest-deadline — Query and complaint register date and deadline check

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-protest-deadline` reads one query-and-complaint register (质疑与投诉台账) — the project header plus one row per query — and checks what such a register can be held to mechanically: that the date the query was raised or the date it was answered is recorded, that the dates parse and follow one another, that the reply falls inside the deadline the register itself states, that every status comes from your own vocabulary, that the query numbers are unique, and that the header names the procurement project.

## Install

```sh
dsh plugin --profile <name> add dsh-protest-deadline
dsh --profile <name> --dump-config | grep 'dsh-protest-deadline'
```

## What it looks like

![Terminal demo of dsh-protest-deadline: real output over its PD-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-protest-deadline/main/docs/assets/dsh-protest-deadline-hero.png)

![Animated terminal demo of dsh-protest-deadline](https://raw.githubusercontent.com/PerryLink/dsh-protest-deadline/main/docs/assets/dsh-protest-deadline-demo.gif)

Real output from this plugin over its own `PD-002` test fixture — not a mock-up. The rule pack ships no invented quotations, so a finding names both the clause it applied and the fact that the clause text was not obtained.

## What it answers

| You ask | What it answers |
|---|---|
| A row leaves both the date the query was raised and the date it was answered blank. Is that reported? | Yes. `PD-001` requires at least one of `raisedAt` and `replyAt` on every row and reports the row where both are empty. It checks only that one of the two is filled, not whether the query was raised inside the legal period: that needs the date the supplier knew of the harm, the service date and a working-day count a register usually does not carry. |
| The reply date is written earlier than the raise date. Is that caught? | `PD-002` compares the raise date with the reply date row by row and reports `raisedAt` when it is later than `replyAt`; the same day counts as not later. A value it cannot parse — `2026年3月15日`, say, where `2026-03-15`, `2026/3/15` or `2026-03-15 09:30` would be read — is reported on that row instead of being passed over quietly. The rule only orders the two dates the register carries. |
| Our reply went out after the reply deadline recorded in the register. Was it late? | `PD-003` hard-codes no day count and cannot say “late”: it compares the actual reply date with the deadline written in the register's own `replyDueAt` column, so a finding means “this disagrees with the deadline you recorded”. With that column empty there is nothing to compare against and the rule reports itself in `skipped`, rather than assuming a period. |
| The status column says 已答复, yet nothing came back for it. Why? | `PD-005` compares the status with the vocabulary you configure, and `values` ships empty, so as delivered the rule reports itself in `skipped` — the choice of values belongs to your institution, not to the engine — instead of passing silently. Fill `values` with your own list (待答复, 已答复, 已投诉, 已撤回, …) and any value not on it is reported row by row. It checks that the value is on the list, never how the query should be handled. |
| The header names the project but carries no header-level raise date. Is something missing? | No. `PD-006` checks the header for the procurement project only: its `fields` default to `[project]`, because the raise date is normally a per-row column. If your form does state it in the header, the rule's own note says to set `fields` to `[project, raisedAt]`. A missing project is reported against the header, not against a row. |
| The same query number appears on two rows. | `PD-007` reports the second row and names the first, comparing the numbers with whitespace ignored. A repeat usually means the same query was registered twice or a number was copied — telling those apart is a human call. If the register carries no number column, the rule reports that it does not apply rather than passing. |

## Standards it follows

| Document | Number | Cited by rules |
|---|---|---|
| 《政府采购质疑和投诉办法》 | 财政部令第94号（2017 年 12 月 26 日公布，自 2018 年 3 月 1 日起施行；六章四十五条。⚠️ 本令第四十五条同时废止财政部令第20号《政府采购供应商投诉处理办法》） | PD-001, PD-002, PD-003, PD-004, PD-005, PD-006, PD-007 |

**Boundary:** this plugin checks a **质疑与投诉台账** for what a register can be held to mechanically — that
the key dates are recorded, that they parse and follow one another, that a reply falls inside the deadline
the register itself states, that statuses come from your vocabulary, and that query numbers are unique. It
does **not** decide whether a query was filed in time, whether it should be accepted, or whether it should
be rejected. **Those calls need the purchaser or the finance department, the service dates, and a
working-day basis that a ledger usually does not record.**

> ### ⚠️ What the citation rests on
>
> **《政府采购质疑和投诉办法》(财政部令第94号) was obtained and read verbatim** — the whole text, six chapters
> and forty-five articles — and `rules/evidence/clause-verification.md` records what was quoted:
> article 10 (question within **7 working days**), article 13 (reply within **7 working days**), article 17
> (complaint within 15 working days **after the reply period expires**), article 21 (5 and 8 working days),
> article 26 (30 working days) and **article 42**, which fixes two calculation rules — 「期间开始之日，
> 不计算在期间内」 and a roll-over when the final day is a holiday. Article 45 also **repealed**
> 财政部令第20号, so this pack never cites it.
>
> **The rule `excerpt` fields still say "本次未取得", and every rule remains `warn` or `info`.** What this
> plugin checks is an internal register's dates and columns; the measure governs how purchasers and finance
> departments behave. Calling a blank column a `direct` breach of "shall reply within 7 working days" would
> dress a record-keeping gap up as a regulatory one. The government procurement law itself was not obtained.
>
> **This plugin hard-codes no day count, and the text now proves why.** The periods run in **working days**,
> article 42 excludes the opening day from the count and rolls the deadline forward off a holiday, and
> article 17 starts the complaint clock from the **expiry of the reply period** rather than the reply date —
> while a register usually records calendar dates only. So `PD-003` compares the actual reply date against the
> deadline **written in the register's own `答复期限` column**, and with that column empty it reports itself in
> `skipped`. Its finding says "this disagrees with the deadline you recorded", **not** "the reply is late".

## Compatibility

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-rc.2`. `engines.dsh` is declared as `>=0.2.1-0 <0.3.0` and is enforced by the host since 0.2.1 |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native` and `ptc`; for a year's register use `ptc` |

## What it does

Registers the `protest_deadline` tool. It reads one query-and-complaint register — the project header plus one
row per query — applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `PD-001` | a raise date or a reply date is recorded | warn | direct |
| `PD-002` | the reply date is not earlier than the raise date | warn | direct |
| `PD-003` | the reply falls inside the recorded deadline | info | local |
| `PD-004` | the complaint date is not earlier than the reply date | warn | direct |
| `PD-005` | the status comes from your vocabulary (off by default) | info | local |
| `PD-006` | the register names its procurement project | warn | principle |
| `PD-007` | query numbers are unique in the register | warn | principle |
## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/protest-deadline.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `PD-003` reads the register's `答复期限` / `replyDueAt` column. Compute that deadline under 财政部令第94号
  (working days) and write it into the ledger; the plugin will not derive it.
- `PD-005` `values` — your status vocabulary, e.g. `[待答复, 已答复, 已投诉, 已处理完毕, 已撤回]`.
- `PD-002` and `PD-004` compare date pairs; to also check the reply-to-complaint direction, add a second
  rule with `field: replyAt` and `notAfterField: complaintAt`.

## Material format

The tool accepts JSON or YAML:

```yaml
project: 某某设备采购项目
projectNo: ZC-2026-018
agency: 某某采购代理机构
rows:
  - { 序号: ZY-2026-001, 质疑人: 某某科技有限公司, 质疑提出日期: 2026-03-02,
      答复期限: 2026-03-09, 实际答复日期: 2026-03-06, 投诉日期: 2026-03-12, 处理状态: 已答复 }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens; the register's own
column names are kept, so a finding names the column it read. Dates may be `2026-03-02` or
`2026-03-02 09:30`.

## Rule sources

Rule data lives in `rules/protest-deadline.yaml`. The pack's header states the citation gap in full, and each
rule's `note` repeats the part that matters for that rule. The load-time guard that normally enforces "an
excerpt must be a real quotation of at least eight characters" cannot tell a quotation from a description —
so this pack leans on the header, the per-rule notes and a test that asserts every `excerpt` admits the gap.

## Troubleshooting

- **`PD-003` reports itself as skipped.** The register records no reply deadline. That is deliberate: the
  statutory period is counted in working days and the plugin will not convert calendar dates into it.
- **`PD-003` fires but I consider the reply timely.** The register's `答复期限` disagrees with the actual
  reply date. Either the deadline column was computed wrongly or the reply date is wrong.
- **`PD-005` never runs.** Its vocabulary is empty; fill it with your register's status values.
- **`PD-002` fires on dates I can read.** The reader accepts `2026-03-02` and `2026-03-02 09:30`;
  `2026年3月2日` is reported as unparseable on purpose.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-protest-deadline@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-protest-deadline   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and
the check engine, and the rule pack declares every check.

## PerryLink DSH Plugin Family

This project is part of the DeepSeek Harness plugin family from [PerryLink](https://github.com/PerryLink). The roster stays collapsed below so every README keeps a short first screen; expand it to see every row and its status.

<details>
<summary>Expand all plugins</summary>

| Plugin | Status |
|---|---|
| **[dsh-aqua-input-check](https://github.com/PerryLink/dsh-aqua-input-check)** |  |
| **[dsh-archive-check](https://github.com/PerryLink/dsh-archive-check)** |  |
| **[dsh-auto-review](https://github.com/PerryLink/dsh-auto-review)** |  |
| **[dsh-autotier](https://github.com/PerryLink/dsh-autotier)** |  |
| **[dsh-bid-ca-precheck](https://github.com/PerryLink/dsh-bid-ca-precheck)** |  |
| **[dsh-bid-qual-check](https://github.com/PerryLink/dsh-bid-qual-check)** |  |
| **[dsh-cert-mcp](https://github.com/PerryLink/dsh-cert-mcp)** |  |
| **[dsh-checkpoint-rewind](https://github.com/PerryLink/dsh-checkpoint-rewind)** |  |
| **[dsh-click](https://github.com/PerryLink/dsh-click)** |  |
| **[dsh-composer-history](https://github.com/PerryLink/dsh-composer-history)** |  |
| **[dsh-contract-stance](https://github.com/PerryLink/dsh-contract-stance)** |  |
| **[dsh-customs-doc-check](https://github.com/PerryLink/dsh-customs-doc-check)** |  |
| **[dsh-data-quality](https://github.com/PerryLink/dsh-data-quality)** |  |
| **[dsh-demurrage-ledger](https://github.com/PerryLink/dsh-demurrage-ledger)** |  |
| **[dsh-doublecheck](https://github.com/PerryLink/dsh-doublecheck)** |  |
| **[dsh-drill-script-check](https://github.com/PerryLink/dsh-drill-script-check)** |  |
| **[dsh-eia-guide-check](https://github.com/PerryLink/dsh-eia-guide-check)** |  |
| **[dsh-emergency-plan](https://github.com/PerryLink/dsh-emergency-plan)** |  |
| **[dsh-essay-rubric-check](https://github.com/PerryLink/dsh-essay-rubric-check)** |  |
| **[dsh-evidence-check](https://github.com/PerryLink/dsh-evidence-check)** |  |
| **[dsh-export-ctl-check](https://github.com/PerryLink/dsh-export-ctl-check)** |  |
| **[dsh-fast](https://github.com/PerryLink/dsh-fast)** |  |
| **[dsh-fmea-table-check](https://github.com/PerryLink/dsh-fmea-table-check)** |  |
| **[dsh-forecast-penalty](https://github.com/PerryLink/dsh-forecast-penalty)** |  |
| **[dsh-fund-research](https://github.com/PerryLink/dsh-fund-research)** |  |
| **[dsh-github](https://github.com/PerryLink/dsh-github)** |  |
| **[dsh-gongwen-flow-check](https://github.com/PerryLink/dsh-gongwen-flow-check)** |  |
| **[dsh-gongwen-word-check](https://github.com/PerryLink/dsh-gongwen-word-check)** |  |
| **[dsh-guard-plan-qc](https://github.com/PerryLink/dsh-guard-plan-qc)** |  |
| **[dsh-hazchem-check](https://github.com/PerryLink/dsh-hazchem-check)** |  |
| **[dsh-hazplan-check](https://github.com/PerryLink/dsh-hazplan-check)** |  |
| **[dsh-hidden-risk-map](https://github.com/PerryLink/dsh-hidden-risk-map)** |  |
| **[dsh-hs-classify](https://github.com/PerryLink/dsh-hs-classify)** |  |
| **[dsh-icd-rule-check](https://github.com/PerryLink/dsh-icd-rule-check)** |  |
| **[dsh-industry-research](https://github.com/PerryLink/dsh-industry-research)** |  |
| **[dsh-lawcite-adapter](https://github.com/PerryLink/dsh-lawcite-adapter)** |  |
| **[dsh-laya](https://github.com/PerryLink/dsh-laya)** |  |
| **[dsh-lc-doc-check](https://github.com/PerryLink/dsh-lc-doc-check)** |  |
| **[dsh-learning-gap-check](https://github.com/PerryLink/dsh-learning-gap-check)** |  |
| **[dsh-library](https://github.com/PerryLink/dsh-library)** |  |
| **[dsh-local-ai](https://github.com/PerryLink/dsh-local-ai)** |  |
| **[dsh-lsp-actions](https://github.com/PerryLink/dsh-lsp-actions)** |  |
| **[dsh-mask](https://github.com/PerryLink/dsh-mask)** |  |
| **[dsh-mcp-panel](https://github.com/PerryLink/dsh-mcp-panel)** |  |
| **[dsh-medrec-qc](https://github.com/PerryLink/dsh-medrec-qc)** |  |
| **[dsh-memento](https://github.com/PerryLink/dsh-memento)** |  |
| **[dsh-nsfc-form-check](https://github.com/PerryLink/dsh-nsfc-form-check)** |  |
| **[dsh-nurse-record-check](https://github.com/PerryLink/dsh-nurse-record-check)** |  |
| **[dsh-observe](https://github.com/PerryLink/dsh-observe)** |  |
| **[dsh-origin-rvc-check](https://github.com/PerryLink/dsh-origin-rvc-check)** |  |
| **[dsh-ota-review-check](https://github.com/PerryLink/dsh-ota-review-check)** |  |
| **[dsh-output-styles](https://github.com/PerryLink/dsh-output-styles)** |  |
| **[dsh-paper-doc-adapter](https://github.com/PerryLink/dsh-paper-doc-adapter)** |  |
| **[dsh-permission-rules](https://github.com/PerryLink/dsh-permission-rules)** |  |
| **[dsh-permit-report-check](https://github.com/PerryLink/dsh-permit-report-check)** |  |
| **[dsh-pipeline-check](https://github.com/PerryLink/dsh-pipeline-check)** |  |
| **[dsh-pleading-draft](https://github.com/PerryLink/dsh-pleading-draft)** |  |
| **[dsh-plugin-doctor](https://github.com/PerryLink/dsh-plugin-doctor)** |  |
| **[dsh-plugin-guide](https://github.com/PerryLink/dsh-plugin-guide)** |  |
| **[dsh-plugin-kit](https://github.com/PerryLink/dsh-plugin-kit)** |  |
| **[dsh-plugin-upgrade](https://github.com/PerryLink/dsh-plugin-upgrade)** |  |
| **[dsh-policy-brief-draft](https://github.com/PerryLink/dsh-policy-brief-draft)** |  |
| **[dsh-power-loss-split](https://github.com/PerryLink/dsh-power-loss-split)** |  |
| **[dsh-power-ticket-check](https://github.com/PerryLink/dsh-power-ticket-check)** |  |
| **[dsh-ppap-check](https://github.com/PerryLink/dsh-ppap-check)** |  |
| **[dsh-protest-deadline](https://github.com/PerryLink/dsh-protest-deadline)** |  |
| **[dsh-railway-window](https://github.com/PerryLink/dsh-railway-window)** |  |
| **[dsh-repair-order-qc](https://github.com/PerryLink/dsh-repair-order-qc)** |  |
| **[dsh-research-report](https://github.com/PerryLink/dsh-research-report)** |  |
| **[dsh-review-reply-check](https://github.com/PerryLink/dsh-review-reply-check)** |  |
| **[dsh-rulefile-check](https://github.com/PerryLink/dsh-rulefile-check)** |  |
| **[dsh-safety-brief-check](https://github.com/PerryLink/dsh-safety-brief-check)** |  |
| **[dsh-score](https://github.com/PerryLink/dsh-score)** |  |
| **[dsh-session-sync](https://github.com/PerryLink/dsh-session-sync)** |  |
| **[dsh-site-log-check](https://github.com/PerryLink/dsh-site-log-check)** |  |
| **[dsh-skill-pack-security](https://github.com/PerryLink/dsh-skill-pack-security)** |  |
| **[dsh-soe-decision-check](https://github.com/PerryLink/dsh-soe-decision-check)** |  |
| **[dsh-soilwater-check](https://github.com/PerryLink/dsh-soilwater-check)** |  |
| **[dsh-sop-sync-check](https://github.com/PerryLink/dsh-sop-sync-check)** |  |
| **[dsh-spc-gbt-adapter](https://github.com/PerryLink/dsh-spc-gbt-adapter)** |  |
| **[dsh-talk](https://github.com/PerryLink/dsh-talk)** |  |
| **[dsh-tender-extract](https://github.com/PerryLink/dsh-tender-extract)** |  |
| **[dsh-tender-matrix](https://github.com/PerryLink/dsh-tender-matrix)** |  |
| **[dsh-test-drive](https://github.com/PerryLink/dsh-test-drive)** |  |
| **[dsh-ticktick](https://github.com/PerryLink/dsh-ticktick)** |  |
| **[dsh-translate](https://github.com/PerryLink/dsh-translate)** |  |
| **[dsh-warranty-calc](https://github.com/PerryLink/dsh-warranty-calc)** |  |
| **[dsh-budget](https://github.com/PerryLink/dsh-budget)** | 🧊 FROZEN — see the repo README |
| **[dsh-claude-move](https://github.com/PerryLink/dsh-claude-move)** | 🧊 FROZEN — see the repo README |
| **[dsh-defend](https://github.com/PerryLink/dsh-defend)** | 🧊 FROZEN — see the repo README |
| **[dsh-draw](https://github.com/PerryLink/dsh-draw)** | 🧊 FROZEN — see the repo README |
| **[dsh-reach](https://github.com/PerryLink/dsh-reach)** | 🧊 FROZEN — see the repo README |
| **[dsh-background-agents](https://github.com/PerryLink/dsh-background-agents)** | 🚫 RETIRED — see the repo README |
| **[dsh-session-pin](https://github.com/PerryLink/dsh-session-pin)** | 🚫 RETIRED — see the repo README |
| **[dsh-team-rooms](https://github.com/PerryLink/dsh-team-rooms)** | 🚫 RETIRED — see the repo README |

</details>## License

[Apache License 2.0](LICENSE) © 2026 dsh-protest-deadline contributors.
