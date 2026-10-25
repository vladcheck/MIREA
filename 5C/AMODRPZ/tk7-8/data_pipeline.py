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

STRING_COLS = [
    "variable_1",
    "variable_5",
    "variable_20",
    "variable_21",
    "variable_22",
    "variable_28",
]

RARE_MIN_COUNT = 100


def load_cleaned(csv_path, with_string_cols=False):
    cols = list(FEATURE_COLS)
    if with_string_cols:
        cols += STRING_COLS
    df = pd.read_csv(csv_path, header=0, usecols=cols + [TARGET_COL])
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


def load_clean_split(csv_path, with_string_cols=False):
    df_cleaned, _ = load_cleaned(csv_path, with_string_cols=with_string_cols)
    train, validate, test = split_train_validate_test(df_cleaned)
    scaler = StandardScaler()
    scaler.fit(train[FEATURE_COLS].values.astype(np.float64))
    return train, validate, test, scaler


def encode_string_features(fit_df, df, rare_min_count=RARE_MIN_COUNT):
    """Mean-target encoding of STRING_COLS, mapping fitted on fit_df (train).

    Rare categories (< rare_min_count rows in fit_df) and categories unseen
    in fit_df map to the global train target mean. Returns an ndarray of
    shape (len(df), len(STRING_COLS)).
    """
    global_mean = fit_df[TARGET_COL].mean()
    encoded = []
    for c in STRING_COLS:
        counts = fit_df[c].value_counts()
        allowed = set(counts[counts >= rare_min_count].index)
        means = (
            fit_df.loc[fit_df[c].isin(allowed)]
            .groupby(c)[TARGET_COL]
            .mean()
        )
        encoded.append(df[c].map(means).fillna(global_mean).values.astype(np.float64))
    return np.column_stack(encoded)


def scaled_matrix(df, scaler, add_intercept=True):
    X = scaler.transform(df[FEATURE_COLS].values.astype(np.float64))
    if add_intercept:
        X = np.concatenate((np.ones((X.shape[0], 1)), X), axis=1)
    y = df[TARGET_COL].values.astype(np.int64)
    return X, y
