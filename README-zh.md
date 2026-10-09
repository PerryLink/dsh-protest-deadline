# dsh-protest-deadline — 质疑与投诉期限核对

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-protest-deadline` 读取一份质疑与投诉台账——项目表头加每条质疑一行——核对这份台账能够被机械核对的部分：质疑提出日期或答复日期是否填写、日期是否可解析且先后关系是否成立、答复是否落在台账自己写明的答复期限内、处理状态是否取自本机构口径、质疑函编号是否唯一、表头是否写明采购项目。

## 实际输出长什么样

![Terminal demo of dsh-protest-deadline: real output over its PD-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-protest-deadline/main/docs/assets/dsh-protest-deadline-demo.png)

本插件对自己 `PD-002` 测试夹具的**真实输出**，不是示意图。规则库不伪造引文，因此每条发现都会同时写明所引条款，以及该条款原文本次未取得。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 某行的质疑提出日期与答复日期都空着，会被报出吗？ | 会。`PD-001` 要求每行 `raisedAt`、`replyAt` 至少填写一项，两者都为空即报出该行。它只核对这两个日期是否填了其中一个，不判断质疑是否在法定期限内提出——那要结合供应商知道或应知权益受损之日、送达日期与工作日计算，台账里通常记不全。 |
| 答复日期写在质疑提出日期之前，能查出来吗？ | 能。`PD-002` 逐行比较提出日期与答复日期，`raisedAt` 晚于 `replyAt` 时报出；同一天不视为晚于。解析不了的日期（例如写成 `2026年3月15日`，而 `2026-03-15`、`2026/3/15`、`2026-03-15 09:30` 都能读）会单独报出该行，不会静默放过。它只比较台账里这两个日期的先后。 |
| 我们的答复晚于台账里写的答复期限，算逾期吗？ | `PD-003` 不内置任何天数，也不下「逾期」的结论：它拿实际答复日期与台账自己写明的 `replyDueAt`（答复期限）相比，命中只表示「与你写在台账里的期限不一致」。该栏为空时没有可比对象，本条出现在 `skipped` 中，不会替你假定一个期限。 |
| 处理状态栏填了「已答复」，为什么什么都没报出来？ | `PD-005` 拿状态值与你在 `values` 里配置的取值清单比对，而该清单出厂为空，所以照原样交付时本条出现在 `skipped` 中——取值口径由本机构规定，不由引擎硬编码——而不是静默通过。把「待答复」「已答复」「已投诉」「已撤回」等本机构口径填入 `values` 后，不在册的值会逐行报出。它只核对取值是否在册，不判断该质疑投诉应当如何处理。 |
| 台账表头写了项目名称，但表头里没有质疑提出日期，算漏填吗？ | 不算。`PD-006` 默认只核对表头的 `project`（采购项目名称）一项，因为提出日期通常是逐条记录的列而非表头字段。若本机构表式确实在表头记录提出日期，按本条 note 的说明把 `fields` 改为 `[project, raisedAt]` 即可。缺项目名称时报出的是表头，不是某一行。 |
| 同一个质疑函编号在两行各出现一次。 | `PD-007` 会报出后一行并指出与哪一行重复，比较时忽略空白字符。编号重复通常意味着同一份质疑被登记了两次，或编号抄错——分辨是哪种需要人工确认。台账若没有编号列，本条报告「不适用」，而不是静默通过。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
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

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-protest-deadline
dsh --profile <name> --dump-config | grep 'dsh-protest-deadline'
```

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/protest-deadline.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-protest-deadline
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-protest-deadline contributors.
