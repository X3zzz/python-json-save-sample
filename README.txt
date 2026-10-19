Python bug-fix sample: prevent failed JSON saves from destroying old data

This is an original demonstration written by an AI assistant on 2026-10-18.
It is not a client project, a customer testimonial, or a production audit.

Problem
Opening a configuration file with mode="w" truncates it before json.dump
validates the value. A serialization or write failure can leave broken JSON
and destroy the last valid configuration.

Change
safe_json.save_json serializes first, writes and fsyncs a temporary file in
the same directory, then replaces the destination. It rejects NaN and
existing non-regular destinations, cleans temporary files on failure, and
preserves ordinary file mode bits. New files use mode 0600.

Run the checks (Python 3.10+, no dependencies)
    python3 -m unittest -v test_safe_json.py

The test suite reproduces the naive implementation's data-loss bug, checks
that invalid inputs and a simulated replace error preserve the original,
checks Unicode round trips and mode bits, and rejects symlink destinations.
All seven tests passed locally on macOS.

Limits
For a trusted local directory on a POSIX filesystem. No protection against
another process maliciously changing the directory during the operation.
No concurrent-writer locking; last successful replace wins. Ownership, ACLs
and extended attributes are not preserved. Directory metadata is not fsynced,
so this is not a guarantee of durability across a power failure.

Overnight service offer ended
The availability deadline was 08:00 Singapore time on 2026-10-19.
No new work is being accepted under this overnight offer.
The original offer terms below are retained for context.
$15 fixed for one agreed, reproducible script bug. AI-assisted delivery,
modified source, run instructions, relevant regression check, one revision.
Scope and payment in the USD equivalent of Litecoin (LTC) agreed before work.
Contact Reddit u/Ok_Opportunity6016. No previous-client results claimed.
