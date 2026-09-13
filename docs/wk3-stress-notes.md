- **Finding 1 — Malformed JSON.** 
None reached the app code, all of them gave a 422 error
Streaming worked, we did not hit token limit
- **Finding 3 — Disconnect mid-stream.** What the server logged on `--max-time 1`; whether `/health` still responded after.
1004 milliseconds was when it timed out after it started printing approx 8 words 
- **Finding 4 — 50 parallel requests.** Successes out of 50; p50 / p95 latency; effective req/s; whether SQLite captured all entries.
Was very slow actually dont think its the networks its how gpt 4o mini is I think
Latency (successful requests):
  min:   3.03s
  p50:   14.69s
  p95:   30.46s
  max:   35.10s
