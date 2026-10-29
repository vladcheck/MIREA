"""Seam 2: insclass data pipeline (workbook cells [43]-[48] equivalents)."""

import numpy as np

from pathlib import Path

from data_pipeline import FEATURE_COLS, TARGET_COL, load_clean_split

TRAIN_CSV = str(Path(__file__).resolve().parent.parent / "docs" / "insclass_train.csv")


def test_load_clean_split_ratios_and_no_nans():
    train, validate, test, scaler = load_clean_split(TRAIN_CSV)
    assert list(train.columns) == FEATURE_COLS + [TARGET_COL]
    n = len(train) + len(validate) + len(test)
    assert n == 146529  # 151406 raw minus dropna rows, per workbook cell [46]
    assert abs(len(train) / n - 0.70) < 0.01
    assert abs(len(validate) / n - 0.15) < 0.01
    assert abs(len(test) / n - 0.15) < 0.01
    for df in (train, validate, test):
        assert int(df.isna().sum().sum()) == 0


def test_scaler_fit_on_train_only():
    train, _, _, scaler = load_clean_split(TRAIN_CSV)
    assert scaler.mean_ is not None
    assert scaler.mean_.shape == (len(FEATURE_COLS),)
    # StandardScaler fitted on train: transformed train has ~zero mean.
    Xt = scaler.transform(train[FEATURE_COLS].values)
    assert abs(Xt.mean()) < 1e-9


def test_target_imbalance_preserved():
    train, _, _, _ = load_clean_split(TRAIN_CSV)
    rate = (train[TARGET_COL] == 1).mean()
    assert 0.08 < rate < 0.12  # ~9.5% risky in raw probe
    assert set(np.unique(train[TARGET_COL].values)) <= {0, 1}  # type: ignore


def test_string_mean_encoding_fitted_on_train():
    from data_pipeline import STRING_COLS, encode_string_features, load_clean_split

    train, validate, _, _ = load_clean_split(TRAIN_CSV, with_string_cols=True)
    enc_tr = encode_string_features(train, train)
    enc_va = encode_string_features(train, validate)
    assert enc_tr.shape == (len(train), len(STRING_COLS))
    assert enc_va.shape == (len(validate), len(STRING_COLS))
    assert not np.isnan(enc_tr).any() and not np.isnan(enc_va).any()
    # Encoded values are target rates: within [0, 1], centered near the train rate.
    assert enc_tr.min() >= 0 and enc_tr.max() <= 1
    train_rate = train[TARGET_COL].mean()
    assert abs(enc_va.mean() - train_rate) < 0.05
