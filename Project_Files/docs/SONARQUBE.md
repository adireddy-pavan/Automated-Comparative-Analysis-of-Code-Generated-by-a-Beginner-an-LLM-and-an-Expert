# SonarQube (OPTIONAL) — not required to run the Tharun Project

> **The core pipeline does not use SonarQube.** All complexity, maintainability,
> size and security metrics in this study come from **radon**, **pylint** and
> **bandit**, which run offline with no server. This document is only for users
> who *already* operate a SonarQube instance and would like an additional,
> independent view of the same code. Nothing here is needed for
> `python run_analysis.py` to succeed.

## What SonarQube would add

SonarQube reports overlap conceptually with what this project already computes:

| This project (radon/pylint/bandit) | Rough SonarQube equivalent |
|---|---|
| radon cyclomatic complexity        | Cognitive / Cyclomatic Complexity |
| radon maintainability index        | Maintainability rating, code smells |
| bandit security findings           | Security hotspots / vulnerabilities |
| pylint score & issues              | Reliability rating, issues |

Because SonarQube needs a running server (and often a token), it cannot be part
of a single offline, deterministic command — hence it is kept optional.

## One-time setup

1. Run a SonarQube server (e.g. the official Docker image):
   ```bash
   docker run -d --name sonarqube -p 9000:9000 sonarqube:lts-community
   ```
   Open <http://localhost:9000> and log in (default `admin`/`admin`, then change
   the password).

2. Create a project named **Tharun Project** with key `tharun-project` and
   generate an analysis **token**.

3. Install the scanner CLI (`sonar-scanner`) from the SonarSource downloads page
   and put it on your `PATH`.

## Running a scan

From the project root:

```bash
# Copy the template up to the root (the scanner looks for it there by default).
cp sonar/sonar-project.properties .

sonar-scanner \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.token=YOUR_TOKEN_HERE
```

The provided `sonar/sonar-project.properties` already scopes the scan to the
benchmark solutions (`dataset/tasks/**/solutions/*.py`) and excludes the
framework, tests and generated artifacts.

## Optional: feed pylint/bandit reports to Sonar

The pipeline already saves raw pylint and bandit output under `evidence/`. If you
want SonarQube to ingest those, generate them in the external formats Sonar
expects and point the commented `sonar.python.*.reportPaths` keys in the
properties file at them. This is entirely optional and unrelated to the study's
results.

## Mapping back to the report

If you do run SonarQube, treat its ratings as corroboration for the
maintainability/complexity/security sections of `report/report.html`. The
project's conclusions are drawn solely from the radon/pylint/bandit numbers in
`outputs/`, so a SonarQube scan never changes them.
