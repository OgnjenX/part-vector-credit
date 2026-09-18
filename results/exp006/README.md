# EXP006 data and reproduction

The repository keeps the frozen EXP006 protocols, summaries, classifications,
figures, and SHA-256 manifests. The 20 compressed raw array files are about
3.9 GB in total, so they are not stored in Git.

The tracked `SHA256SUMS.json` files contain the expected digest of every raw
array and of each summary. They preserve a byte-level record of the frozen
outputs without requiring the large arrays to be part of the source history.

## Recreate the raw arrays

From the repository root, install the locked environment and write the
reproduction outputs outside the repository:

```bash
uv sync --extra dev
uv run part-credit-exp006 confirmatory \
  --output /tmp/part-vector-credit-exp006-primary
uv run part-credit-exp006 confirmatory \
  --population secondary \
  --output /tmp/part-vector-credit-exp006-secondary-n8
```

The confirmation command verifies the frozen configuration and source hashes
before it runs. It also refuses to overwrite an existing output directory.
Compare the recreated `SHA256SUMS.json` files with the tracked manifests in
`frozen_v1_primary` and `frozen_v1_secondary_n8` to verify the outputs.

The smaller tracked files are sufficient to inspect the reported numerical
results and classifications. The raw arrays are needed only to repeat analyses
that operate on the stored trial-level and cell-level traces.
