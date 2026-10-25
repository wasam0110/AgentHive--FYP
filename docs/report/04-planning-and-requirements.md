# Chapter 4 — System Planning and Requirements

Status: Requirements draft. Shizza consolidates; all module owners review.

## 4.1 Non-functional requirements

### Performance

Measure response and processing time separately from human waiting. PRD targets are goals, not observed results.

### Availability and reliability

Stored conversations remain viewable during provider failures. Persist waiting state and prevent repeated side effects after retries. Verify a basic restart scenario during FYP-I.

### Capacity and scalability

One configured business at a time is the baseline. Record tested concurrency and hardware; do not claim production scale.

### Maintainability and manageability

Use typed interfaces, focused modules, reproducible setup, meaningful tests and clear operational errors.

### Security

Enforce authentication, ownership, role checks, proposal versioning, consent and approval in backend code. Do not expose credentials or unnecessary personal data in traces.

## 4.2 Functional requirements

| ID | Requirement | FYP-I evidence needed |
|---|---|---|
| F1 | Identify complaint and service request in one message | Intake test and real integrated trace |
| F2 | Retrieve support evidence | Source IDs and reviewed response |
| F3 | Produce deterministic quote and available slots | Calculation and query tests |
| F4 | Collect separate consent and approval | Accepted/rejected/stale tests |
| F5 | Execute once with valid booking | Receipt, duplicate and contention tests |
| F6 | Display connected chat, approval and inspector | Real backend UI journey |

Use the detailed PRD requirements for full-release traceability; add actual test paths when implemented.

## 4.3 Existing system study

### 4.3.1 Overview

Document the selected customer-service process using a supervisor-approved scenario. No real business interview or process observation is claimed yet.

### 4.3.2 Specifications

Record current channels, participants, data, response steps and limitations when verified.

### 4.3.3 Conclusion

Explain which observed requirements justify the proposed modules; distinguish scenario assumptions from field evidence.

## 4.4 Summary

This chapter defines intended behavior. Link implemented requirements to evidence without changing a planned requirement into a claimed result.

## Configuration requirements

Validate business profiles at startup; route only enabled capabilities; load the configured catalog and knowledge sources; retain profile/policy versions on proposals. Run Profile A/B smoke tests with isolated data and unchanged core code. Reject unknown adapters, missing references and disabled booking. The UI displays configured terminology/currency without weakening backend validation.
