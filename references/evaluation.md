# Evaluation guide

## Package regression checks

From the repository root, run:

```bash
python scripts/validate-package.py
python -m unittest discover -s tests -v
npx --yes skills@1.5.20 add . --list
claude plugin validate .
```

Use `python3` instead of `python` where that is the available interpreter. The last two checks require Node.js and Claude Code respectively. Discovery is not installation and does not test the quality of a rewrite.

The Python tests execute the actual validator on disposable package copies. They cover duplicate headings and table rows, gaps, version mismatches, invalid numbered section references, missing linked documents, and renamed patterns. These are packaging tests, not proof that a language model follows the prompt.

## Rewrite smoke evaluation

1. Load the exact candidate SKILL.md, not an older installed version.
2. Use [structured cases](preservation-cases.json) for inference, attribution, action modality, uncertainty, fiction editing, numeric bounds, and protected spans. Give the rewriting model only each source plus the candidate skill, not expected rewrites. Return final prose in embedded mode; place any factual concerns in a separate field. Keep raw model output. The examples document provides additional manual cases.
3. Compare the output claim by claim with the source. Record model identity if exposed, skill version, cases, failures, and the output file location. Never report the expected example as if a model generated it.
4. Reject added or lost facts, numbers, ranges, conditions, negation, attribution, uncertainty, citations, protected code, URLs, quotations, or invented personal reactions. A rewrite can differ from the suggested After and still pass.
5. Check readability and voice separately. Unchanged text is acceptable where no edit helps. Do not reward aggressive shortening that loses information.
6. Before broad adoption, repeat with the intended deployment model and representative user documents. One small smoke evaluation is not a reliability benchmark.

## Limits

This is a prompt, not a deterministic rewrite engine or fact verifier. Static checks cannot prove semantic equivalence. Human review remains necessary for financial, legal, audit, medical, and safety-critical writing. Preserve factual claims when editing, and report suspected errors separately. The skill does not promise to evade AI detectors or establish authorship.

## Hermes adoption

Update the existing `humanizer` skill rather than creating another skill with the same name. Back up its directory outside the scanned skills tree first. Install the corrected SKILL.md and its referenced documents, retain the MIT license and attribution, and compare installed file hashes against the tested candidate. On Windows, use the actual HERMES_HOME, not a guessed Unix path.

If normal skill discovery fails because of an unrelated path error, report that separately. A direct file read confirms the installed artifact, not successful discovery in the active session. Start a new session to load the revised skill after discovery is working; do not reset an active conversation automatically.
