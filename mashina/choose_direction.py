"""Direction check-up 12.11.2026: 5 directions x 8 criteria, scores 0-3 set by Claude
from what was known that day. Prints the equal-weight score, how often each
direction wins over 20 000 random weightings, and the winner with each criterion
left out. Scores are judgements, not measurements; change them and rerun.
Usage: python -m mashina.choose_direction
"""
import numpy as np
opts = ["1 Доказательство происхождения (CBAM, SAFE 65%, батареи, принудтруд)",
        "2 Оборонное производство в Европе",
        "3 Проверка ИИ и данных под AI Act/EHDS",
        "4 Энергия: прогноз цен и сети по физике погоды",
        "5 Критические минералы и магниты"]
crit = ["механизм (дата+предел+обязанный покупатель)", "незанятость", "твой доступ к трудной информации",
        "проект к 15.03 без лаборатории и денег, с проверкой", "разноплановость для DTU/ITU",
        "путь к должности/доле в Дании", "устойчивость к развороту", "совпадает с тезисом «качество информации»"]
S = np.array([
 [3,3,3,2,2,2,2,3],
 [3,1,2,1,2,2,2,1],
 [2,2,2,3,2,2,1,3],
 [1,1,1,3,3,3,2,1],
 [2,2,2,2,3,1,1,2]], float)
eq = S.mean(1)
print("equal weights:", dict(zip([o[:1] for o in opts], eq.round(2))))
rng = np.random.default_rng(42)
W = rng.dirichlet(np.ones(len(crit)), 20000)
win = np.bincount((W @ S.T).argmax(1), minlength=len(opts)) / len(W)
print("wins over random weights:", dict(zip([o[:1] for o in opts], win.round(3))))
# named weightings
named = {"деньги прежде всего": [3,3,2,0,0,2,2,1], "поступление прежде всего": [1,0,1,3,3,0,0,1], "твоя гипотеза прежде всего": [1,1,3,1,0,0,0,3]}
for k,w in named.items():
    w=np.array(w,float); sc=S@w/w.sum(); print(k, dict(zip([o[:1] for o in opts], sc.round(2))))
# leave-one-criterion-out
for j,c in enumerate(crit):
    m=np.delete(S,j,1).mean(1); print("без", c, "->", opts[m.argmax()][:1], m.round(2))
