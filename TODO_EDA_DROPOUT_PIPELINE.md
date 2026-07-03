# TODO - EDA & High-Performance Dropout Predictive Pipeline

## Step 1 — Repository + dataset audit
- [ ] Load `datasets/student dropout.csv` and print structural schema (dtypes, unique counts, missingness).
- [ ] Identify target/label column (default attempt: `risk_label`).
- [ ] Generate distribution/outlier diagnostics for educational dropout indicators.

## Step 2 — EDA report generation
- [ ] Create EDA notebook(s) that includes missingness patterns, correlations, and class imbalance.
- [ ] Export audit summary artifacts (JSON/CSV) into repo.

## Step 3 — Automated cleaning
- [ ] Implement cleaning logic: duplicates, null handling, encoding strategy, outlier clipping/winsorization.
- [ ] Ensure transformations are reproducible (fit on train only).

## Step 4 — Feature engineering
- [ ] Add interaction terms and polynomial features for selected numeric features.
- [ ] Add optional PCA (guarded by feature count / collinearity checks).

## Step 5 — Rigorous ML workflow
- [ ] Implement stratified k-fold CV.
- [ ] Add automated feature selection inside CV folds.
- [ ] Benchmark models: gradient boosting, ensemble, and neural net (if feasible).
- [ ] Add Bayesian hyperparameter optimization (Optuna preferred).

## Step 6 — Evaluation & reporting
- [ ] Multi-metric evaluation: Precision-Recall, AUC-ROC, F1, confusion matrices.
- [ ] Optimize classification threshold using PR/F1 on validation folds.
- [ ] Save best model + preprocessing pipeline + metrics + plots.

## Step 7 — Integration / outputs
- [ ] Store artifacts under `models/trained/` (and/or new outputs dir).
- [ ] Ensure the trained artifact can be loaded by existing app inference or provide adapter.

