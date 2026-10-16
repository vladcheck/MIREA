"""TK5-6 wine kNN pipeline. New file; docs/ originals stay read-only."""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import label_binarize

FEATURES = [
    "fixed acidity",
    "volatile acidity",
    "citric acid",
    "residual sugar",
    "chlorides",
    "free sulfur dioxide",
    "total sulfur dioxide",
    "density",
    "pH",
    "sulphates",
    "alcohol",
]
TARGET = "quality"
TEST_SIZE = 0.3
RANDOM_STATE = 42  # deviation from workbook (it sets none); fixed for reproducibility
N_NEIGHBORS = 5  # workbook default KNeighborsClassifier()


def load_wine_data(csv_path: str | Path):
    """Load winequality-red.csv, report cleaning facts. No mutation of docs/."""
    csv_path = Path(csv_path)
    df = pd.read_csv(csv_path)
    missing_cells = int(df.isna().sum().sum())
    full_dup_rows = int(df.duplicated().sum())
    quality_counts = {
        int(k): int(v) for k, v in sorted(df["quality"].value_counts().items())
    }
    info = {
        "shape": tuple(df.shape),
        "missing_cells": missing_cells,
        "full_dup_rows": full_dup_rows,
        "quality_counts": quality_counts,
    }
    return df, info


def _load_split(csv_path: str | Path):
    """Shared load + stratified workbook split. Single protocol point."""
    df, _ = load_wine_data(csv_path)
    X = df[FEATURES].to_numpy()
    y = df[TARGET].to_numpy()
    classes = sorted(np.unique(y).tolist())
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, stratify=y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    return X_train, X_test, y_train, y_test, classes


def _ovr_auc(y_bin, proba, average):
    return float(roc_auc_score(y_bin, proba, multi_class="ovr", average=average))


def evaluate_knn(csv_path: str | Path, n_neighbors: int = N_NEIGHBORS):
    """Workbook protocol: stratify split 0.3, KNN(k), test metrics + OvR AUC.

    Returns dict with confusion matrix, accuracy/precision/recall/F1
    (macro + weighted + per-class), OvR ROC AUC, train/test check.
    """
    X_train, X_test, y_train, y_test, classes = _load_split(csv_path)
    clf = KNeighborsClassifier(n_neighbors=n_neighbors)
    clf.fit(X_train, y_train)
    pred = clf.predict(X_test)
    cm = confusion_matrix(y_test, pred, labels=classes)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, pred, labels=classes, zero_division=0
    )
    proba = clf.predict_proba(X_test)
    proba_order = [list(clf.classes_).index(c) for c in classes]
    y_bin = label_binarize(y_test, classes=classes)
    proba_aligned = proba[:, proba_order]
    auc_macro = _ovr_auc(y_bin, proba_aligned, "macro")
    auc_weighted = _ovr_auc(y_bin, proba_aligned, "weighted")
    auc_per_class = {
        c: float(roc_auc_score(y_bin[:, i], proba[:, proba_order[i]]))
        for i, c in enumerate(classes)
    }
    return {
        "classes": classes,
        "test_size": int(len(y_test)),
        "train_accuracy": float(accuracy_score(y_train, clf.predict(X_train))),
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision_macro": float(np.mean(precision)),
        "recall_macro": float(np.mean(recall)),
        "f1_macro": float(np.mean(f1)),
        "precision_weighted": float(np.average(precision, weights=support)),
        "recall_weighted": float(np.average(recall, weights=support)),
        "f1_weighted": float(np.average(f1, weights=support)),
        "per_class": {
            "precision": dict(zip(classes, map(float, precision))),
            "recall": dict(zip(classes, map(float, recall))),
            "f1": dict(zip(classes, map(float, f1))),
            "support_test": dict(zip(classes, map(int, support))),
            "roc_auc_ovr": auc_per_class,
        },
        "roc_auc_ovr_macro": auc_macro,
        "roc_auc_ovr_weighted": auc_weighted,
        "confusion_matrix": cm,
        "y_test": y_test,
        "y_pred": pred,
        "y_proba": proba[:, proba_order],
    }


def k_sweep(csv_path: str | Path, k_max: int = 30):
    """Recall-macro/accuracy vs k for the defense plots + overfit check."""
    X_train, X_test, y_train, y_test, classes = _load_split(csv_path)
    rows = []
    for k in range(1, k_max + 1):
        clf = KNeighborsClassifier(n_neighbors=k)
        clf.fit(X_train, y_train)
        pred = clf.predict(X_test)
        _, rec, _, _ = precision_recall_fscore_support(
            y_test, pred, labels=classes, zero_division=0
        )
        rows.append(
            {
                "k": k,
                "train_accuracy": float(accuracy_score(y_train, clf.predict(X_train))),
                "test_accuracy": float(accuracy_score(y_test, pred)),
                "recall_macro": float(np.mean(rec)),
            }
        )
    return rows
