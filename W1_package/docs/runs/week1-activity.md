**Prompt A — "You are concise."**

running 
python src/hello_llm.py "Explain quantum entanglement in two sentences."

Response:
Quantum entanglement is a phenomenon where two or more particles become linked, such that the state of one particle instantaneously affects the state of the other, regardless of the distance between them. This creates a correlation between their properties that cannot be explained by classical physics, challenging our understanding of separation in space and time.

**Prompt B**

Response:
Quantum entanglement is a phenomenon where two or more particles become interconnected in such a way that the state of one particle instantaneously influences the state of the other, regardless of the distance between them. This occurrence challenges classical intuitions about separability and locality, leading to implications for quantum computing and information theory.

**Prompt C**

Response:
In realms where particles entwine their fate,  
Two souls connected, distant yet as mate.  

When one is changed, the other knows, though far,  
A dance of threads unseen, like light from star.  

**Prompt D**

Response: 
Quantum entanglement is a phenomenon where two or more particles become interconnected in such a way that the state of one particle instantly influences the state of the other, regardless of the distance separating them. This nonlocal connection defies classical intuitions about separability and locality, leading to implications that challenge conventional understandings of information and measurement in quantum mechanics.

 **What changed?**

 - What stayed the same across all four answers?
 The model used for the LLM call
 The Question
 The format
- What changed the most?
The system message/ Role played by the LLM
- Where would you reach for a *system prompt change* in a real product instead of fine-tuning the model?
If u want answers in a particular perspective or tone, or based on a particular domain we can system prompt change.


**Stretch**
Temperature 0
Quantum entanglement is a phenomenon where two or more particles become interconnected in such a way that the state of one particle instantaneously influences the state of the other, regardless of the distance separating them. This non-local correlation challenges classical intuitions about separability and locality, leading to implications for quantum computing and information theory.

Temperature 1.5
Quantum entanglement is a phenomenon where pairs or groups of particles become interlinked, such that the state of one particle instantaneously influences the state of the other, regardless of the distance separating them. This visionary connection challenges conventional notions of locality and separateness in physics, as measurements on entangled particles lead to correlated results that cannot be explained by classical physics.

**multi-turn**
Input
 messages=[
            {"role": "system", "content": "You are concise."},
            {"role": "user",   "content": question},
        ]

python /voc/work/hello_llm.py "What according to you is the best way to learn"

Response
The best way to learn varies by individual, but effective strategies include:

1. **Active Engagement**: Involve yourself by taking notes, asking questions, and participating in discussions.
2. **Practice and Repetition**: Apply knowledge through exercises and practical applications to strengthen retention.
3. **Spaced Repetition**: Study material over spaced intervals to enhance long-term memory.
4. **Teach Others**: Explaining concepts reinforces your understanding.
5. **Multisensory Learning**: Combine visual, auditory, and hands-on experiences to cater to different learning styles.
6. **Set Goals**: Create specific, achievable learning objectives to stay focused and motivated.
7. **Self-Assessment**: Test yourself regularly to evaluate your understanding and identify areas needing improvement.

Yes, keeping notes is a good practice. It enhances understanding, improves retention, aids in review, and allows for future reference. Notes can also help you organize thoughts and concepts more effectively.

**Second Query**
{"role": "system", "content": "You are concise."},
            {"role": "user",   "content": question},
            {"role": "assistant", "content": """The best way to learn varies by individual, but effective strategies include:

1. **Active Engagement**: Involve yourself by taking notes, asking questions, and participating in discussions.
2. **Practice and Repetition**: Apply knowledge through exercises and practical applications to strengthen retention.
3. **Spaced Repetition**: Study material over spaced intervals to enhance long-term memory.
4. **Teach Others**: Explaining concepts reinforces your understanding.
5. **Multisensory Learning**: Combine visual, auditory, and hands-on experiences to cater to different learning styles.
6. **Set Goals**: Create specific, achievable learning objectives to stay focused and motivated.
7. **Self-Assessment**: Test yourself regularly to evaluate your understanding and identify areas needing improvement."""},

            {"role": "user",   "content": "Is it good practise to keep notes?"},

**RESPONSE**
Yes, keeping notes is a good practice. It enhances understanding, improves retention, aids in review, and allows for future reference. Notes can also help you organize thoughts and concepts more effectively.

**LAST**

{"role": "system", "content": "You are concise."},
            {"role": "user",   "content": question},
            {"role": "assistant", "content": """The best way to learn varies by individual, but effective strategies include:

1. **Active Engagement**: Involve yourself by taking notes, asking questions, and participating in discussions.
2. **Practice and Repetition**: Apply knowledge through exercises and practical applications to strengthen retention.
3. **Spaced Repetition**: Study material over spaced intervals to enhance long-term memory.
4. **Teach Others**: Explaining concepts reinforces your understanding.
5. **Multisensory Learning**: Combine visual, auditory, and hands-on experiences to cater to different learning styles.
6. **Set Goals**: Create specific, achievable learning objectives to stay focused and motivated.
7. **Self-Assessment**: Test yourself regularly to evaluate your understanding and identify areas needing improvement."""},

            {"role": "user",   "content": "Is it good practise to keep notes?"},
            {"role": "assistant", "content": "Yes, keeping notes is a good practice. It enhances understanding, improves retention, aids in review, and allows for future reference. Notes can also help you organize thoughts and concepts more effectively."},

            {"role": "user", "content": "Best time of the day to do this?"}
        ],


**RESPONSE**

The best time to take notes varies by individual, but generally:

- **Morning**: When the mind is fresh.
- **Post-Lesson**: Soon after learning to reinforce concepts.
- **Before Bed**: To enhance retention due to a sleep-learning connection.

Experiment to find your optimal time.