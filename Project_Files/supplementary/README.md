# Post-generation supplementary specification tests

These cases were assembled on 2026-10-15 after examining the archived task
descriptions and some original test files. **They are not prospectively blind or
independently selected** and are not a substitute for original train/test
separation. The original model did not receive this new file during its
archived generation according to the submitted provenance; that claim itself
is not independently authenticated.

Run `python tools/run_supplementary_tests.py`. The script imports each source
into a fresh Python subprocess with a 4-second timeout. On Unix it applies
resource limits to the child process. This is NOT a network/filesystem security
sandbox; run only vetted coursework samples and use an isolated VM/container
for untrusted code. Each solution must satisfy every added case to pass.

Keep the original `outputs/metrics.csv` unchanged. Secondary results are in
`supplementary/results.json` and `supplementary/results.csv`, not mixed into
the original pass@k and visible-test denominators.
