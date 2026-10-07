# dsh-protest-deadline

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
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a year's register use `ptc` |

## What it does

Registers the `protest_deadline` tool. It reads one query-and-complaint register — the project header plus one
row per query — applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `PD-001` | a raise date or a reply date is recorded | warn | principle |
| `PD-002` | the reply date is not earlier than the raise date | warn | principle |
| `PD-003` | the reply falls inside the recorded deadline | info | local |
| `PD-004` | the complaint date is not earlier than the reply date | warn | principle |
| `PD-005` | the status comes from your vocabulary (off by default) | info | local |
| `PD-006` | the register names its procurement project | warn | principle |
| `PD-007` | query numbers are unique in the register | warn | principle |

## Install

```sh
pnpm pack
dsh plugin --profile <name> add ./dsh-protest-deadline-0.1.0.tgz
dsh --profile <name> --dump-config | grep 'dsh-protest-deadline'
```

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

## License

[Apache License 2.0](LICENSE) © 2026 dsh-protest-deadline contributors.
