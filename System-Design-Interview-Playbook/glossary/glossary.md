---
slug: glossary
status: draft
---

# Glossary

Keep definitions interview-short. Add terms as chapters land.

**Availability.** The share of time a service can do useful work inside its SLO.

**Hot path.** The request the user is waiting on.

**Idempotent.** Doing the same write more than once leaves the same stored result.

**NFR.** Non-functional requirement: latency, availability, cost, compliance, and the rest.

**SLO.** Service level objective: a target you can measure, not a slogan.

**Working set.** The data that must be fast, not the data that merely exists.

**Latency.** Time to finish one action.

**Throughput.** How many of those actions finish per unit time.

**Nines.** Availability spoken as 99.9% (three nines), 99.99% (four nines), and so on; convert to downtime before you promise them.

**CAP (operational).** When replicas cannot agree in time, do you refuse the verb or proceed and repair.

**Eventual consistency.** If writes stop, copies converge; until then a read may be stale.

**Read-your-writes.** The client that wrote a value can read that value back.

**Reliability.** Correct work over time, not merely "the process is up."

