"""Binary logistic regression, aligned to workbook cells [19]-[27].

Mirrors the original ``LogisticRegressionGD`` API and math verbatim
(same method names, same LL/CE updates, same ``fit`` signature with the
``epsylon``/``Rtype`` spellings). Deviations only where the workbook has
no equivalent: ``precision``/``recall``/``f1``/``confusion_matrix``
(required by the task text), numeric stability (epsilon clip), and
accepting both DataFrame and ndarray inputs.
"""

import numpy as np
import pandas as pd

_EPS = 1e-12


class LogisticRegressionGD(object):
    def __init__(self):
        self.a = np.zeros(2).reshape(1, 2)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x @ self.a))

    def predict(self, x):
        return self.sigmoid(x)

    def predict_labels(self, x, threshold=0.5):
        return (np.asarray(self.predict(x)).ravel() > threshold).astype(int)

    def coefs(self):
        return self.a

    def LogLikelihood(self, x, Y):
        p = np.clip(np.asarray(self.predict(x)).ravel(), _EPS, 1 - _EPS)
        y = np.asarray(Y).ravel()
        return (y * np.log(p) + (1 - y) * np.log(1 - p)).sum()

    def CrossEntropy(self, x, Y):
        p = np.clip(np.asarray(self.predict(x)).ravel(), _EPS, 1 - _EPS)
        y = np.asarray(Y).ravel()
        return (-y * np.log(p) - (1 - y) * np.log(1 - p)).sum()

    def accuracy(self, x, Y):
        return ((self.predict(x) > 0.5) == Y).mean()

    def confusion_matrix(self, x, Y, threshold=0.5):
        y_true = np.asarray(Y).ravel()
        y_pred = (np.asarray(self.predict(x)).ravel() > threshold).astype(int)
        tp = int(((y_pred == 1) & (y_true == 1)).sum())
        tn = int(((y_pred == 0) & (y_true == 0)).sum())
        fp = int(((y_pred == 1) & (y_true == 0)).sum())
        fn = int(((y_pred == 0) & (y_true == 1)).sum())
        return tn, fp, fn, tp

    def precision(self, x, Y, threshold=0.5):
        tn, fp, fn, tp = self.confusion_matrix(x, Y, threshold)
        return tp / (tp + fp) if (tp + fp) > 0 else 0.0

    def recall(self, x, Y, threshold=0.5):
        tn, fp, fn, tp = self.confusion_matrix(x, Y, threshold)
        return tp / (tp + fn) if (tp + fn) > 0 else 0.0

    def f1(self, x, Y, threshold=0.5):
        p = self.precision(x, Y, threshold)
        r = self.recall(x, Y, threshold)
        return 2 * p * r / (p + r) if (p + r) > 0 else 0.0

    def fit(self, x, Y, alpha=0.01, epsylon=0.01, max_steps=10000, Rtype="LL"):
        X = x.values if isinstance(x, pd.DataFrame) else np.asarray(x, dtype=float)
        y = Y.values if isinstance(Y, pd.DataFrame) else np.asarray(Y)
        self.a = np.zeros(X.shape[1]).reshape(X.shape[1], 1)
        steps, errors = [], []
        step = 0
        for _ in range(max_steps):
            new_error = None

            if Rtype == "LL":
                new_error = self.LogLikelihood(X, y)
                dT_a = X.T @ (y - self.predict(X)) / X.shape[0]
                self.a += alpha * dT_a
            elif Rtype == "CE":
                new_error = self.CrossEntropy(X, y)
                dT_a = -X.T @ (y - self.predict(X)) / X.shape[0]
                self.a -= alpha * dT_a
            step += 1
            steps.append(step)

            if new_error is not None:
                errors.append(new_error)
            # if new_error < epsylon:
            #    break
        return steps, errors
