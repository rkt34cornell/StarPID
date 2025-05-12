## Covariance Matrix

|             | RA_error            | DEC_error           | Roll_error          |
|-------------|---------------------|---------------------|---------------------|
| RA_error    | 1.071931529731781e-05 | 2.9585521218141e-08 | 0.0004044725690919465 |
| DEC_error   | 2.9585521218141e-08 | 6.190014088584843e-06 | -0.0001625924476595249 |
| Roll_error  | 0.0004044725690919465 | -0.0001625924476595249 | 75.43528880682577 |

| Metric       | Count   | Mean      | Std Dev  | Skewness | Kurtosis | Shapiro-W p |
|--------------|---------|-----------|----------|----------|----------|-------------|
| RA_error     | 300,000 | ~0.0000°  | 0.0033°  | ~0.15    | ~4.8     | p ≪ 0.05    |
| DEC_error    | 300,000 | ~0.0000°  | 0.0025°  | ~0.12    | ~4.6     | p ≪ 0.05    |
| Roll_error   | 10,000  | ~0.0137°  | 8.6820°  | ~0.05    | ~3.2     | p ≪ 0.05    |

# Star Tracker Adversarial Analysis Outputs

This folder contains the results of our adversarial-image generation and subsequent attitude-solution analysis. Below is a breakdown of each file, what it represents, and pointers on where to find the per-image deviations and summary statistics. 

We ran the STT pipeline (Star Tracker Software) over: 300,000 adversarial images (all 10 000 originals × 6 attack types × 5 levels) and 10 000 genuine images (the matching subset used to generate those adversarials)

**For our baseline (genuine) dataset we extracted Level-0 FITS frames from the SECCHI/HI-1A instrument on NASA’s STEREO-A spacecraft. In total we processed images collected during eight mission years — 2009, 2010, 2011, 2012, 2013, 2018, 2019, and 2020.
**---

## 1. Raw STT Outputs

- **`genuine_attitude.csv`**  
  - *Columns:*  
    - `filename` — original genuine `.fts` file name  
    - `type` — always `"genuine"`  
    - `RA_center`, `DEC_center`, `sig`, `Nr` — match-candidate metrics from SExtractor  
    - `RA`, `DEC`, `Roll` — attitude solution angles in degrees  
  - *Usage:*  
    - Baseline attitude solutions for genuine images.

- **`adversarial_attitude.csv`**  
  - *Columns:* same as above, but `type="adversarial"` and `filename` includes attack and level suffix.  
  - *Usage:*  
    - Attitude solutions after each tampering attack.  

---

## 2. Per-Image Error Table

- **`attitude_errors_combined.csv`**  
  - *Columns:*  
    - `filename_adv`, `type_adv`, `RA_center_adv`, …, `Roll_adv`  
    - `base_name` — original genuine filename  
    - `attack`, `level` — tampering type & severity  
    - `filename_gen`, `type_gen`, `RA_center_gen`, …, `Roll_gen`  
    - `RA_error`, `DEC_error`, `Roll_error` — per-image deviations (adversarial minus genuine)  
  - *Usage:*  
    - **Your primary per-image “deviation” table** — each row shows exactly how much RA, DEC, and Roll shifted for a given adversarial file.

---

## 3. Per-Attack/Level Breakdowns

- **`attitude_errors_<attack>_<level>.csv`**  
  Example: `attitude_errors_salt_pepper_moderate.csv`  
  - Subset of `attitude_errors_combined.csv` for one attack type & level.  
  - *Usage:*  
    - Quickly inspect or plot the error distribution for a single tampering scenario.

---

## 4. Summary Statistics

- **`summary_stats.csv`**  
  - *Columns:*  
    - `attack`, `level`  
    - `RA_error_mean`, `DEC_error_mean`, `Roll_error_mean`  
    - `RA_error_std`, `DEC_error_std`, `Roll_error_std`  
    - `sig_gen_mean`, `sig_adv_mean`, `Nr_gen_mean`, `Nr_adv_mean`  
    - `sig_gen_std`, `sig_adv_std`, `Nr_gen_std`, `Nr_adv_std`  
  - *Usage:*  
    - **Overall bias & precision** of each tampering scenario.  
    - Look at `<axis>_error_std` for the typical deviation per image.

- **`covariance_matrix.csv`**  
  - 3×3 covariance of (`RA_error`, `DEC_error`, `Roll_error`).  
  - *Usage:*  
    - Understand how errors in different axes co-vary (off-diagonals) and their variances (diagonals).

---

## 5. Visualizations

- **`distribution_plots/`**  
  - Histograms & KDEs for each error metric, boxplots by attack type & level.  
  - For a composite view, see `combined_errors_kde.png` 
---

> “Per-image deviations” live in the three `<axis>_error` columns of **`attitude_errors_combined.csv`**.  
> Overall scenario‐level deviations (mean & std) are in **`summary_stats.csv`**.

---

