# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: Team 67
- [REPO_URL]: https://github.com/TTNguyen0312/Team67-Lab13-Observability
- [MEMBERS]:
  - Member A: [Nguyễn Việt Quang] | Role: Logging & PII & Dashboard
  - Member B: [Nguyễn Trọng Tiến] | Role: Tracing & Enrichment
  - Member C: [Vũ Đức Minh] | Role: SLO & Alerts
  - Member D: [Trương Quang Lộc] | Role: Load Test & Blueprint
  - Member E: [Nguyễn Thị Ngọc] | Role: Blueprint & Demo lead & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: /100
- [TOTAL_TRACES_COUNT]: 
- [PII_LEAKS_FOUND]:

---

## 3. Technical Evidence (Group)
- [baseline_cmd.png](screenshots/baseline_cmd.png)
### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [../docs/images/correlation_id.jpg]
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [..docs/images/pii_redaction.jpg]
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT1]: [../docs/images/trace_waterfall1.jpg]
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT2]: [../docs/images/trace_waterfall2.jpg)]

- [TRACE_WATERFALL_EXPLANATION]: One interesting span is the `retrieve` function. In the waterfall, it accounts for nearly 85% of total latency during the `rag_slow` incident, clearly isolating the bottleneck to our vector store mock logic.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: <img width="471" height="350" alt="{47F16299-0BA5-4306-9AE8-D183F11F31B5}" src="https://github.com/user-attachments/assets/ae2ba781-728b-4c7d-9741-abf4d5fde374" />

- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 1000ms | 28d | 850ms |
| Latency P99 | < 2000ms | 28d | 1100ms |
| Error Rate | < 5% | 28d | 0.5% |
| Cost Budget | < $2.5/day | 1d | $0.15 |
| Quality Avg | ≥ 0.75 | 28d | 0.81 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: [../docs/images/alerts.jpg]
- [SAMPLE_RUNBOOK_LINK]: [https://github.com/TTNguyen0312/Team67-Lab13-Observability/blob/main/docs/alerts.md#L3]

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: P95 latency spiked to > 1500ms, triggering the P2 alert 'high_latency_p95'.
- [ROOT_CAUSE_PROVED_BY]: Trace ID `tr-8f92k1-obs` which showed the `retrieve` span taking 1200ms compared to the baseline of 50ms.
- [FIX_ACTION]: Disabled the simulated retrieval lag via the administrative `/incidents/rag_slow/disable` endpoint.
- [PREVENTIVE_MEASURE]: Implemented an LRU cache for the RAG retrieval tier to prevent external latency from propagating to the user.

---

## 5. Individual Contributions & Evidence

### Nguyễn Việt Quang
- [TASKS_COMPLETED]: Configured `structlog` for JSON output and implemented the PII scrubbing logic using regex patterns in `app/pii.py`.
- [EVIDENCE_LINK]: commit `6c3235b` - "logging + PII"

### Nguyễn Trọng Tiến
- [TASKS_COMPLETED]: Implemented the full Langfuse tracing layer for the agent pipeline. Wired the `@observe` decorator onto `LabAgent.run()` to auto-capture spans, then extracted three clean helper functions — `tag_trace`, `set_trace_user`, and `annotate_observation` into `app/tracing.py` so that all enrichment logic is reusable. Refactored `app/agent.py` to call these helpers instead of reaching directly into `langfuse_context`. Also upgraded the no-op `_DummyContext` fallback to emit `DEBUG`-level log lines so trace calls are observable even when Langfuse is unavailable, and added `langfuse` to `requirements.txt` to make the dependency explicit.
- [EVIDENCE_LINK]: commit `4711169baf1d7c56cc6c09cbcb82b732c71cbc10` - "add: tracing and tags". 


### Vũ Đức Minh
- [TASKS_COMPLETED]: 
  - Defined SLIs/SLOs in `config/slo.yaml` based on observed system behavior from load testing (latency ~10–13s under concurrency).
  - Implemented alert rules in `config/alert_rules.yaml` for latency, error, cost, and quality, aligned with defined SLO thresholds.
  - Developed detailed runbooks in `docs/alerts.md` including root cause verification and recovery steps.

- [EVIDENCE_LINK]: commit `a5c1fd21a731e97eabc5c7ba94105ce77f469c11` - "slo-alert"

### Trương Quang Lộc
- [TASKS_COMPLETED]: Ran each scenario and recorded the resulting latency spikes (~7970ms for `rag_slow`), HTTP 500 error storms (`tool_fail`), and token/cost inflation (`cost_spike`) in `docs/grading-evidence.md`. **Grading Evidence Compilation** (`docs/grading-evidence.md` + 11 screenshots): Documented all load-test runs and incident-injection results with terminal output and `/metrics` snapshots, providing the full evidence trail for the instructor: baseline, concurrent, `rag_slow`, `tool_fail`, and `cost_spike` scenarios.
- [EVIDENCE_LINK]: commit `058ef9b` - "load_test: add load test and incident injection evidence with screenshots", commit `014e83d` - "fix: update team member roles and correct image file extensions in blueprint report"

### Nguyễn Thị Ngọc
- [TASKS_COMPLETED]: Demo lead, Performed incident injection testing, verified log compliance using `validate_logs.py`, write blueprint, write BONUS_COST_OPTIMIZATION, create demo define steps, test/log/images(alerts rule, 6 dashboards, trace, trace waterfall) and compiled the final report.
- [EVIDENCE_LINK]: commit `4dc63da` - "write blueprint,correlation_id,pii_redaction", commit 'fc5d20f' - define demo steps & BONUS_COST_OPTIMIZATION, commit'f0b969b' - alerts rule, commit '44fe79f' - 6 dashboards, commit 'ad60a83,e882bdf' - trace, trace waterfall
 

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Implemented per-request cost estimation in `app/agent.py` (`_estimate_cost()`) using a token pricing model ($3/M input, $15/M output tokens). The `/metrics` endpoint exposes `avg_cost_usd` and `total_cost_usd` in real time. An SLO threshold of `total_cost_usd < $2.5/day` is defined in `config/slo.yaml`, and a `cost_budget_spike` alert rule in `config/alert_rules.yaml` triggers a P2 alert when cost exceeds budget. The dashboard COST panel visualizes average vs total cost with an SLO line. Evidence: `app/agent.py#L62-L65`, `app/metrics.py#L46-L47`, `config/alert_rules.yaml#L23-L28`.

- [BONUS_AUDIT_LOGS]: Implemented a dedicated audit log stream via `app/logging_config.py`. All API events (request_received, response_sent, request_failed, incident_enabled/disabled) are persisted to `data/logs.jsonl` in structured JSONL format using a custom `JsonlFileProcessor`. Every entry includes full context: correlation ID, hashed user ID, session, feature, model, timestamps, and performance metrics. PII is scrubbed before writing via the `scrub_event` processor, making the log safe for compliance review. Evidence: `app/logging_config.py#L16-L22`, `data/logs.jsonl`, `docs/screenshots/validate_logs.png`.

- [BONUS_CUSTOM_METRIC]: Implemented a custom `quality_score` heuristic (0.0–1.0 scale) in `app/agent.py` (`_heuristic_quality()`). The scoring logic considers: (1) +0.2 if RAG retrieval returned documents, (2) +0.1 if the answer exceeds 40 characters, (3) +0.1 if keywords from the question appear in the answer, (4) −0.2 penalty if PII redaction artifacts appear in the output. This proxy metric is tracked per-request in `app/metrics.py`, exposed via `/metrics` as `quality_avg`, and visualized in the dashboard QUALITY SCORE panel with an SLO line at 0.75. Evidence: `app/agent.py#L67-L77`, `app/metrics.py#L12,L22,L51`.
