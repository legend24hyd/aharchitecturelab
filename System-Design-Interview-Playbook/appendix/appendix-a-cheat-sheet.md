---
slug: appendix-a-cheat-sheet
status: draft
---

# Appendix A — Board cheat sheet

Use this when the clock is loud.

1. Restate the problem in one sentence. Name what is out of scope.
2. Functional requirements, then two NFRs that would change the diagram.
3. Rough QPS, payload, stored bytes, read/write ratio. Convert with powers of two. Check hops against latency orders of magnitude (Chapter 3).
4. Four to six APIs or events. Two or three entities and their keys.
5. One picture: clients, edge, app, data, async.
6. Deep dive the bottleneck the numbers pointed to. Name a trade-off pair: performance vs scale, latency vs throughput, or availability vs consistency. If you shard a cache or mapping store, say whether ownership is `% N` or a hash ring (Chapter 14).
7. Close with two risks, two metrics, and what another hour would buy. If create is abuse-prone, name the 429 path (Chapter 17) without putting it on the user-facing GET.
