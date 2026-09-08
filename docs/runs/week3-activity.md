- In one sentence: what's lost if the process restarts? (i.e., what is the `request_counts` dict missing that a real metrics system would provide?)
The request_counts doesnt have a cache or any memory when the connection is terminated or uvicorn is disconnected
- In one sentence: under heavy concurrency, would two simultaneous requests to `/health` always result in the counter going from N to N+2? Why or why not?
unfortunately since its not atomic, we will ahve N=1 and not +2
