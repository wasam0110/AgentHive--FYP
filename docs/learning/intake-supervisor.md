# Structured intake and supervisor routing

The W05 supervisor receives Pydantic-validated intent data and creates typed task definitions without authorizing any mutation. `build_task_plan` assigns task IDs, binds run/conversation IDs and records deterministic dependencies.

Support and sales may run independently. Scheduling waits for sales when both a catalog or service intent and an appointment intent are present. Refund/cancellation requests produce a manual support task, not an execution task.

The provider remains deterministic in demo mode. Hosted output is validated against the Pydantic schema, and extra model fields or write authority are rejected.
