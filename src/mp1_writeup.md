| Strategy | Accuracy (mean) | Parse rate | Judge score | Cost ($) | Latency p50 (s) |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Zero-shot | 2.6 / 3 | 0% | 20 / 25 | $0.00003498 | 1.40s |
| Few-shot | 2.9 / 3 | 100% | 24 / 25 | $0.00004740 | 1.20s |
| Structured | 2.8 / 3 | 100% | 25 / 25 | $0.00006600 | 1.42s |
| CoT | 2.6 / 3 | 20% | 20 / 25 | $0.00008874 | 1.66s |


Strategy Comparision:
In terms of accuracy, parse rate, LLM Judge score [ Quality metrics], Structured and Few shot prompting are very closly matched. Few shot prompting is slightly cheaper and faster compared to Structured Prompting, and its a close casll between those 2.

What Surprised You:
The inefficiency of CoT prompt, I expected better form that prompt, though prompt engineering could fix some of the formatting issues.

Capstone domain, which strategy would you reach out first:
Structured.  Providing a proper structure is always the best way.  I also think there is a slight variation in score, bec of '.' for the company names, whcih if cleaned up, will give even better accuracy.

What woudl you try next:
Try an open source model to see how efficient it is for the Few shot and Structure prompts.  Can we save evaluation cost by using a cheaper nodel.  I believe the cost of eval would have been higher in this project, since we are use 4-o for eval, which is 15x times costlier than mini.