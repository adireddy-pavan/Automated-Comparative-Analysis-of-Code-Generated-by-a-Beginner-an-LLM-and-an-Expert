# Corrected matched-task statistical analysis

Tasks: 30; source samples/task: beginner=1, llm=5, expert=1; paired observations/source: beginner=30, llm=30, expert=30.

**Design:** Each of the 30 tasks provides a matched triplet of beginner,
expert and per-task median LLM measurements. Friedman is the omnibus
test; two-sided paired Wilcoxon tests use Bonferroni adjustment
within each metric. Rank-biserial effect sizes preserve pairing.
P-values are exploratory across the many tested metrics (no global family correction).

## Matched-task omnibus tests

| Metric                     |   beginner median |   LLM median |   expert median |   n | Friedman chi2   | p               | Kendall W   |
|----------------------------|-------------------|--------------|-----------------|-----|-----------------|-----------------|-------------|
| Mean Cyclomatic Complexity |             3.5   |        3     |           3     |  30 | 5.128           | 0.07700924594   | 0.086       |
| Max Cyclomatic Complexity  |             3.5   |        3     |           3     |  30 | 6.432           | 0.04011884556   | 0.107       |
| Maintainability Index      |            68.636 |       93.385 |          90.937 |  30 | 43.655          | 3.314360596e-10 | 0.728       |
| Halstead Volume            |            31.5   |       27.764 |          13.932 |  30 | 14.126          | 0.0008561516271 | 0.235       |
| Lines of Code (LOC)        |             8.5   |       17.5   |          23.5   |  30 | 55.580          | 8.530860559e-13 | 0.926       |
| Logical LOC                |             8.5   |       12     |          11     |  30 | 2.673           | 0.2628207112    | 0.044       |
| Source LOC                 |             8.5   |       10     |           9     |  30 | 4.784           | 0.09143226421   | 0.080       |
| Comment Lines              |             0     |        0     |           0     |  30 | 2.000           | 0.3678794412    | 0.033       |
| Pylint Score (/10)         |            10     |       10     |          10     |  30 | 12.667          | 0.001776103546  | 0.211       |
| Pylint Issue Count         |             0     |        0     |           0     |  30 | 12.667          | 0.001776103546  | 0.211       |
| Bandit Low-severity        |             0     |        0     |           0     |  30 | 8.000           | 0.01831563889   | 0.133       |
| Bandit Medium-severity     |             0     |        0     |           0     |  30 | N/A             | None            | N/A         |
| Bandit High-severity       |             0     |        0     |           0     |  30 | N/A             | None            | N/A         |
| Bandit Total Findings      |             0     |        0     |           0     |  30 | 8.000           | 0.01831563889   | 0.133       |
| Tests Passed               |             5     |        7     |           7     |  30 | 34.000          | 4.139937719e-08 | 0.567       |

## Paired post-hoc tests

| Metric                     | Pair               |   Wilcoxon W |   p adjusted |   Rank-biserial |   Median paired diff |   n nonzero |
|----------------------------|--------------------|--------------|--------------|-----------------|----------------------|-------------|
| Mean Cyclomatic Complexity | beginner vs expert |        111   |  0.286596    |           0.368 |                1     |          26 |
| Mean Cyclomatic Complexity | beginner vs llm    |         77   |  0.292115    |           0.391 |                0     |          22 |
| Mean Cyclomatic Complexity | expert vs llm      |         71.5 |  0.976643    |          -0.247 |                0     |          19 |
| Max Cyclomatic Complexity  | beginner vs expert |        113.5 |  0.326157    |           0.353 |                1     |          26 |
| Max Cyclomatic Complexity  | beginner vs llm    |         94.5 |  1           |           0.182 |                0     |          21 |
| Max Cyclomatic Complexity  | expert vs llm      |         27   |  0.138288    |          -0.55  |                0     |          15 |
| Maintainability Index      | beginner vs expert |          2   |  1.67638e-08 |          -0.991 |              -26.462 |          30 |
| Maintainability Index      | beginner vs llm    |          0   |  5.19992e-06 |          -1     |              -26.058 |          30 |
| Maintainability Index      | expert vs llm      |        134   |  0.875627    |          -0.236 |                0     |          26 |
| Halstead Volume            | beginner vs expert |        122.5 |  0.119711    |           0.437 |               14.583 |          29 |
| Halstead Volume            | beginner vs llm    |        131   |  0.49036     |           0.307 |                3.553 |          27 |
| Halstead Volume            | expert vs llm      |         53   |  0.00964364  |          -0.674 |               -4.755 |          25 |
| Lines of Code (LOC)        | beginner vs expert |          0   |  5.10253e-06 |          -1     |              -14     |          30 |
| Lines of Code (LOC)        | beginner vs llm    |          1.5 |  5.90725e-06 |          -0.994 |               -8.5   |          30 |
| Lines of Code (LOC)        | expert vs llm      |          1.5 |  8.48351e-06 |           0.993 |                5     |          29 |
| Logical LOC                | beginner vs expert |        126   |  0.232549    |          -0.379 |               -1.5   |          28 |
| Logical LOC                | beginner vs llm    |         99   |  0.0524467   |          -0.512 |               -1.5   |          28 |
| Logical LOC                | expert vs llm      |        173   |  1           |          -0.085 |                0     |          27 |
| Source LOC                 | beginner vs expert |        103   |  1           |           0.186 |                0.5   |          22 |
| Source LOC                 | beginner vs llm    |        179.5 |  1           |          -0.116 |                0     |          28 |
| Source LOC                 | expert vs llm      |         75   |  0.0899077   |          -0.5   |               -1     |          24 |
| Comment Lines              | beginner vs expert |          0   |  0.951932    |          -1     |                0     |           1 |
| Comment Lines              | beginner vs llm    |          0   |  0.951932    |          -1     |                0     |           1 |
| Comment Lines              | expert vs llm      |          0   |  1           |           0     |                0     |           0 |
| Pylint Score (/10)         | beginner vs expert |          0   |  0.0348481   |          -1     |                0     |           8 |
| Pylint Score (/10)         | beginner vs llm    |          2   |  0.0452011   |          -0.911 |                0     |           9 |
| Pylint Score (/10)         | expert vs llm      |          0   |  0.951932    |           1     |                0     |           1 |
| Pylint Issue Count         | beginner vs expert |          0   |  0.025159    |           1     |                0     |           8 |
| Pylint Issue Count         | beginner vs llm    |          4   |  0.062998    |           0.822 |                0     |           9 |
| Pylint Issue Count         | expert vs llm      |          0   |  0.951932    |          -1     |                0     |           1 |
| Bandit Low-severity        | beginner vs expert |          0   |  0.136501    |           1     |                0     |           4 |
| Bandit Low-severity        | beginner vs llm    |          0   |  0.136501    |           1     |                0     |           4 |
| Bandit Low-severity        | expert vs llm      |          0   |  1           |           0     |                0     |           0 |
| Bandit Medium-severity     | beginner vs expert |          0   |  1           |           0     |                0     |           0 |
| Bandit Medium-severity     | beginner vs llm    |          0   |  1           |           0     |                0     |           0 |
| Bandit Medium-severity     | expert vs llm      |          0   |  1           |           0     |                0     |           0 |
| Bandit High-severity       | beginner vs expert |          0   |  1           |           0     |                0     |           0 |
| Bandit High-severity       | beginner vs llm    |          0   |  1           |           0     |                0     |           0 |
| Bandit High-severity       | expert vs llm      |          0   |  1           |           0     |                0     |           0 |
| Bandit Total Findings      | beginner vs expert |          0   |  0.136501    |           1     |                0     |           4 |
| Bandit Total Findings      | beginner vs llm    |          0   |  0.136501    |           1     |                0     |           4 |
| Bandit Total Findings      | expert vs llm      |          0   |  1           |           0     |                0     |           0 |
| Tests Passed               | beginner vs expert |          0   |  0.00077061  |          -1     |               -1     |          17 |
| Tests Passed               | beginner vs llm    |          0   |  0.00077061  |          -1     |               -1     |          17 |
| Tests Passed               | expert vs llm      |          0   |  1           |           0     |                0     |           0 |

## Functional analysis

| Source   |   Passed |   Total samples |   Descriptive pass rate |
|----------|----------|-----------------|-------------------------|
| beginner |       13 |              30 |                   0.433 |
| llm      |      150 |             150 |                   1     |
| expert   |       30 |              30 |                   1     |

**Paired binary test:** prespecified LLM sample 1 per task (30 matched triplets).
Cochran Q=34.0; p=4e-08; n=30.

**Exact paired McNemar with Bonferroni for three comparisons:**

- beginner_vs_expert: discordant 17; adjusted p=4.578e-05; rate difference=-0.5667
- beginner_vs_llm: discordant 17; adjusted p=4.578e-05; rate difference=-0.5667
- expert_vs_llm: discordant 0; adjusted p=1.0; rate difference=0.0

## pass@k

The original visible-tests estimates are descriptive
and must not be interpreted as unseen-test reliability.

- beginner: pass@1=0.4333, pass@5=None
- llm: pass@1=1.0, pass@5=1.0
- expert: pass@1=1.0, pass@5=None
