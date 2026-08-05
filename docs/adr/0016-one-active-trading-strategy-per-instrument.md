# Authorize one active trading strategy per instrument

An instrument may have many research and shadow candidates but only one active strategy authorized to propose a new live position. When that strategy is replaced while it owns an actual position, it becomes retiring and continues managing that position to closure; the successor cannot open the same instrument until the position is flat. This avoids inventing virtual lot attribution that the manually operated broker account cannot reliably preserve.
