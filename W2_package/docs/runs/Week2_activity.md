what did `as_completed` make visible that `gather` hides?
Gather did wait for the results of all the 5 Q's availble, and then print in the terminal
as_completed, printed as and when the answer was available

when would you reach for `gather`, and when for `as_completed`?
When the use case needs answer of all Q's or tasks to be completed before proceeding further we should use Gather
But if the next step is not dependent dependent on the completion of all the tasks we can use as_completed