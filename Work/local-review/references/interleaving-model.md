# Interleaving model

Turn a concurrency hotspot into a finite list of **legal orders**, check every order against the hotspot's invariants, and report exactly what was checked. Exhaustive enumeration of the reduced list is the check; random or stress schedules only supplement it.

## 1. Write the model

Write the model into the report before driving anything. Derive every item from the code and cite lines.

- **States** of the shared entity and its legal transitions (for a request, for example: none → saved → posting → accepted → running → stopping → terminal → cleared, plus replaced). Name the line that performs each transition.
- **Actors**: every party that can drive a transition — each instance (tab A, tab B, window, process, device), the server, timers, storage or broadcast events — and the operations each one runs.
- **Suspension points** of each operation in code order: `await`, callback, timer, lock wait, event listener.
- **Critical events**: events that change intent, ownership, or identity — stop or cancel intent written, receipt or acceptance recorded, terminal reached, shared record cleared, request replaced or taken over, scope or account switched.
- **Outcome classes** of every external call, kept apart by meaning: success, explicit rejection, retryable failure, unknown acceptance (sent, result not known), not cancellable yet (saving, locked, in transition), not found, superseded.

## 2. Reduce to legal orders

Along each **critical path** (a path whose steps can break an invariant), enumerate the orders of critical events against suspension points, then reduce. Record each reduction with its reason and the count before and after.

1. **Causality** — drop orders that violate happens-before: a receipt before its request exists, a terminal before acceptance, a callback before its registration, a read of a record before any writer could create it. Cite the line or protocol rule that enforces the order.
2. **Commutation** — merge orders that differ only in the relative order of operations on disjoint state (for example an independent quota read against a request write). Name the disjoint state. Operations that read or write the same shared record, the same local ref, or the same UI flag never commute.
3. **Critical placement** — for each critical event and each suspension point of another actor that later reads the state the event changes, keep both placements: the event lands before that suspension point resumes, and after it. These pairs are where stale snapshots, lost intents, and stuck waiting states live.
4. **Representative per guard** — orders that reach the same guard with the same outcome class may share one representative case; name the guard. Orders reaching different outcome classes stay separate cases even when one guard handles them all.

The reduced list is the hotspot's cell list. If it still exceeds what the review can drive, state the number, drive the orders that touch the most invariants first, and mark the rest unchecked.

## 3. Drive every order

- Make the harness choose the order: deferred promises, gated locks, fake timers, a controllable scheduler. Timing-dependent runs prove nothing about a named order.
- Use the real module under review. Mock only the boundary (network, storage backend, clock, lock primitive).
- Assert every invariant when the order completes and at every quiescent point in between: intent progresses (a recorded stop ends in a cancel or a terminal), identity holds (each action targets the request currently owned or observed), waiting ends (every waiting state exits on every terminal or foreign clear).
- A random or stress schedule counts toward a cell only when the exact order it hit is recorded and replayable; otherwise it is supplementary evidence.
- When the toolchain cannot run (read-only sandbox, missing SDK), walk each reduced order by reading, citing the line at each step, and mark the method `reading`. A walked order can confirm a `defect`; an order marked `ok` by reading alone is reported as reading-only and cannot support `PASS` — with no blocking defect, the decision stays `UNVERIFIED`.

## 4. Report

Per hotspot, in the matrix:

- the model (states, actors, suspension points, critical events, outcome classes), compact;
- the reduction chain with counts: raw → after causality → after commutation → after critical placement → after representatives;
- each reduced order: one line naming the order, the method (`harness`, `reading`, `test`), and `ok` / `defect` / `unreachable`;
- the unchecked orders, which keep the decision at `UNVERIFIED`.
