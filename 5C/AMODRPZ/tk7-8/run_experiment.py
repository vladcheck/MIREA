"""Workbook flow end-to-end: advert demo + insclass LL vs CE comparison.

Mirrors workbook cells: advert x/Y, intercept concat, time.time() fits at
alpha=0.01 / max_steps=10000, coefs + accuracy; then insclass
load_clean_split -> scaled_matrix -> fits -> accuracy/precision/recall/f1.
Writes results/comparison.csv and learning-curve PNGs.
"""

import os
import time
from typing import Dict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data_pipeline import TARGET_COL, load_clean_split, scaled_matrix
from logistic_regression import LogisticRegressionGD

HERE = os.path.dirname(os.path.abspath(__file__))
TRAIN_CSV = os.path.join(HERE, "docs", "insclass_train.csv")
RESULTS = os.path.join(HERE, "results")
os.makedirs(RESULTS, exist_ok=True)


def advert_frames():
    x = pd.DataFrame(
        np.array(
            [
                39,
                36,
                60,
                21,
                27,
                12,
                51,
                57,
                54,
                42,
                18,
                9,
                48,
                66,
                6,
                30,
                24,
                33,
                15,
                21,
                100,
                200,
            ]
        )
    )
    Y = pd.DataFrame(
        np.array([1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1])
    )
    x_ = pd.DataFrame(np.concatenate((np.ones((x.shape[0], 1)), x), axis=1))
    return x, Y, x_


def fit_report(name, x_, Y, alpha=0.01, max_steps=10000):
    row = {"dataset": name}
    for rtype in ("LL", "CE"):
        m = LogisticRegressionGD()
        t0 = time.time()
        steps, errors = m.fit(x_, Y, alpha=alpha, max_steps=max_steps, Rtype=rtype)
        row[f"{rtype}_time"] = time.time() - t0
        row[f"{rtype}_accuracy"] = float(np.asarray(m.accuracy(x_, Y)).mean())
        row[f"{rtype}_precision"] = m.precision(x_, Y)
        row[f"{rtype}_recall"] = m.recall(x_, Y)
        row[f"{rtype}_f1"] = m.f1(x_, Y)
        row[f"{rtype}_coef0"] = float(np.asarray(m.coefs()).ravel()[0])
        row[f"{rtype}_coef1"] = (
            float(np.asarray(m.coefs()).ravel()[1])
            if np.asarray(m.coefs()).size == 2
            else None
        )
        plt.figure()
        plt.plot(
            steps,
            np.asarray(errors).ravel()
            if not isinstance(errors[0], (int, float, np.floating))
            else errors,
            label=rtype,
        )
        plt.title(f"Кривая обучения: {name} ({rtype})")
        plt.xlabel("Шаг")
        plt.ylabel("Ошибка")
        plt.legend()
        plt.savefig(os.path.join(RESULTS, f"{name}_{rtype}_curve.png"))
        plt.close()
    return row


def main():
    rows = []
    x, Y, x_ = advert_frames()
    rows.append(fit_report("advert", x_, Y))

    train, validate, _, scaler = load_clean_split(TRAIN_CSV)
    # ndarrays (not DataFrames): identical math, no per-step pandas overhead.
    # 10000 шагов, как в методичке.
    Xtr, ytr = scaled_matrix(train, scaler)
    Xva, yva = scaled_matrix(validate, scaler)
    rows.append(fit_report("insclass_train", Xtr, ytr, max_steps=10000))

    # Validate-set scores from the train-fitted models.
    m_ll, m_ce = LogisticRegressionGD(), LogisticRegressionGD()
    m_ll.fit(Xtr, ytr, max_steps=10000, Rtype="LL")
    m_ce.fit(Xtr, ytr, max_steps=10000, Rtype="CE")
    val_row: Dict[str, float | str] = {"dataset": "insclass_validate"}
    for tag, m in (("LL", m_ll), ("CE", m_ce)):
        val_row[f"{tag}_accuracy"] = float(np.asarray(m.accuracy(Xva, yva)).mean())
        val_row[f"{tag}_f1"] = m.f1(Xva, yva)
    rows.append(val_row)

    cmp_df = pd.DataFrame(rows)
    cmp_df.to_csv(os.path.join(RESULTS, "comparison.csv"), index=False)
    print(cmp_df.to_string())
    print(f"\ntarget rate train: {(train[TARGET_COL] == 1).mean():.4f}")
    print(
        "NOTE: insclass_test.csv is absent from the archive; "
        "held-out split used instead."
    )


if __name__ == "__main__":
    main()
