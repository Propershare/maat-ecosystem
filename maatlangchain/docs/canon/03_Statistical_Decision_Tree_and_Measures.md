# Statistical Decision Tree and Measures Overview

## Data Preparation
- Organize raw data into an array
- Combine and simplify data as needed
- Prepare frequency distribution table
- Choose graphic display (histogram, etc.)

---

## Measures

### Measures of Central Tendency
- Mean (Arithmetic, Geometric, Harmonic)
- Median
- Mode

### Measures of Variability
- Range
- Standard Deviation
- Variance
- Interquartile Range (IQR)

### Measures of Association
- Cross-tabulation
- Chi-square (χ²)

### Measures of Linear Relationship
- Pearson Correlation Coefficient
- Spearman's Rho
- Kendall's Tau

---

## Levels of Measurement
- Nominal
- Ordinal
- Interval
- Ratio

---

## Statistical Tests Based on:
- **Number of Variables**: One, Two, or Multiple
- **Type of Variable**: Category or Metric
- **Level of Measurement**: Nominal, Ordinal, Interval/Ratio
- **Parametric (P) vs Non-Parametric (NP)**

---

## Statistical Tests by Variable Type and Number

### Category Variables

#### Nominal
- One Variable: 
  - Chi-square (NP)
  - Coefficient of differentiation (NP)
- Two Variables:
  - Kendall's tau (NP)
  - Fisher's exact test (NP)
  - Point biserial correlation (P)
- Multiple Variables:
  - Discriminant analysis (P)
  - Canonical correlation (P)

#### Ordinal
- One Variable: 
  - Median test (NP)
- Two Variables:
  - Spearman's rank correlation (NP)
  - Mann-Whitney U test (NP)
- Multiple Variables:
  - Kruskal-Wallis ANOVA (NP)

#### Interval/Ratio
- One Variable:
  - One-sample t-test (P)
- Two Variables:
  - Independent t-test (P)
  - Paired t-test (P)
  - Pearson correlation (P)
- Multiple Variables:
  - ANOVA (P)
  - MANOVA (P)
  - Multiple regression (P)
  - Canonical correlation (P)

---

## Number of Independent Variables and Dependent Variables

### One Independent Variable
- One Dependent (Interval/Ratio): 
  - t-test or ANOVA
- Multiple Dependents:
  - MANOVA

### Multiple Independent Variables
- One Dependent: 
  - Factorial ANOVA
- Multiple Dependents: 
  - Factorial MANOVA

---

## Test Selection Based on Grouping

| Number of Groups | Level of Measurement | Independent/Related | Statistical Test                  |
|------------------|----------------------|----------------------|-----------------------------------|
| 2                | Nominal              | Independent          | Chi-square                        |
|                  |                      | Related              | McNemar test                      |
|                  | Ordinal              | Independent          | Mann-Whitney U                    |
|                  |                      | Related              | Wilcoxon                          |
|                  | Interval/Ratio       | Independent          | Independent t-test                |
|                  |                      | Related              | Paired t-test                     |
| >2               | Nominal              | Independent          | Chi-square                        |
|                  |                      | Related              | Cochran Q                         |
|                  | Ordinal              | Independent          | Kruskal-Wallis H test             |
|                  |                      | Related              | Friedman ANOVA                    |
|                  | Interval/Ratio       | Independent          | One-way ANOVA                     |
|                  |                      | Related              | Repeated measures ANOVA           |

