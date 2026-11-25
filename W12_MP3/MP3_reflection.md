# MP3 Reflection    
         
    ## Grounding & abstention    
    Where did your assistant abstain correctly? Did it ever answer something it    
    shouldn't have (or refuse something it could have answered)? What threshold did    
    you settle on, and why?    
    The assistant answered all the abstain Questions correcly, mentioning it did not know the answer based on the provided contexts.  I will settle with this threshold bec of multiple reasons.  The current threshold in itslef is very low [ 0.3], so a chance of retrieving a correct snippet below that is very rare and the pipeline needs to work for all generic data and we should not tune this for 1-2 Q's.


         
    ## Citations    
    Did the model ever cite a chunk that didn't support the claim, or invent a marker?    
    What did `validate_citations` catch?    
    As u can infer from the metrics, the hallucination rate is 0 and the grounded rate is 0.66, which does mean tht there is no hallucation and no invention of claims.
         
    ## Reading your eval table    
    What do your four numbers say? Which is weakest, and what would you change?    
    Groundedness, is indeed the weakest and I also figured out why.  There are couple of Q's which are multihop and is failing bec the answer is generated partially, and the second part of the Q is abstined.  Since the way we have setup eval, if the term abstain is present we mark it as abstained, we are rating these Q's 0.  Either we can change the whay it is rated ,. to provided ratings for partial answers or change the prompt to be more clear.  Ideally we need to improve the chunking [which is the root case of this failure] to improve retreival, answer Quality and eventuqlly groundedness.
         
    ## One surprise    
    Something from the build that genuinely surprised you.    
    Again the way partial answers are generated and rated.  And not getting citation for partial answer for which I will change the promopt to include inline citations rather than citing at the end.  Also most of the answers have only one citation, which is interesting since u can get answers from multiple sources.
