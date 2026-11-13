# Радар: где цены говорят о дефиците

Запуск 2026-11-13 16:55 UTC. Работает сам, по расписанию в GitHub Actions, каждую неделю. Правило записано в `mashina/radar.py`.
Списки полные, ни один товар не выбран вручную. Строка наверху — это вопрос «почему?», а не ответ:
цена растёт и из-за пошлин, разовых событий, пересчёта индекса.

## А. Цены производителей ЕС по отраслям

Источник: Eurostat, все опубликованные коды отраслей. Рядов: 295, месяц 2026-09. Медианный рост за 24 месяца: +3.9%. Держатся у максимума: 88% рядов.

| Что подорожало и держится | 24 мес. | 12 мес. | 36 мес. |
|---|---|---|---|
| Manufacture of refined petroleum products [C192] | +70% | +72% | +33% |
| Manufacture of coke and refined petroleum products [C19] | +69% | +72% | +32% |
| Copper production [C2444] | +35% | +34% | +42% |
| Mining of metal ores [B07] | +35% | +33% | +33% |
| MIG - energy [MIG_NRG] | +32% | +35% | +16% |
| Manufacture of basic precious and other non-ferrous metals [C244] | +31% | +25% | +36% |
| Manufacture of jewellery and related articles [C3212] | +31% | +17% | +42% |
| Manufacture of jewellery, bijouterie and related articles [C321] | +26% | +14% | +36% |
| Extraction of crude petroleum and natural gas [B06] | +23% | +41% | +13% |
| Other non-ferrous metal production [C2445] | +23% | +25% | +15% |
| Electricity, gas, steam and air conditioning supply [D35] | +22% | +24% | +12% |
| Electricity, gas, steam and air conditioning supply [D] | +21% | +24% | +11% |
| Aluminium production [C2442] | +18% | +18% | +19% |
| Lead, zinc and tin production [C2443] | +16% | +16% | +14% |
| Manufacture of basic metals [C24] | +15% | +15% | +14% |
| Mining and quarrying [B] | +13% | +17% | +10% |
| Casting of other non-ferrous metals [C2454] | +13% | +10% | +16% |
| Repair of other equipment [C3319] | +12% | +6% | +14% |
| Manufacture of other electronic and electric wires and cables [C2732] | +12% | +11% | +14% |
| Sawmilling and planing of wood [C161] | +11% | +4% | +17% |
| Manufacture of basic chemicals, fertilisers and nitrogen compounds, plastics and synthetic rubber in primary forms [C201] | +11% | +13% | +9% |
| Manufacture of other inorganic basic chemicals [C2013] | +11% | +8% | +10% |
| Industry (except construction, sewerage, waste management and remediation activities), except food, beverages and tobacco [B-E36_X_FOOD] | +11% | +11% | +8% |
| Manufacture of other chemical products n.e.c. [C2059] | +11% | +10% | +8% |
| Manufacture of other organic basic chemicals [C2014] | +11% | +18% | +8% |
| Manufacture of imitation jewellery and related articles [C3213] | +10% | +6% | +11% |
| Manufacture of wiring and wiring devices [C273] | +10% | +9% | +13% |
| Mining and quarrying; manufacturing; electricity, gas, steam and air conditioning supply [B-D] | +10% | +10% | +7% |
| Manufacture of chemicals and chemical products [C20] | +10% | +11% | +8% |
| Manufacture of other chemical products [C205] | +10% | +9% | +7% |

Взгляд назад, верх списка в декабре каждого года:

- **2019** (медиана +2.3%): Precious metals production [C2441] +23%; Processing and preserving of meat [C1011] +15%; Processing and preserving of meat and production of meat products [C101] +10%; Manufacture of wallpaper [C1724] +7%; Mining support service activities [B09] +7%; Production of meat and poultry meat products [C1013] +7%; Preparation and spinning of textile fibres [C131] +7%; Casting of steel [C2452] +7%; Manufacture of refractory products [C232] +6%; Manufacture of cement, lime and plaster [C235] +6%
- **2020** (медиана +1.1%): Mining of metal ores [B07] +23%; Manufacture of sugar [C1081] +13%; Copper production [C2444] +13%; Manufacture of jewellery and related articles [C3212] +12%; Manufacture of jewellery, bijouterie and related articles [C321] +9%; Manufacture of margarine and similar edible fats [C1042] +9%; Manufacture of oils and fats [C1041] +7%; Manufacture of basic precious and other non-ferrous metals [C244] +7%; Manufacture of vegetable and animal oils and fats [C104] +6%; Manufacture of wallpaper [C1724] +6%
- **2021** (медиана +5.6%): Extraction of crude petroleum and natural gas [B06] +100%; Electricity, gas, steam and air conditioning supply [D35] +80%; Electricity, gas, steam and air conditioning supply [D] +79%; Manufacture of fertilisers and nitrogen compounds [C2015] +74%; MIG - energy [MIG_NRG] +59%; Manufacture of basic iron and steel and of ferro-alloys [C241] +58%; Cold forming or folding [C2433] +52%; Manufacture of oils and fats [C1041] +42%; Manufacture of other products of first processing of steel [C243] +41%; Manufacture of basic metals [C24] +41%
- **2022** (медиана +18.9%): Manufacture of other inorganic basic chemicals [C2013] +77%; Manufacture of lime and plaster [C2352] +69%; Manufacture of oils and fats [C1041] +66%; Manufacture of vegetable and animal oils and fats [C104] +63%; Manufacture of sugar [C1081] +61%; Manufacture of starches and starch products [C1062] +60%; Manufacture of margarine and similar edible fats [C1042] +57%; Manufacture of paper and paperboard [C1712] +54%; Manufacture of grain mill products, starches and starch products [C106] +54%; Manufacture of grain mill products [C1061] +48%
- **2023** (медиана +11.8%): Manufacture of sugar [C1081] +80%; Processing and preserving of potatoes [C1031] +55%; Manufacture of cement, lime and plaster [C235] +46%; Manufacture of bricks, tiles and construction products, in baked clay [C2332] +32%; Manufacture of ready-mixed concrete [C2363] +31%; Manufacture of plaster products for construction purposes [C2362] +29%; Manufacture of condiments and seasonings [C1084] +28%; Processing and preserving of fruit and vegetables [C103] +27%; Manufacture of other non-metallic mineral products [C23] +26%; Processing and preserving of meat and production of meat products [C101] +26%
- **2024** (медиана +3.3%): Manufacture of cocoa, chocolate and sugar confectionery [C1082] +49%; Precious metals production [C2441] +25%; Processing and preserving of potatoes [C1031] +25%; Manufacture of fruit and vegetable juice [C1032] +23%; Processing of tea and coffee [C1083] +21%; Manufacture of jewellery and related articles [C3212] +16%; Manufacture of ready-mixed concrete [C2363] +15%; Manufacture of other food products [C108] +15%; Manufacture of jewellery, bijouterie and related articles [C321] +14%; Manufacture of ice cream [C1052] +12%

## Б. Мировые цены на сырьё

Источник: Всемирный банк, все товары таблицы. Рядов: 67, месяц 2026-10. Медианный рост за 24 месяца: +12.6%. Держатся у максимума: 31% рядов.

| Что подорожало и держится | 24 мес. | 12 мес. | 36 мес. |
|---|---|---|---|
| Natural gas, Europe | +121% | +162% | +96% |
| Natural gas index | +89% | +86% | +60% |
| Fish meal | +73% | +61% | +55% |
| Crude oil, Brent | +65% | +93% | +37% |
| Copper | +52% | +35% | +83% |
| Crude oil, average | +47% | +72% | +22% |
| DAP | +40% | +7% | +50% |
| Crude oil, Dubai | +37% | +60% | +13% |
| Crude oil, WTI | +36% | +62% | +14% |
| Lamb ** | +34% | +18% | +35% |
| Liquefied natural gas, Japan | +32% | +49% | +31% |
| Rubber, TSR20 ** | +27% | +49% | +76% |
| Chicken ** | +24% | +7% | +16% |
| Soybeans | +17% | +27% | -3% |
| Tea, Mombasa | +13% | +4% | +8% |
| Phosphate rock | +11% | +11% | -51% |
| Sugar, US | +10% | +19% | -6% |
| Rubber, RSS3 | +8% | +42% | +76% |
| Soybean meal | +7% | +27% | -12% |
| Groundnut oil ** | +6% | +14% | -5% |
| Coal, Australian | +4% | +42% | +7% |

Взгляд назад, верх списка в декабре каждого года:

- **2019** (медиана -2.2%): Wheat, US SRW +38%; Groundnuts +24%; Potassium chloride ** +23%; Gold +17%; Coffee, Arabica +14%; Shrimps, Mexican +14%; Palm oil +13%; Rice, Thai 25% +8%
- **2020** (медиана +8.1%): Iron ore, cfr spot +125%; Palm oil +90%; Coconut oil +84%; Sunflower oil +66%; Palm kernel oil +66%; Rubber, RSS3 +62%; Soybean oil +41%; Groundnut oil ** +38%
- **2021** (медиана +30.9%): Natural gas, Europe +723%; Natural gas index +322%; Urea +309%; DAP +213%; Potassium chloride ** +204%; TSP +182%; Phosphate rock +144%; Tin +130%
- **2022** (медиана +14.8%): Orange +72%; Banana, US +46%; Fish meal +17%; Banana, Europe +10%; Tobacco, US import u.v. +5%; Cocoa +4%
- **2023** (медиана -12.0%): Cocoa +77%; Rice, Thai A.1 +65%; Rice, Thai 5% +61%; Rice, Viet Namese 5% +57%; Rice, Thai 25% +55%; Groundnuts +39%; Tobacco, US import u.v. +31%; Fish meal +30%
- **2024** (медиана -4.4%): Cocoa +311%; Coffee, Robusta +155%; Orange +145%; Palm kernel oil +97%; Coconut oil +70%; Coffee, Arabica +63%; Rubber, TSR20 ** +47%; Gold +47%

### Эпизоды по правилу: цена в 2 раза и больше выше минимума за предыдущие 24 месяца (с 2000 года, всего 278)

| Товар | Начало | Пик | Во сколько раз | Конец |
|---|---|---|---|---|
| Crude oil, average | 2000-01 | 2000-11 | 3.11 | 2001-02 |
| Crude oil, Brent | 2000-01 | 2000-09 | 3.33 | 2001-02 |
| Crude oil, Dubai | 2000-01 | 2000-10 | 2.99 | 2001-02 |
| Nickel | 2000-01 | 2000-03 | 2.65 | 2000-09 |
| Crude oil, WTI | 2000-01 | 2000-11 | 3.04 | 2001-02 |
| Banana, US | 2000-02 | 2000-02 | 2.0 | 2000-02 |
| Natural gas, US | 2000-05 | 2000-12 | 5.14 | 2001-04 |
| Natural gas index | 2000-06 | 2000-12 | 4.05 | 2001-04 |
| Natural gas, Europe | 2000-07 | 2001-01 | 2.49 | 2001-06 |
| Sugar, world | 2000-08 | 2000-10 | 2.18 | 2001-02 |
| Urea | 2000-08 | 2000-08 | 2.12 | 2000-08 |
| Banana, US | 2001-02 | 2001-02 | 2.38 | 2001-02 |
| Orange | 2001-04 | 2001-07 | 3.2 | 2001-08 |
| Banana, US | 2001-05 | 2001-07 | 2.26 | 2001-08 |
| Banana, US | 2002-05 | 2002-06 | 2.1 | 2002-06 |
| Orange | 2002-05 | 2002-07 | 2.1 | 2002-09 |
| Cocoa | 2002-07 | 2003-02 | 2.56 | 2003-03 |
| Soybean oil | 2002-11 | 2002-12 | 2.06 | 2002-12 |
| Natural gas, US | 2002-12 | 2003-02 | 3.61 | 2004-02 |
| Palm oil | 2002-12 | 2002-12 | 2.09 | 2003-02 |
| Rubber, RSS3 | 2003-02 | 2003-10 | 2.65 | 2004-02 |
| Natural gas index | 2003-02 | 2003-02 | 2.57 | 2003-03 |
| Rubber, TSR20 ** | 2003-02 | 2003-03 | 2.02 | 2003-03 |
| Natural gas index | 2003-05 | 2003-05 | 2.09 | 2003-06 |
| Groundnut oil ** | 2003-06 | 2004-01 | 2.43 | 2004-05 |
| Rubber, TSR20 ** | 2003-08 | 2003-10 | 2.74 | 2004-02 |
| Nickel | 2003-09 | 2003-12 | 2.69 | 2004-03 |
| Orange | 2003-10 | 2003-10 | 2.0 | 2003-10 |
| Cotton, A Index | 2003-11 | 2003-11 | 2.02 | 2003-11 |
| Natural gas index | 2003-12 | 2003-12 | 2.16 | 2004-01 |
| Lead | 2004-02 | 2004-02 | 2.12 | 2004-03 |
| Soybeans | 2004-03 | 2004-03 | 2.16 | 2004-03 |
| Orange | 2004-03 | 2004-07 | 2.3 | 2004-10 |
| Copper | 2004-03 | 2004-03 | 2.03 | 2004-03 |
| Coal, Australian | 2004-03 | 2004-07 | 2.75 | 2005-07 |
| Banana, Europe | 2004-03 | 2004-03 | 2.16 | 2004-03 |
| Rubber, RSS3 | 2004-04 | 2004-04 | 2.04 | 2004-04 |
| Tin | 2004-04 | 2004-05 | 2.47 | 2004-12 |
| Coal, South African ** | 2004-04 | 2004-07 | 3.22 | 2005-01 |
| Natural gas, US | 2004-05 | 2004-05 | 2.13 | 2004-06 |
| Banana, US | 2004-06 | 2004-06 | 2.07 | 2004-07 |
| Lead | 2004-06 | 2005-03 | 2.3 | 2005-06 |
| Nickel | 2004-06 | 2004-07 | 2.26 | 2004-08 |
| Urea | 2004-07 | 2004-10 | 2.62 | 2004-11 |
| Crude oil, Brent | 2004-10 | 2004-10 | 2.06 | 2004-10 |
| Copper | 2004-10 | 2004-10 | 2.03 | 2004-10 |
| Nickel | 2004-10 | 2004-10 | 2.12 | 2004-10 |
| Crude oil, WTI | 2004-10 | 2004-10 | 2.02 | 2004-10 |
| Banana, Europe | 2004-11 | 2005-05 | 3.0 | 2005-06 |
| Banana, US | 2005-01 | 2005-02 | 3.07 | 2005-05 |
| Iron ore, cfr spot | 2005-01 | 2005-01 | 2.03 | 2005-12 |
| Copper | 2005-02 | 2005-04 | 2.14 | 2005-04 |
| Crude oil, Brent | 2005-03 | 2005-03 | 2.12 | 2005-04 |
| Coffee, Arabica | 2005-03 | 2005-03 | 2.21 | 2005-05 |
| Nickel | 2005-03 | 2005-03 | 2.05 | 2005-05 |
| Crude oil, Dubai | 2005-04 | 2005-04 | 2.01 | 2005-04 |
| Orange | 2005-04 | 2005-04 | 2.02 | 2005-04 |
| Urea | 2005-04 | 2005-04 | 2.04 | 2005-04 |
| Crude oil, average | 2005-06 | 2005-08 | 2.3 | 2005-10 |
| Crude oil, Brent | 2005-06 | 2005-08 | 2.37 | 2005-10 |
| Crude oil, Dubai | 2005-06 | 2005-08 | 2.24 | 2005-09 |
| Copper | 2005-06 | 2005-08 | 2.16 | 2005-12 |
| Crude oil, WTI | 2005-07 | 2005-09 | 2.31 | 2005-10 |
| Natural gas, US | 2005-08 | 2005-10 | 2.98 | 2005-12 |
| Banana, Europe | 2005-08 | 2005-08 | 2.04 | 2005-08 |
| Natural gas index | 2005-09 | 2005-10 | 2.65 | 2005-12 |
| Sugar, world | 2005-12 | 2006-02 | 3.08 | 2006-07 |
| Crude oil, Brent | 2006-01 | 2006-01 | 2.06 | 2006-01 |
| Crude oil, Dubai | 2006-01 | 2006-01 | 2.05 | 2006-02 |
| Natural gas, Europe | 2006-01 | 2006-04 | 2.1 | 2006-08 |
| Coffee, Robusta | 2006-01 | 2006-01 | 2.0 | 2006-01 |
| Zinc | 2006-01 | 2006-11 | 4.0 | 2007-09 |
| Banana, US | 2006-02 | 2006-02 | 2.12 | 2006-03 |
| Crude oil, average | 2006-04 | 2006-04 | 2.02 | 2006-04 |
| Crude oil, Brent | 2006-04 | 2006-04 | 2.11 | 2006-04 |
| Crude oil, Dubai | 2006-04 | 2006-04 | 2.06 | 2006-04 |
| Copper | 2006-04 | 2006-05 | 2.99 | 2006-12 |
| Silver | 2006-04 | 2006-05 | 2.27 | 2006-05 |
| Banana, US | 2006-05 | 2006-05 | 2.33 | 2006-05 |
| Rubber, RSS3 | 2006-05 | 2006-06 | 2.29 | 2006-07 |
| Rubber, TSR20 ** | 2006-06 | 2006-06 | 2.06 | 2006-07 |
| Crude oil, Dubai | 2006-07 | 2006-07 | 2.01 | 2006-08 |
| Coffee, Robusta | 2006-07 | 2006-09 | 2.43 | 2007-01 |
| Nickel | 2006-07 | 2007-05 | 4.31 | 2007-11 |
| Lead | 2006-12 | 2006-12 | 2.02 | 2006-12 |
| Silver | 2006-12 | 2006-12 | 2.02 | 2006-12 |
| Lead | 2007-02 | 2007-10 | 3.86 | 2008-05 |
| Tin | 2007-02 | 2008-05 | 3.05 | 2008-09 |
| Copper | 2007-04 | 2007-04 | 2.39 | 2007-07 |
| Fish meal | 2007-06 | 2007-07 | 2.12 | 2007-08 |
| Wheat, US HRW | 2007-09 | 2007-10 | 2.08 | 2007-10 |
| Iron ore, cfr spot | 2007-09 | 2007-11 | 3.0 | 2008-08 |
| Wheat, US SRW | 2007-09 | 2008-03 | 3.0 | 2008-04 |
| Sunflower oil | 2007-09 | 2008-06 | 3.16 | 2008-07 |
| Palm oil | 2007-10 | 2008-03 | 2.91 | 2008-07 |
| Barley | 2007-10 | 2007-10 | 2.0 | 2007-10 |
| TSP | 2007-10 | 2008-08 | 5.6 | 2008-11 |
| Coconut oil | 2007-11 | 2008-06 | 2.7 | 2008-07 |
| Soybean oil | 2007-11 | 2008-03 | 2.76 | 2008-08 |
| DAP | 2007-11 | 2008-07 | 4.92 | 2008-12 |
| Coal, Australian | 2007-11 | 2008-07 | 4.08 | 2008-11 |
| Groundnuts | 2007-11 | 2008-01 | 2.32 | 2008-06 |
| Coal, South African ** | 2007-11 | 2008-07 | 3.48 | 2008-10 |
| Palm kernel oil | 2007-11 | 2008-03 | 2.72 | 2008-07 |
| Groundnut oil ** | 2007-12 | 2008-07 | 2.45 | 2008-10 |
| Soybean meal | 2007-12 | 2008-06 | 2.48 | 2008-07 |
| Wheat, US HRW | 2007-12 | 2008-03 | 2.52 | 2008-04 |
| Soybeans | 2008-01 | 2008-07 | 2.47 | 2008-09 |
| Barley | 2008-01 | 2008-04 | 2.33 | 2008-07 |
| Maize | 2008-01 | 2008-06 | 2.62 | 2008-08 |
| Sorghum | 2008-01 | 2008-06 | 2.34 | 2008-06 |
| Coffee, Robusta | 2008-03 | 2008-03 | 2.05 | 2008-03 |
| Rice, Thai 5% | 2008-03 | 2008-04 | 3.06 | 2008-10 |
| Nickel | 2008-03 | 2008-03 | 2.1 | 2008-03 |
| Rice, Thai A.1 | 2008-03 | 2008-04 | 3.52 | 2008-08 |
| Banana, Europe | 2008-03 | 2008-03 | 2.19 | 2008-03 |
| Rapeseed oil | 2008-03 | 2008-03 | 2.04 | 2008-03 |
| Crude oil, average | 2008-04 | 2008-07 | 2.48 | 2008-08 |
| Crude oil, Brent | 2008-04 | 2008-07 | 2.47 | 2008-08 |
| Natural gas, US | 2008-04 | 2008-06 | 2.61 | 2008-07 |
| Phosphate rock | 2008-04 | 2008-10 | 10.23 | 2009-08 |
| Urea | 2008-04 | 2008-08 | 3.75 | 2008-10 |
| Potassium chloride ** | 2008-04 | 2009-03 | 3.55 | 2009-12 |
| Crude oil, WTI | 2008-04 | 2008-06 | 2.47 | 2008-08 |
| Crude oil, Dubai | 2008-05 | 2008-07 | 2.52 | 2008-08 |
| Tea, Kolkata | 2008-06 | 2008-07 | 2.16 | 2008-08 |
| Orange | 2008-06 | 2008-06 | 2.1 | 2008-06 |
| Natural gas index | 2008-06 | 2008-06 | 2.1 | 2008-07 |
| Rapeseed oil | 2008-06 | 2008-06 | 2.06 | 2008-07 |
| Rice, Viet Namese 5% | 2008-06 | 2008-06 | 3.03 | 2008-09 |
| Rice, Thai 25% | 2008-07 | 2008-07 | 2.56 | 2008-09 |
| Liquefied natural gas, Japan | 2008-09 | 2008-11 | 2.2 | 2008-12 |
| Sugar, world | 2009-08 | 2009-09 | 2.32 | 2010-02 |
| Copper | 2009-08 | 2010-12 | 2.98 | 2011-04 |
| Nickel | 2009-08 | 2009-08 | 2.03 | 2009-08 |
| Lead | 2009-09 | 2010-01 | 2.46 | 2010-04 |
| Rubber, RSS3 | 2009-11 | 2011-02 | 4.38 | 2011-09 |
| Rubber, TSR20 ** | 2009-11 | 2011-02 | 4.36 | 2011-09 |
| Zinc | 2009-12 | 2010-01 | 2.21 | 2010-01 |
| Sugar, US | 2010-01 | 2010-02 | 2.07 | 2010-02 |
| Iron ore, cfr spot | 2010-01 | 2011-02 | 3.13 | 2011-09 |
| Crude oil, WTI | 2010-01 | 2010-01 | 2.0 | 2010-01 |
| Nickel | 2010-03 | 2011-02 | 2.91 | 2011-04 |
| Zinc | 2010-03 | 2010-04 | 2.15 | 2010-04 |
| Crude oil, WTI | 2010-03 | 2010-04 | 2.16 | 2010-04 |
| Crude oil, average | 2010-04 | 2010-04 | 2.04 | 2010-04 |
| Crude oil, Brent | 2010-04 | 2010-04 | 2.04 | 2010-04 |
| Crude oil, Dubai | 2010-04 | 2010-04 | 2.03 | 2010-04 |
| Platinum | 2010-04 | 2010-04 | 2.04 | 2010-04 |
| Palm kernel oil | 2010-05 | 2011-02 | 4.08 | 2011-07 |
| Lead | 2010-08 | 2010-12 | 2.51 | 2011-03 |
| Coconut oil | 2010-09 | 2011-02 | 3.61 | 2011-08 |
| Cotton, A Index | 2010-09 | 2011-03 | 4.44 | 2011-06 |
| Tin | 2010-09 | 2011-02 | 2.95 | 2011-05 |
| Silver | 2010-09 | 2011-04 | 3.42 | 2011-11 |
| Sugar, world | 2010-10 | 2010-12 | 2.38 | 2011-02 |
| TSP | 2010-10 | 2011-10 | 2.59 | 2011-12 |
| Zinc | 2010-10 | 2011-02 | 2.22 | 2011-02 |
| Platinum | 2010-10 | 2010-12 | 2.04 | 2010-12 |
| DAP | 2010-10 | 2010-10 | 2.18 | 2011-01 |
| Lamb ** | 2010-10 | 2011-04 | 2.52 | 2012-04 |
| Crude oil, WTI | 2010-10 | 2011-02 | 2.28 | 2011-04 |
| Crude oil, average | 2010-11 | 2011-02 | 2.34 | 2011-04 |
| Crude oil, Brent | 2010-11 | 2011-03 | 2.44 | 2011-04 |
| Crude oil, Dubai | 2010-11 | 2011-03 | 2.38 | 2011-04 |
| Sugar, US | 2010-11 | 2010-11 | 2.0 | 2010-11 |
| Coffee, Arabica | 2010-12 | 2011-03 | 2.28 | 2011-05 |
| Palm oil | 2010-12 | 2010-12 | 2.1 | 2010-12 |
| Wheat, US HRW | 2011-01 | 2011-05 | 2.25 | 2011-06 |
| Coal, Australian | 2011-01 | 2011-01 | 2.17 | 2011-03 |
| Wheat, US SRW | 2011-01 | 2011-02 | 2.14 | 2011-02 |
| Coal, South African ** | 2011-01 | 2011-04 | 2.14 | 2011-05 |
| Palm oil | 2011-02 | 2011-02 | 2.02 | 2011-02 |
| Sugar, US | 2011-02 | 2011-02 | 2.02 | 2011-03 |
| Sunflower oil | 2011-02 | 2011-02 | 2.25 | 2011-08 |
| Sorghum | 2011-03 | 2011-04 | 2.21 | 2011-04 |
| Barley | 2011-04 | 2011-07 | 2.08 | 2011-07 |
| Maize | 2011-04 | 2011-04 | 2.12 | 2011-08 |
| Urea | 2011-06 | 2011-09 | 2.25 | 2011-11 |
| DAP | 2011-06 | 2011-07 | 2.27 | 2011-11 |
| Liquefied natural gas, Japan | 2011-06 | 2011-07 | 2.15 | 2011-08 |
| Sorghum | 2011-07 | 2011-08 | 2.31 | 2011-11 |
| Wheat, US HRW | 2011-08 | 2011-08 | 2.07 | 2011-09 |
| Phosphate rock | 2011-08 | 2011-11 | 2.17 | 2012-02 |
| Barley | 2011-09 | 2011-09 | 2.03 | 2011-09 |
| Coconut oil | 2011-11 | 2011-11 | 2.03 | 2011-11 |
| Groundnuts | 2011-11 | 2011-11 | 2.15 | 2012-07 |
| Sorghum | 2012-01 | 2012-03 | 2.09 | 2012-03 |
| Silver | 2012-02 | 2012-02 | 2.14 | 2012-02 |
| Phosphate rock | 2012-04 | 2012-05 | 2.17 | 2012-06 |
| Urea | 2012-04 | 2012-05 | 2.27 | 2012-06 |
| Sorghum | 2012-06 | 2012-07 | 2.03 | 2012-07 |
| Maize | 2012-07 | 2012-07 | 2.03 | 2012-07 |
| Natural gas, US | 2013-04 | 2013-04 | 2.14 | 2013-05 |
| Natural gas, US | 2013-12 | 2014-02 | 3.06 | 2014-04 |
| Tea, Kolkata | 2015-07 | 2015-07 | 2.01 | 2015-07 |
| Coal, Australian | 2016-11 | 2016-11 | 2.11 | 2016-11 |
| Palm kernel oil | 2016-11 | 2017-01 | 2.36 | 2017-02 |
| Natural gas, US | 2016-12 | 2016-12 | 2.11 | 2016-12 |
| Rubber, RSS3 | 2017-01 | 2017-02 | 2.2 | 2017-02 |
| Rubber, TSR20 ** | 2017-01 | 2017-02 | 2.06 | 2017-02 |
| Crude oil, Dubai | 2017-02 | 2017-02 | 2.01 | 2017-02 |
| Iron ore, cfr spot | 2017-02 | 2017-02 | 2.21 | 2017-03 |
| Coal, Australian | 2017-08 | 2017-08 | 2.01 | 2017-08 |
| Zinc | 2017-09 | 2018-01 | 2.26 | 2018-02 |
| Crude oil, Dubai | 2017-10 | 2018-01 | 2.44 | 2018-02 |
| Crude oil, average | 2017-11 | 2018-01 | 2.22 | 2018-02 |
| Crude oil, Brent | 2017-11 | 2018-01 | 2.24 | 2018-01 |
| Coal, Australian | 2017-12 | 2018-01 | 2.17 | 2018-02 |
| Natural gas, US | 2018-01 | 2018-01 | 2.27 | 2018-01 |
| Crude oil, WTI | 2018-01 | 2018-01 | 2.1 | 2018-02 |
| Coal, Australian | 2018-05 | 2018-06 | 2.16 | 2018-06 |
| Natural gas, Europe | 2018-09 | 2018-09 | 2.24 | 2018-09 |
| Tea, Kolkata | 2020-06 | 2020-08 | 3.13 | 2021-01 |
| Crude oil, WTI | 2020-06 | 2022-03 | 6.58 | 2022-11 |
| Crude oil, average | 2020-07 | 2020-08 | 2.07 | 2020-08 |
| Natural gas, Europe | 2020-09 | 2022-07 | 28.52 | 2023-03 |
| Crude oil, average | 2020-11 | 2022-03 | 5.35 | 2022-11 |
| Coconut oil | 2020-11 | 2021-05 | 2.7 | 2022-05 |
| Crude oil, Brent | 2020-12 | 2022-03 | 4.96 | 2022-11 |
| Crude oil, Dubai | 2020-12 | 2022-03 | 4.85 | 2022-11 |
| Iron ore, cfr spot | 2020-12 | 2020-12 | 2.25 | 2021-01 |
| Palm kernel oil | 2020-12 | 2022-02 | 3.57 | 2022-06 |
| Natural gas index | 2021-01 | 2021-02 | 2.87 | 2021-02 |
| Natural gas, US | 2021-02 | 2021-02 | 3.15 | 2021-02 |
| DAP | 2021-02 | 2022-04 | 3.63 | 2022-10 |
| Sunflower oil | 2021-03 | 2021-03 | 2.26 | 2021-05 |
| Tea, Kolkata | 2021-04 | 2021-06 | 2.57 | 2021-12 |
| Soybean oil | 2021-04 | 2022-03 | 2.88 | 2022-06 |
| TSP | 2021-04 | 2022-04 | 3.57 | 2022-11 |
| Iron ore, cfr spot | 2021-04 | 2021-06 | 2.53 | 2021-07 |
| Natural gas index | 2021-04 | 2022-08 | 9.89 | 2023-01 |
| Palm oil | 2021-05 | 2021-05 | 2.09 | 2021-05 |
| Maize | 2021-05 | 2021-05 | 2.12 | 2021-06 |
| Copper | 2021-05 | 2021-05 | 2.01 | 2021-05 |
| Tin | 2021-05 | 2022-02 | 2.94 | 2022-05 |
| Coal, Australian | 2021-05 | 2022-08 | 8.12 | 2023-04 |
| Rapeseed oil | 2021-05 | 2021-05 | 2.02 | 2021-06 |
| Natural gas, US | 2021-06 | 2022-05 | 5.06 | 2022-12 |
| Potassium chloride ** | 2021-06 | 2022-04 | 5.45 | 2022-12 |
| Urea | 2021-07 | 2022-04 | 4.58 | 2022-12 |
| Coal, South African ** | 2021-07 | 2022-04 | 5.34 | 2023-01 |
| Rapeseed oil | 2021-08 | 2022-04 | 2.99 | 2022-06 |
| Palm oil | 2021-09 | 2022-03 | 3.08 | 2022-06 |
| Phosphate rock | 2021-09 | 2022-07 | 4.27 | 2023-11 |
| Aluminum | 2021-10 | 2021-10 | 2.01 | 2021-10 |
| Liquefied natural gas, Japan | 2021-10 | 2022-09 | 4.04 | 2023-03 |
| Coffee, Arabica | 2022-01 | 2022-02 | 2.06 | 2022-02 |
| Cotton, A Index | 2022-01 | 2022-05 | 2.49 | 2022-06 |
| Aluminum | 2022-01 | 2022-03 | 2.4 | 2022-04 |
| Maize | 2022-02 | 2022-04 | 2.42 | 2022-07 |
| Nickel | 2022-02 | 2022-03 | 2.87 | 2022-06 |
| Sunflower oil | 2022-02 | 2022-03 | 3.23 | 2022-06 |
| Soybeans | 2022-03 | 2022-05 | 2.02 | 2022-05 |
| Wheat, US HRW | 2022-03 | 2022-05 | 2.63 | 2022-06 |
| Copper | 2022-03 | 2022-03 | 2.02 | 2022-04 |
| Zinc | 2022-03 | 2022-04 | 2.29 | 2022-04 |
| Wheat, US SRW | 2022-03 | 2022-03 | 2.23 | 2022-05 |
| Tea, Kolkata | 2022-04 | 2022-04 | 2.39 | 2022-04 |
| Orange | 2023-02 | 2023-11 | 3.12 | 2025-01 |
| Cocoa | 2024-02 | 2024-04 | 4.35 | 2025-08 |
| Coffee, Robusta | 2024-04 | 2024-04 | 2.07 | 2024-04 |
| Coffee, Robusta | 2024-06 | 2024-09 | 2.61 | 2025-05 |
| Tea, Kolkata | 2024-06 | 2024-09 | 2.3 | 2024-10 |
| Palm kernel oil | 2024-11 | 2025-09 | 2.65 | 2026-05 |
| Natural gas, US | 2024-12 | 2025-02 | 2.81 | 2025-07 |
| Coffee, Arabica | 2025-02 | 2025-02 | 2.23 | 2025-05 |
| Coconut oil | 2025-03 | 2025-05 | 2.73 | 2025-12 |
| Tea, Kolkata | 2025-05 | 2025-05 | 2.07 | 2025-07 |
| Coffee, Arabica | 2025-09 | 2025-10 | 2.2 | 2025-11 |
| Natural gas, US | 2025-10 | 2026-01 | 5.05 | 2026-03 |
| Gold | 2025-10 | 2026-02 | 2.48 | 2026-04 |
| Silver | 2025-10 | 2026-01 | 4.06 | 2026-09 |
| Platinum | 2025-12 | 2026-01 | 2.72 | 2026-05 |
| Natural gas index | 2026-01 | 2026-01 | 2.3 | 2026-01 |
| Natural gas, Europe | 2026-03 | 2026-03 | 2.09 | 2026-03 |
| Urea | 2026-03 | 2026-04 | 3.01 | 2026-05 |
| Natural gas, Europe | 2026-08 | 2026-10 | 3.01 | идёт сейчас |

## Источники

| Источник | Ответ |
|---|---|
| federal_register | 200 |
| eurlex_rss | 200 |
| comext_bulk | 200 |
| eu | 200 |
| commodities | 200 |
| bls | error: <HTTPError 403: 'Forbidden'> |
