I have successfully built the pipleine in the below order
Chunking >> Embedding >> Ingesting >> Query Embedding >> Retreival >> Answer Generation 

My observations, even though the pipeline works the chunking strategy I used is having an effect on the answer Quality.
I have used paragraph chunking bec I feel that doing naive chunking by standard character count might not be very condusive when doing full scale projecs.  Alternately sentence chunking might be too short.  In this case I realise that the paragraphs are too short and hence the chunks are too short as well.

And hence I can see that all the expected facts are not in the actual answer.
I also think since we are use string search to evaluae if the fact is presentor not, there are chances that the accuracy might be misrepresented.

When we have smaller paragraphs, I think its ideal to increase the size of retrieval and hence I changed it from 3 to 5, and saw a marked improvement in the no of facts matched.  

If I had more time, I would have tried slightly different chunking strategy and evaluated the impact of sliding window chunks or alternate strategies.  

I theorotically dont think CROSS Encoder or Hybrid search might actually improve in this particular sceaniro since the corpus is small.  But definitely they would ahve a huge impact on a larger corpus.

The latency is not returned in the openai response api and hence I couldnt capture that.