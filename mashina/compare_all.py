"""All niches proposed in the chats up to 12.11.2026, scored 0-3 on the same 9 criteria.
Scores are Claude's judgements from what was checked by that date, not measurements.
Prints the mean score, how often each niche wins over 20 000 random weightings,
three named weightings and the winner with each criterion left out.
Usage: python -m mashina.compare_all
"""
import numpy as np

CRIT = ["механизм", "незанято", "доступ", "проект к 15.03", "DTU/ITU", "работа в Дании",
        "устойчивость", "качество инфо", "потолок"]
# name: [mechanism, open, access, project, breadth, job_dk, stability, quality_info, ceiling]
NICHES = {
    "Доказательство происхождения (CBAM, SAFE, батареи, труд, санкции)": [3, 3, 3, 2, 2, 2, 2, 3, 2],
    "Метан в импортном газе (регламент ЕС, спутники)":               [3, 2, 2, 2, 3, 1, 1, 3, 2],
    "Проверка ИИ и данных под AI Act / EHDS":                        [2, 2, 2, 3, 2, 2, 1, 3, 2],
    "Медь Узбекистана":                                              [2, 2, 3, 2, 2, 1, 2, 2, 2],
    "Энергия по физике погоды (Energinet, торговля)":                [1, 1, 1, 3, 3, 3, 2, 1, 2],
    "Трансформаторы, электротехническая сталь, оборудование сети":   [2, 1, 1, 3, 3, 2, 2, 1, 2],
    "Критические минералы и магниты в Европе":                       [2, 2, 2, 2, 3, 1, 1, 2, 2],
    "Коммерческая наука и патенты":                                  [1, 2, 2, 2, 2, 1, 2, 3, 2],
    "Сурьма Таджикистана":                                           [3, 2, 2, 2, 2, 0, 1, 2, 2],
    "Средний коридор через Каспий":                                  [2, 2, 2, 2, 2, 2, 1, 2, 1],
    "Космос: космическая погода, орбитальные дата-центры":           [1, 2, 1, 2, 3, 1, 2, 2, 2],
    "Гелий, гелий-3, тритий, сверхпроводящая лента":                 [1, 2, 1, 2, 3, 0, 2, 2, 2],
    "ИИ для науки, автономные лаборатории":                          [1, 1, 1, 2, 2, 1, 1, 2, 3],
    "Оборонная химия и двигатели в Европе":                          [3, 1, 1, 1, 2, 1, 2, 1, 2],
    "Газ Южного коридора (Азербайджан)":                             [2, 1, 2, 2, 1, 1, 2, 1, 1],
    "Обогащение урана и топливо":                                    [3, 0, 0, 2, 3, 0, 2, 1, 2],
    "Доставка генной терапии (биомедицина)":                         [1, 1, 1, 0, 1, 2, 2, 1, 3],
    "Память и чипы для ИИ":                                          [1, 0, 0, 2, 2, 1, 1, 0, 1],
    "Рынки предсказаний и стейблкоины":                              [2, 0, 0, 2, 1, 0, 0, 1, 2],
    "Дженерики GLP-1":                                               [2, 0, 0, 1, 1, 1, 1, 0, 1],
}


def main():
    names = list(NICHES)
    S = np.array([NICHES[n] for n in names], float)
    mean = S.mean(1)
    rng = np.random.default_rng(42)
    W = rng.dirichlet(np.ones(len(CRIT)), 20000)
    wins = np.bincount((W @ S.T).argmax(1), minlength=len(names)) / len(W)
    top3 = np.zeros(len(names))
    for row in np.argsort(-(W @ S.T), axis=1)[:, :3]:
        top3[row] += 1
    top3 /= len(W)
    named = {"деньги": [2, 3, 2, 0, 0, 1, 2, 1, 3], "поступление": [1, 0, 1, 3, 3, 0, 0, 1, 0],
             "твоя гипотеза": [1, 1, 3, 1, 0, 0, 0, 3, 1]}
    order = np.argsort(-mean)
    print("niche | mean | wins | top3 | " + " | ".join(named))
    for i in order:
        nm = [float(S[i] @ np.array(w) / sum(w)) for w in named.values()]
        print(f"{names[i]} | {mean[i]:.2f} | {wins[i]:.3f} | {top3[i]:.3f} | " + " | ".join(f"{x:.2f}" for x in nm))
    for k, w in named.items():
        sc = S @ np.array(w, float) / sum(w)
        print("best for", k, "->", names[int(sc.argmax())], round(float(sc.max()), 2))
    for j, c in enumerate(CRIT):
        m = np.delete(S, j, 1).mean(1)
        print("without", c, "->", names[int(m.argmax())], round(float(m.max()), 2))


if __name__ == "__main__":
    main()
