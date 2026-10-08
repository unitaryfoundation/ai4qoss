# CI gates for AI-era contributions

A CI gate is an automated check that runs on every pull request and can block merging
until it passes. Gates handle mechanically what does not need human judgment, so
review capacity is spent on substance. Each gate below states what it enforces, gives
a GitHub Actions workflow to copy into your repository's `.github/workflows/`
directory, and says where it can be fooled. Adapt the file paths and commands to your
project, and try a gate in a scratch repository before turning it into a required
check.

The workflows use building blocks published by others, referenced by version tag, for
example `dorny/paths-filter@v4`; versions are current as of the date below. Before
enforcing a gate, replace each third-party tag with the full 40-character commit SHA
(Secure Hash Algorithm hash) of that release, `dorny/paths-filter@<full-commit-sha>`.
A tag can later be moved to point at different code; a commit SHA identifies one exact
version forever. This is a real attack path: in March 2025 the version tags of the
widely used `tj-actions/changed-files` action were repointed at a malicious commit
([CVE-2025-30066](https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-tj-actionschanged-files-cve-2025-30066-and-reviewdogaction)),
which leaked CI secrets from roughly 23,000 repositories that referenced it by tag.

Last verified: 2026-08-27

## 1. Tests required

A pull request that changes source without touching tests fails a check. A maintainer
exempts docs-only or refactor PRs by applying a label; only accounts with triage or
write access can apply labels, so the exemption is maintainer-gated by construction.

```yaml
name: tests-required
on:
  pull_request:
    types: [opened, synchronize, reopened, labeled, unlabeled]
permissions:
  contents: read
  pull-requests: read
jobs:
  tests-required:
    runs-on: ubuntu-latest
    if: "!contains(github.event.pull_request.labels.*.name, 'no-tests-needed')"
    steps:
      - uses: dorny/paths-filter@v4 # pin to a commit SHA
        id: changes
        with:
          filters: |
            src:
              - 'src/**'
            tests:
              - 'tests/**'
      - name: source changed without tests
        if: steps.changes.outputs.src == 'true' && steps.changes.outputs.tests == 'false'
        run: |
          echo "Source changed without touching tests."
          echo "Add a test, or ask a maintainer for the no-tests-needed label."
          exit 1
```

Where it can be fooled: any test edit satisfies the gate, including a cosmetic one.
The gate checks that tests were touched; whether they test the change stays with
review, or with the reproduction gate below.

## 2. Reproduction required for bug fixes

A PR labeled as a bug fix must contain a test that fails on the base branch and passes
on the head. The gate demands a machine-checkable demonstration that the bug exists
and that the change removes it, which is the check low-effort submissions cannot
fake. Fail-then-pass is the standard task-validation rule in agent benchmarks
(SWE-bench), and we found no widely used CI implementation of it, so the pattern below
is offered as-is.

The gate runs only on PRs a maintainer has labeled `bugfix`; an unlabeled PR skips it,
and the skip counts as passing. The workflow assumes tests live under `tests/` and the
package is installed in editable mode, so switching the working tree switches the code
under test. On `pull_request` events the checked-out commit is the merge of the PR
into its base, so "the head" below means the merged result.

```yaml
name: reproduction-required
on:
  pull_request:
    types: [opened, synchronize, reopened, labeled, unlabeled]
permissions:
  contents: read
  pull-requests: read
jobs:
  fail-then-pass:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.labels.*.name, 'bugfix')
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: dorny/paths-filter@v4 # pin to a commit SHA
        id: tests
        with:
          list-files: shell
          filters: |
            tests:
              - added|modified: 'tests/**'
      - name: a bug fix must add or change a test
        if: steps.tests.outputs.tests != 'true'
        run: |
          echo "A bugfix PR must contain a test that reproduces the bug."
          exit 1
      - name: install
        # add your setup-python / build steps here
        run: pip install -e ".[dev]"
      - name: the new tests must fail on the base branch
        env:
          TEST_FILES: ${{ steps.tests.outputs.tests_files }}
        run: |
          git checkout ${{ github.event.pull_request.base.sha }}
          git checkout ${{ github.sha }} -- tests/
          if echo "$TEST_FILES" | xargs pytest; then
            echo "The new tests pass on the base branch: they do not reproduce a bug."
            exit 1
          fi
      - name: and pass on the head
        env:
          TEST_FILES: ${{ steps.tests.outputs.tests_files }}
        run: |
          git checkout ${{ github.sha }}
          echo "$TEST_FILES" | xargs pytest
```

Where it can be fooled: the gate checks that the new tests fail on base and pass on
head, and a test can fail on base for the wrong reason, for example an import error
rather than the reported bug. The reviewer still reads the test; the gate guarantees
there is a real, runnable one to read. Projects with compiled extensions need a
rebuild step after each checkout, and a PR that touches only test helpers can make
pytest collect nothing, which reads as a failure.

## 3. Disclosure footer present

The PR description must contain an `AI use:` line, any value including "none". Several
projects ask for a disclosure in their PR template (MicroPython added AI checkboxes to
its template in March 2026) and enforce it manually; this check automates the
enforcement. Disclosure is a prompt, honesty is not machine-checkable, and measured
disclosure rates are lower bounds (see [../data/](../data/)).

```yaml
name: ai-disclosure
on:
  pull_request:
    types: [opened, edited, synchronize, reopened]
permissions:
  pull-requests: read
jobs:
  disclosure:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v9
        with:
          script: |
            const body = context.payload.pull_request.body ?? '';
            if (!/^\W{0,4}AI use:/im.test(body)) {
              core.setFailed('The PR description must contain an "AI use:" line (any value, including "none").');
            }
```

The `edited` trigger type matters: without it, fixing the description never re-runs
the check and a required check stays red. Match the pattern to your PR template; the
`\W{0,4}` prefix accepts bold or list markup around the line. Read the body inside
`github-script` or pass it through `env:`; interpolating
`github.event.pull_request.body` directly into a `run:` script lets a crafted
description inject shell commands.

## 4. Dependency and CI freeze for first-time contributors

Changes to dependency files, CI configuration, or release workflows from first-time
contributors fail a check until a maintainer applies an approval label.

```yaml
name: sensitive-paths
on:
  pull_request:
    types: [opened, synchronize, reopened, labeled, unlabeled]
permissions:
  contents: read
  pull-requests: read
jobs:
  freeze:
    runs-on: ubuntu-latest
    if: "!contains(github.event.pull_request.labels.*.name, 'maintainer-approved')"
    steps:
      - uses: dorny/paths-filter@v4 # pin to a commit SHA
        id: sensitive
        with:
          filters: |
            sensitive:
              - '.github/workflows/**'
              - 'pyproject.toml'
              - 'requirements*.txt'
      - name: sensitive paths need maintainer approval
        if: >-
          steps.sensitive.outputs.sensitive == 'true' &&
          contains(fromJSON('["FIRST_TIME_CONTRIBUTOR", "FIRST_TIMER", "NONE"]'), github.event.pull_request.author_association)
        run: |
          echo "Dependency or CI changes from first-time contributors need a maintainer"
          echo "to apply the maintainer-approved label."
          exit 1
```

Block on the association values listed above. The inverse condition, blocking unless
the author is `MEMBER`, misfires: organization members with private membership can
surface as `CONTRIBUTOR`
([actions/github-script#643](https://github.com/actions/github-script/issues/643)).

Where it can be fooled: the label persists, so once applied it also clears every later
push to the same PR. A contributor can add sensitive changes after approval; a
maintainer who wants per-push control removes the label after merging or relies on
the CODEOWNERS route below.

Two simpler mechanisms cover part of the same ground. A `CODEOWNERS` entry for
`.github/workflows/` and the dependency files, combined with the "require review from
code owners" branch rule, freezes those paths for every non-owner, first-time or
otherwise. And GitHub's default setting already requires maintainer approval before
workflows run on a first-time contributor's PR, which gates execution although it does
not gate merging.

## 5. Equivalence verification where it exists

For compiler or transpiler changes: run the project's circuit-equivalence suite in
addition to the unit tests, exact for small circuits, stabilizer or sampled comparison
for larger ones. Tools, costs, and their limits are in the
[verifier catalog](../verifiers/). This gate is project-specific; the pattern is a
dedicated CI job that runs the equivalence suite whenever the transpiler or compiler
paths change, using the same paths-filter mechanism as gate 1.

## Making a gate required

Any of these workflows becomes blocking through branch protection or a repository
ruleset ("require status checks to pass"). Two behaviors of required checks shape the
patterns above. A job skipped by its `if:` condition counts as passing, which is what
makes label exemptions work. A workflow filtered out at the `on:` level never creates
its check, and the merge waits forever for it, so all filtering above happens at the
job and step level.

## Notes

- Gates filter mechanically what does not need human judgment, so review time goes to
  the parts that do.
- Publish the gates in CONTRIBUTING so contributors, human or agent, can run them
  locally before opening the PR.
- Set an explicit `permissions:` block in every workflow, as the examples do.
- The current majors used above (paths-filter v4, github-script v9) run on Node 24 and
  need Actions Runner 2.327.1 or newer; GitHub-hosted runners qualify, and the
  previous majors remain available for older self-hosted fleets.
