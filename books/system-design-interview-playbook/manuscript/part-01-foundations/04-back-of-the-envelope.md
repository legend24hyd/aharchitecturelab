---
slug: back-of-the-envelope
status: draft
---

# Back-of-the-envelope estimates

*Outline for Version 1.0 — expand during writing.*

## Why numbers belong on the board

A cache, a queue, or a shard is a claim about volume. Make the volume visible.

## The small table you always fill

QPS (peak and average), payload size, stored bytes per year, fan-out, working set vs cold data.

## Rules of thumb (and when they lie)

Seconds in a day, bytes in a UTF-8 URL, replication overhead, index bloat. Interviewers care that you **show the arithmetic**, not that you memorized a constant.

## From estimate to component

“This working set fits in memory” → cache.  
“Writes are bursty and consumers are slow” → queue.  
“Single primary cannot hold the QPS” → partition.
