# dsh-protest-deadline — Verificación de fechas y plazos del registro de impugnaciones y denuncias

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-protest-deadline` lee un registro de impugnaciones y denuncias (质疑与投诉台账) —la cabecera del proyecto más una fila por impugnación— y comprueba lo que un registro así puede sostener mecánicamente: que esté registrada la fecha de presentación de la impugnación o la fecha de su respuesta, que las fechas se puedan analizar y sigan un orden, que la respuesta caiga dentro del plazo que el propio registro declara, que cada estado provenga de su propio vocabulario, que los números de impugnación no se repitan y que la cabecera nombre el proyecto de contratación.

## Cómo se ve la salida

![Terminal demo of dsh-protest-deadline: real output over its PD-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-protest-deadline/main/docs/assets/dsh-protest-deadline-demo.png)

Salida real de este plugin sobre su propio fixture de prueba `PD-002` — no es un montaje. El paquete de reglas no inventa citas, así que cada hallazgo nombra la cláusula aplicada y advierte que su texto no se obtuvo.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| Una fila deja en blanco tanto la fecha de presentación como la de respuesta. ¿Se informa de ello? | Sí. `PD-001` exige que en cada fila esté relleno al menos uno de `raisedAt` y `replyAt`, e informa de la fila en la que ambos están vacíos. Solo comprueba que uno de los dos esté puesto, no si la impugnación se presentó dentro del plazo legal: eso exige la fecha en que el proveedor conoció el daño, la fecha de notificación y un cómputo en días hábiles que el registro no suele llevar. |
| La fecha de respuesta figura antes que la fecha de presentación. ¿Se detecta? | `PD-002` compara fila por fila la fecha de presentación con la de respuesta e informa de `raisedAt` cuando es posterior a `replyAt`; el mismo día no cuenta como posterior. Un valor que no puede analizar —`2026年3月15日`, por ejemplo, cuando `2026-03-15`, `2026/3/15` o `2026-03-15 09:30` sí se leen— se informa en esa fila en lugar de dejarlo pasar en silencio. La regla solo ordena las dos fechas que el registro contiene. |
| Nuestra respuesta salió después del plazo de respuesta registrado en el registro. ¿Fue tardía? | `PD-003` no incorpora ningún número de días y no puede decir «tardía»: compara la fecha real de la respuesta con el plazo escrito en la propia columna `replyDueAt` del registro, de modo que un hallazgo significa «esto no concuerda con el plazo que usted registró». Si esa columna está vacía no hay con qué comparar y la regla aparece en `skipped`, en lugar de suponer un plazo. |
| La columna de estado dice 已答复 y no se informó nada de ella. ¿Por qué? | `PD-005` contrasta el estado con el vocabulario que usted configure, y `values` viene vacío, así que tal como se entrega la regla aparece en `skipped` —la elección de los valores corresponde a su institución, no al motor— en lugar de pasar en silencio. Rellene `values` con su propia lista (待答复, 已答复, 已投诉, 已撤回, …) y todo valor que no figure en ella se informará fila por fila. Solo comprueba que el valor esté en la lista, nunca cómo debe tramitarse la impugnación. |
| La cabecera nombra el proyecto pero no lleva la fecha de presentación a nivel de cabecera. ¿Falta algo? | No. `PD-006` solo comprueba en la cabecera el proyecto de contratación: su `fields` por defecto es `[project]`, porque la fecha de presentación suele ser una columna por fila. Si su formulario sí la declara en la cabecera, la propia nota de la regla indica poner `fields` en `[project, raisedAt]`. La falta del proyecto se informa contra la cabecera, no contra una fila. |
| El mismo número de impugnación aparece en dos filas. | `PD-007` informa de la segunda fila y nombra la primera, comparando los números sin tener en cuenta los espacios. Una repetición suele significar que la misma impugnación se registró dos veces o que se copió mal un número: distinguirlo es una decisión humana. Si el registro no lleva columna de número, la regla informa de que no se aplica en lugar de pasar. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-protest-deadline
dsh --profile <name> --dump-config | grep 'dsh-protest-deadline'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/protest-deadline.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-protest-deadline
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-protest-deadline contributors.
