"""Retired unsafe bulk-approval entry point.

Approval is a human decision.  This command intentionally makes no changes;
use ``ml.dataset_review --review-ledger-input`` after reviewers complete the
ledger, then train from that derived export.
"""

raise SystemExit(
    "Refusing to bulk-approve samples. Complete a review ledger with reviewer "
    "identity and ISO-8601 timestamps, then derive a reviewed export."
)
