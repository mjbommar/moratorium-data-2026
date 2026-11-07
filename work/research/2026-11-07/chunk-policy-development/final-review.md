**Verdict: no correctness issues found in the reviewed changes.**

- Invalid chunk policies and unsupported overrides raise `PreflightRejected` before resumable state or backend calls. The domain adapter preserves the existing packet and state for that exception; a failed same-context rerun still removes the stale domain packet.
- Resolved chunk parameters are pinned in the workspace context and passed to the compatible native extractor. The installed older runtime rejects explicit overrides before requests.
- Targeted tests passed: **33** with the installed runtime and **57** with the isolated runtime at `9eeb6bfb`, including its chunk-policy unit tests; each run also passed six subtests.
- The [support-windows report](/home/mjbommar/projects/personal/moratorium-data-2026/work/research/2026-11-07/chunk-policy-development/support-windows.json) confirms that the Harwood moderate primary quote fits a default window, while its selected full support set does not. This is a joint-context measurement for two development documents, not evidence of model-quality improvement.

No paid execution was performed. For accounting, `max_attempts=1` denotes one backend attempt; SDK and agent retries are zero and `max_model_requests=1`. Per-backend-call dollar reservations are estimated metering, distinct from the observed HTTP request cap and any provider invoice.
