# dsh-protest-deadline — Verificação de datas e prazos do registo de impugnações e denúncias

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-protest-deadline` lê um registo de impugnações e denúncias (质疑与投诉台账) —o cabeçalho do projeto mais uma linha por impugnação— e verifica o que um registo desses pode sustentar mecanicamente: se está registada a data de apresentação da impugnação ou a data da resposta, se as datas são analisáveis e seguem uma ordem, se a resposta cai dentro do prazo que o próprio registo declara, se cada estado vem do seu próprio vocabulário, se os números de impugnação não se repetem e se o cabeçalho nomeia o projeto de contratação.

## Como é a saída

![Terminal demo of dsh-protest-deadline: real output over its PD-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-protest-deadline/main/docs/assets/dsh-protest-deadline-demo.png)

Saída real deste plugin sobre o seu próprio fixture de teste `PD-002` — não é uma simulação. O pacote de regras não inventa citações, por isso cada achado nomeia a cláusula aplicada e avisa que o seu texto não foi obtido.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| Uma linha deixa em branco tanto a data de apresentação como a da resposta. Isso é reportado? | Sim. `PD-001` exige que em cada linha esteja preenchido pelo menos um de `raisedAt` e `replyAt`, e reporta a linha em que ambos estão vazios. Verifica apenas que um dos dois está preenchido, não se a impugnação foi apresentada dentro do prazo legal: isso exige a data em que o fornecedor teve conhecimento, a data da notificação e uma contagem em dias úteis que o registo normalmente não traz. |
| A data da resposta está escrita antes da data de apresentação. Isso é detetado? | `PD-002` compara linha a linha a data de apresentação com a da resposta e reporta `raisedAt` quando é posterior a `replyAt`; o mesmo dia não conta como posterior. Um valor que não consegue analisar —`2026年3月15日`, por exemplo, quando `2026-03-15`, `2026/3/15` ou `2026-03-15 09:30` são lidos— é reportado nessa linha em vez de ser deixado passar em silêncio. A regra apenas ordena as duas datas que o registo contém. |
| A nossa resposta saiu depois do prazo de resposta registado no registo. Foi tardia? | `PD-003` não fixa qualquer número de dias e não pode dizer «tardia»: compara a data real da resposta com o prazo escrito na própria coluna `replyDueAt` do registo, pelo que um achado significa «isto não concorda com o prazo que registou». Com essa coluna vazia não há termo de comparação e a regra aparece em `skipped`, em vez de presumir um prazo. |
| A coluna de estado diz 已答复 e nada foi reportado sobre ela. Porquê? | `PD-005` confronta o estado com o vocabulário que configurar, e `values` vem vazio, pelo que tal como é entregue a regra aparece em `skipped` —a escolha dos valores cabe à sua instituição, não ao motor— em vez de passar em silêncio. Preencha `values` com a sua própria lista (待答复, 已答复, 已投诉, 已撤回, …) e qualquer valor fora dela será reportado linha a linha. Verifica apenas se o valor consta da lista, nunca como a impugnação deve ser tratada. |
| O cabeçalho nomeia o projeto mas não traz a data de apresentação ao nível do cabeçalho. Falta algo? | Não. `PD-006` verifica no cabeçalho apenas o projeto de contratação: o seu `fields` predefinido é `[project]`, porque a data de apresentação é normalmente uma coluna por linha. Se o seu formulário a declara no cabeçalho, a própria nota da regra indica pôr `fields` em `[project, raisedAt]`. A falta do projeto é reportada contra o cabeçalho, não contra uma linha. |
| O mesmo número de impugnação aparece em duas linhas. | `PD-007` reporta a segunda linha e nomeia a primeira, comparando os números sem considerar espaços. Uma repetição costuma significar que a mesma impugnação foi registada duas vezes ou que um número foi copiado mal: distingui-lo é uma decisão humana. Se o registo não tiver coluna de número, a regra reporta que não se aplica em vez de passar. |

## Normas que segue

| Documento | Número | Regras que o citam |
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

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-protest-deadline
dsh --profile <name> --dump-config | grep 'dsh-protest-deadline'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/protest-deadline.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-protest-deadline
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-protest-deadline contributors.
