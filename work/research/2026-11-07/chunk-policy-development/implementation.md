Implemented per-call `chunk_size` and `chunk_overlap` in [extract.py](/home/mjbommar/projects/bc/bc-modules-evidence-chunk-policy/bc-evidence/python/bc_evidence/extract.py). Defaults remain 7,000 and 400; invalid types and ranges fail before backend calls, including for empty documents. Chunking continues to use `bc_content.chunk_text`.

Added tests in [test_extract_chunks.py](/home/mjbommar/projects/bc/bc-modules-evidence-chunk-policy/bc-evidence/tests/unit/test_extract_chunks.py) for boundary-spanning passages and quote offsets, default chunk coverage, concurrent policies, and invalid inputs.

Validation passed using the existing environment: **92 member tests**, Ruff lint and formatting checks, ty, and `git diff --check`. No installs, builds, paid API calls, browser or network use, commits, or pushes. No extraction-quality improvement is claimed.
