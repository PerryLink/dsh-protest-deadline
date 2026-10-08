# dsh-protest-deadline — आपत्ति और शिकायत रजिस्टर की तिथियों और समय-सीमाओं की जाँच

`dsh-protest-deadline` एक आपत्ति-और-शिकायत रजिस्टर (质疑与投诉台账) पढ़ता है — परियोजना हेडर और प्रत्येक आपत्ति की एक पंक्ति — और जाँचता है कि ऐसे रजिस्टर से यांत्रिक रूप से क्या अपेक्षित किया जा सकता है: आपत्ति उठाने की तिथि या उत्तर की तिथि दर्ज है या नहीं, तिथियाँ पढ़ी जा सकती हैं और उनका क्रम बनता है या नहीं, उत्तर रजिस्टर में ही लिखी उत्तर-समय-सीमा (`replyDueAt`) के भीतर है या नहीं, प्रत्येक स्थिति आपकी ही शब्दावली से है या नहीं, आपत्ति क्रमांक दोहराए नहीं गए हैं या नहीं, और हेडर खरीद परियोजना का नाम देता है या नहीं।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| किसी पंक्ति में आपत्ति की तिथि और उत्तर की तिथि दोनों खाली हैं। क्या यह दर्ज होता है? | हाँ। `PD-001` हर पंक्ति में `raisedAt` और `replyAt` में से कम से कम एक भरा होने की अपेक्षा करता है और जिस पंक्ति में दोनों खाली हैं उसे दर्ज करता है। यह केवल यह देखता है कि दोनों में से एक भरा है, यह नहीं कि आपत्ति विधिक अवधि के भीतर उठाई गई थी: उसके लिए आपूर्तिकर्ता को हानि का ज्ञान होने की तिथि, तामील की तिथि और कार्य-दिवसों की गणना चाहिए, जो रजिस्टर में प्रायः दर्ज नहीं होती। |
| उत्तर की तिथि आपत्ति की तिथि से पहले लिखी है। क्या यह पकड़ में आता है? | `PD-002` पंक्ति-दर-पंक्ति आपत्ति की तिथि की तुलना उत्तर की तिथि से करता है और `raisedAt` के `replyAt` से बाद का होने पर उसे दर्ज करता है; एक ही दिन बाद का नहीं माना जाता। जो मान वह पढ़ नहीं सकता — जैसे `2026年3月15日`, जबकि `2026-03-15`, `2026/3/15` या `2026-03-15 09:30` पढ़े जाते हैं — वह उसी पंक्ति में दर्ज होता है, चुपचाप छोड़ा नहीं जाता। यह नियम केवल रजिस्टर में लिखी इन दो तिथियों का क्रम देखता है। |
| हमारा उत्तर रजिस्टर में लिखी उत्तर-समय-सीमा के बाद गया। क्या वह विलंबित था? | `PD-003` कोई दिन-संख्या कठोरता से नहीं रखता और «विलंबित» नहीं कह सकता: यह वास्तविक उत्तर-तिथि की तुलना रजिस्टर के अपने `replyDueAt` कॉलम में लिखी समय-सीमा से करता है, इसलिए किसी प्रविष्टि का अर्थ है «यह आपके दर्ज की गई समय-सीमा से मेल नहीं खाता»। वह कॉलम खाली हो तो तुलना का आधार ही नहीं रहता और यह नियम `skipped` में दर्ज होता है, किसी अवधि को मान नहीं लेता। |
| स्थिति कॉलम में 已答复 लिखा है, फिर भी उस पर कुछ दर्ज नहीं हुआ। क्यों? | `PD-005` स्थिति की तुलना उस शब्दावली से करता है जो आप कॉन्फ़िगर करते हैं, और `values` खाली आता है, इसलिए जैसा दिया गया है वैसा ही यह नियम चुपचाप पास होने के बजाय `skipped` में दर्ज होता है — मानों का चयन आपकी संस्था का विषय है, इंजन का नहीं। अपनी सूची (待答复, 已答复, 已投诉, 已撤回, …) `values` में भरें, तब सूची में न होने वाला हर मान पंक्ति-दर-पंक्ति दर्ज होगा। यह केवल यह देखता है कि मान सूची में है, यह नहीं कि आपत्ति का निपटारा कैसे होना चाहिए। |
| हेडर परियोजना का नाम देता है, पर हेडर-स्तर पर आपत्ति की तिथि नहीं है। क्या कुछ छूटा है? | नहीं। `PD-006` हेडर में केवल खरीद परियोजना (`project`) देखता है: उसका `fields` डिफ़ॉल्ट `[project]` है, क्योंकि आपत्ति की तिथि सामान्यतः प्रति-पंक्ति कॉलम होती है। यदि आपके फ़ॉर्म में वह हेडर में भी दर्ज होती है, तो नियम का ही नोट कहता है कि `fields` को `[project, raisedAt]` कर दें। परियोजना का अभाव हेडर के विरुद्ध दर्ज होता है, किसी पंक्ति के विरुद्ध नहीं। |
| एक ही आपत्ति क्रमांक दो पंक्तियों में आया है। | `PD-007` दूसरी पंक्ति दर्ज करता है और पहली का उल्लेख करता है; तुलना में रिक्त स्थान नहीं गिने जाते। दोहराव का अर्थ प्रायः यह होता है कि वही आपत्ति दो बार दर्ज हुई या क्रमांक गलत लिखा गया — इन दोनों में अंतर करना मानवीय निर्णय है। रजिस्टर में क्रमांक कॉलम ही न हो तो यह नियम पास होने के बजाय बताता है कि वह लागू नहीं होता। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
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

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-protest-deadline
dsh --profile <name> --dump-config | grep 'dsh-protest-deadline'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/protest-deadline.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-protest-deadline
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-protest-deadline contributors.
