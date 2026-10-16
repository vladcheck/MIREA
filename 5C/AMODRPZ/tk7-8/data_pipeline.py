"""insclass data pipeline, aligned to workbook cells [43]-[48].

Workbook steps mirrored: read_csv(usecols=...), isna().sum() report,
dropna(), np.split 70/15/15. Deviations only where the workbook has no
equivalent: StandardScaler fit on train only (raw scales diverge, Q7),
and the split uses len(df_cleaned) instead of the workbook's len(df)
typo.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

FEATURE_COLS = [
    "variable_4",
    "variable_6",
    "variable_12",
    "variable_13",
    "variable_14",
    "variable_16",
    "variable_17",
    "variable_18",
    "variable_19",
    "variable_27",
]
TARGET_COL = "target"


def load_cleaned(csv_path):
    df = pd.read_csv(csv_path, header=0, usecols=FEATURE_COLS + [TARGET_COL])
    na_report = df.isna().sum()
    df_cleaned = df.dropna().reset_index(drop=True)
    return df_cleaned, na_report


def split_train_validate_test(df_cleaned, train_frac=0.7, validate_frac=0.15):
    n = len(df_cleaned)
    i_train = int(train_frac * n)
    i_val = int((train_frac + validate_frac) * n)
    train, validate, test = (
        df_cleaned.iloc[:i_train].reset_index(drop=True),
        df_cleaned.iloc[i_train:i_val].reset_index(drop=True),
        df_cleaned.iloc[i_val:].reset_index(drop=True),
    )
    return train, validate, test


def load_clean_split(csv_path):
    df_cleaned, _ = load_cleaned(csv_path)
    train, validate, test = split_train_validate_test(df_cleaned)
    scaler = StandardScaler()
    scaler.fit(train[FEATURE_COLS].values.astype(np.float64))
    return train, validate, test, scaler


def scaled_matrix(df, scaler, add_intercept=True):
    X = scaler.transform(df[FEATURE_COLS].values.astype(np.float64))
    if add_intercept:
        X = np.concatenate((np.ones((X.shape[0], 1)), X), axis=1)
    y = df[TARGET_COL].values.astype(np.int64)
    return X, y
