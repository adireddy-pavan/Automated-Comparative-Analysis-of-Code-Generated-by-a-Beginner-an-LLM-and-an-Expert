# Future independent reviewer packet — BLIND TO SOURCE LABELS

No reviewer ratings have been collected. Do not pretend this packet is evidence of completed review. Before recruiting raters confirm any institutional ethics/consent requirements. Reviewers should not inspect the original repository, original class labels or private key before returning ratings.

Read the SPECIFICATION.txt in each task folder; then assess candidate_A.py and candidate_B.py in randomised source-label order. Supply the blank form with independent ratings and critical comments, and give the date and reviewer qualification (using an institution-approved identifier). An external reviewer should independently assess edge-case coverage and task difficulty, not assume the author-assigned tiers are correct. Ratings must be recorded before the private key is opened. The experimenter should preregister agreement and adjudication criteria in advance, document all exclusions and never edit submitted ratings.

This packet holds 60 constructed reference solutions, not code collected from actual novices or expert programmers. Evaluating the labels does not turn them into real participant output.

Additional form field: `perceived_level` MUST be filled with beginner, expert, or uncertain for each anonymised candidate; the existing `source_label` column must remain WITHHELD. The assigned source labels are not expected to be guessed with certainty. Reviewers must submit original dated files and a signed/approved `REVIEWER_ATTESTATION.txt` under their respective submission directories. Never include the private key in the reviewer packet. Once received, run `python tools/external_evidence_review.py` to validate form completeness and calculate agreement.
