# EXP-08 Test Reserve Compatibility

## Conclusion: PATCH_REQUIRED

The Day 2 Task 08 implementation already provides valuable reusable behavior: unique-ID and label validation, group-aware assignment, C-aware stratification, zero group leakage checks, one locked split manifest and preprocessing views created after splitting.

It does not yet explicitly implement the revised handoff policy:

1. `TEST_RESERVE_CANDIDATE` is not automatically the final test set.
2. Candidate reserve is approximately 11.5% of `N_model` and is human blind-finalized first.
3. EXP-08 must select final test at approximately 10% of `N_model`, stratified mainly by final C and group-aware.
4. Unselected reserve records return to the train/dev pool.
5. All preprocessing views must reuse that final locked manifest.

No real split is required at Day 3. Patch Task 08 only when FINAL-07 inputs and the latest Phúc-approved policy are READY.
