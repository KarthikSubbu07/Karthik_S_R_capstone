import pytest
from unittest.mock import AsyncMock, patch
from src.pipeline.fake_llm import Question, Answer, FakeLLMError
from src.pipeline.settings import Settings

async def test_ask_llm_calls_fake_once():
    """testing ask_llm calls the fake LLM once."""
    fake_answer = Answer(
        question="what is RAG",
        text="Mocked answer",
        cost_usd=0.001,
        retries=0,
    )
    with patch(
        "src.pipeline.pipeline.fake_ask_llm", 
        AsyncMock(return_value=fake_answer),
    ) as m:
        from src.pipeline.pipeline import ask_llm
        result = await ask_llm(
            Question(question="what is RAG"),
            Settings(use_fake=True),
        )

    assert m.call_count == 1
    assert result.content == "Mocked answer"
    

async def test_retry_three_times_on_failure():
    """test that ask_llm retries three times on failure."""
    with patch(
        "src.pipeline.pipeline.fake_ask_llm", 
        AsyncMock(side_effect=FakeLLMError("simulated")),
    ) as m_call, patch(
        "src.pipeline.pipeline.asyncio.sleep",
        AsyncMock()
    ):
        from src.pipeline.pipeline import ask_llm_with_retry
        with pytest.raises(FakeLLMError):
            await ask_llm_with_retry(
                Question(question="What is RAG?"),
                tries=3,
                settings=Settings(use_fake=True),
            )
    
    assert m_call.call_count == 3