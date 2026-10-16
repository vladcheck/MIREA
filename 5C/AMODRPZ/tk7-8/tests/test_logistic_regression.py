"""Seam 1: LogisticRegressionGD public behavior (workbook API).

Uses workbook cell [19] names verbatim: predict / coefs / LogLikelihood /
CrossEntropy / accuracy / fit(..., Rtype="LL"|"CE"). Additions only where
the workbook has no equivalent: precision / recall / f1 / confusion_matrix.
"""

import numpy as np
import pandas as pd

from logistic_regression import LogisticRegressionGD


def toy_data():
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


def test_predict_in_unit_interval():
    _, Y, x_ = toy_data()
    m = LogisticRegressionGD()
    m.fit(x_, Y, alpha=0.01, max_steps=10, Rtype="CE")
    p = np.asarray(m.predict(x_)).ravel()
    assert p.shape == (x_.shape[0],)
    assert np.all(p > 0) and np.all(p < 1)


def test_ce_decreases_and_ll_increases():
    # Workbook hyperparams verbatim (alpha=0.01, max_steps=10000): with the
    # unscaled x=200 outlier the first hundred steps oscillate (see the
    # noisy curves in workbook cell [41]), so the trend is asserted over
    # the full horizon, not at 500 steps.
    _, Y, x_ = toy_data()
    m_ce = LogisticRegressionGD()
    _, err_ce = m_ce.fit(x_, Y, alpha=0.01, max_steps=10000, Rtype="CE")
    assert err_ce[-1] < err_ce[0]
    m_ll = LogisticRegressionGD()
    _, err_ll = m_ll.fit(x_, Y, alpha=0.01, max_steps=10000, Rtype="LL")
    assert err_ll[-1] > err_ll[0]


def test_ll_and_ce_converge_to_same_solution():
    _, Y, x_ = toy_data()
    m_ce = LogisticRegressionGD()
    m_ce.fit(x_, Y, alpha=0.01, max_steps=10000, Rtype="CE")
    m_ll = LogisticRegressionGD()
    m_ll.fit(x_, Y, alpha=0.01, max_steps=10000, Rtype="LL")
    np.testing.assert_allclose(
        np.asarray(m_ce.coefs()),
        np.asarray(m_ll.coefs()),
        rtol=1e-6,
        atol=1e-8,
    )
    # Known-good reference from the original workbook run (cells [38]/[40]).
    a = np.asarray(m_ce.coefs()).ravel()
    assert a[0] < 0 < a[1]
    assert abs(a[0] - (-3.598810)) < 0.05
    assert abs(a[1] - 0.112152) < 0.005


def test_fit_with_1d_y_on_wide_matrix():
    # insclass shape: X (N, 11) ndarray, y (N,) 1-d — used to broadcast
    # to (N, N) and crash with ValueError.
    rng = np.random.default_rng(42)
    N = 500
    X = np.concatenate((np.ones((N, 1)), rng.normal(size=(N, 2))), axis=1)
    y = (X[:, 1] + X[:, 2] > 0).astype(np.int64)
    for rtype in ("LL", "CE"):
        m = LogisticRegressionGD()
        steps, errors = m.fit(X, y, alpha=0.1, max_steps=200, Rtype=rtype)
        assert np.asarray(m.coefs()).shape == (3, 1)
        assert len(errors) == 200
    # Loss must improve over the run (direction depends on Rtype).
    m = LogisticRegressionGD()
    _, err_ce = m.fit(X, y, alpha=0.1, max_steps=200, Rtype="CE")
    assert err_ce[-1] < err_ce[0]


def test_metrics_on_hand_worked_example():
    # y_true: 1 1 0 0 1 0 / y_pred: 1 0 0 1 1 0
    # -> TP=2, FN=1, TN=2, FP=1; accuracy=4/6, P=R=F1=2/3.
    m = LogisticRegressionGD()
    m.a = np.array([[100.0], [0.0]])  # intercept-only stub, unused below
    import types

    def fake_predict(self, x, threshold=0.5):
        return pd.DataFrame(np.array([1, 0, 0, 1, 1, 0]))

    m.predict = types.MethodType(fake_predict, m)
    Y = pd.DataFrame(np.array([1, 1, 0, 0, 1, 0]))
    X = pd.DataFrame(np.ones((6, 1)))
    assert m.confusion_matrix(X, Y) == (2, 1, 1, 2)
    # Workbook accuracy() returns a Series (DataFrame mean); reduce to scalar.
    assert abs(float(np.asarray(m.accuracy(X, Y)).mean()) - 4 / 6) < 1e-12
    assert abs(m.precision(X, Y) - 2 / 3) < 1e-12
    assert abs(m.recall(X, Y) - 2 / 3) < 1e-12
    assert abs(m.f1(X, Y) - 2 / 3) < 1e-12
