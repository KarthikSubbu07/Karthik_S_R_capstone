# import asyncio, time
# # from pipeline import ask_llm, Question
# # ans = asyncio.run(ask_llm(Question(text='What is RAG in one sentence?')))
# # print('type:', type(ans).__name__)
# # print('text:', ans.text[:80])
# # print('cost:', ans.cost_usd)
# # print('retries:', ans.retries)

# try:
#     from .pipeline import ask_llm_with_retry, Question, run_batch
# except ImportError:
#     from pipeline import ask_llm_with_retry, Question, run_batch

# # # Clean — should succeed on attempt 0, no retries
# # ans = asyncio.run(ask_llm_with_retry(Question(text='What is RAG?')))
# # print('clean:    retries =', ans.retries)

# # # Always-fail — should retry twice (3 attempts total) and then raise
# # try:
# #     asyncio.run(ask_llm_with_retry(Question(text='What is RAG?'), fail_rate=1.0))
# # except Exception as e:
# #     print('lossy:    raised after 3 attempts:', type(e).__name__)

# questions = [
#     Question(text='What is RAG?'),
#     Question(text='Name three uses of vector databases.'),
#     Question(text='Why might an LLM hallucinate?'),
# ]
# t0 = time.time()
# answers = asyncio.run(run_batch(questions))
# elapsed = time.time() - t0
# print(f'wall-clock: {elapsed:.2f}s')
# for a in answers:
#     print(f'- {a.text[:60]}')

# import asyncio
# from fake_llm import Question, Answer, fake_ask_llm, FakeLLMError
# print(asyncio.run(fake_ask_llm(Question(text='What is RAG?'))))

from pipeline import ANSWER_TOOL
from models import Question, Answer

print('name :', ANSWER_TOOL['function']['name'])
print('properties:', list(ANSWER_TOOL['function']['parameters']['properties'].keys()))
print('required :', ANSWER_TOOL['function']['parameters']['required'])

a = Answer(
    content="This is a test answer.",
    # cost_usd=0.0,
    # retries=0,
    # confidence=1.0,
    # sources=["source1", "source2"],
    # schema_version="v1"
)
print(a.model_dump())
