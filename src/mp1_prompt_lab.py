"""Reusable data-loading helpers for the project."""
import asyncio

from dotenv import load_dotenv
from openai import AsyncOpenAI
import pandas as pd
import os
import time
from pydantic import BaseModel, Field
from pathlib import Path
from prompts import PROMPTS
import json
import re

load_dotenv()
_client = AsyncOpenAI(
	api_key=os.environ.get("OPENAI_API_KEY"),
	base_url=os.environ.get("OPENAI_BASE_URL")
)   

class Settings(BaseModel):
    model:         str   = "gpt-4o-mini"
    
class JobDetails(BaseModel):
    strategy_name: str
    snippet_ID: str
    model_raw_response: str
    parsed_response: str
    cost_in_USD: float
    latency_in_seconds: float


RATES = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
}

##Method to load job snippets from a JSONL file.
def load_job_snippets(path : str = "data/job_snippets.jsonl") -> pd.DataFrame:
	"""Load one JSON object per line from the job snippets dataset."""
	return pd.read_json(path, lines=True)

##Method to load the golden set from a JSONL file.
def load_golden_set(path : str = "data/golden_set.jsonl") -> pd.DataFrame:
    """Load one JSON object per line from the golden set."""
    golden_set = pd.read_json(path, lines=True)
    golden_set["years_experience_required"] = (
        pd.to_numeric(golden_set["years_experience_required"], errors="coerce")
        .astype("Int64")
        .astype("string")
    )
    return golden_set

def compute_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Compute estimated USD cost from prompt and completion token counts."""
    in_rate, out_rate = RATES.get(model, (0.0, 0.0))
    return (prompt_tokens * in_rate + completion_tokens * out_rate) / 1_000_000


def extract_json_response(resp):
    """Extract a JSON object from the model response, if valid."""
    try:
        return json.loads(resp.choices[0].message.content)
    except (TypeError, json.JSONDecodeError):
        return None

def get_json_field(value, field, alternates=None):
    alternates = alternates or []
    candidates = [field] + alternates

    if isinstance(value, dict):
        parsed = value
    elif isinstance(value, str):
        text = value.strip()
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
            if not match:
                return None
            try:
                parsed = json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
    else:
        return None

    if not isinstance(parsed, dict):
        return None

    for key in candidates:
        if key in parsed and parsed[key] is not None:
            return parsed[key]
    return None

async def parse_job_snippet(snippet: str, prompt:str, strategy_name: str , snippet_ID: str, tries = 3, settings: Settings | None = None
) -> JobDetails:
    """Retry up to ``tries`` times. Wait 1 s, 2 s, 4 s between attempts."""
    generative_model=settings.model if settings else "gpt-4o-mini"
    for attempt in range(tries):
        try:
            started_at = time.perf_counter()
            resp = await _client.chat.completions.create(
					model=generative_model,
					messages=[
						{"role": "system", "content": prompt},
						{"role": "user",   "content": snippet},
						]
				)
            latency = time.perf_counter() - started_at            
            
            return JobDetails(
                strategy_name=strategy_name,
                snippet_ID=snippet_ID,
                model_raw_response=resp.choices[0].message.content,
                parsed_response=json.dumps(extract_json_response(resp)),
                cost_in_USD=compute_cost_usd(
                    model=generative_model,
                    prompt_tokens=resp.usage.prompt_tokens,
                    completion_tokens=resp.usage.completion_tokens
                ),
                latency_in_seconds=latency
            )

        except Exception as exc:
            if attempt == tries-1:
                raise
            print(f"attempt {attempt+1} failed for snippet: {snippet[:40]} ({exc})")
            await asyncio.sleep(2**attempt)

    raise NotImplementedError("Step 3 — wrap ask_llm with retry + exponential backoff")

async def run_all_strategies(snippet: str, snippet_id: str):
    tasks = [
        parse_job_snippet(
            snippet=snippet,
            prompt=prompt,
            strategy_name=strategy_name,
            snippet_ID=snippet_id,
        )
        for strategy_name, prompt in PROMPTS.items()
    ]
    return await asyncio.gather(*tasks)

def extract_json(text: str) -> dict:
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not match:
        return json.loads(text)
    return json.loads(match.group(1))


def get_trimmed_result_df(result_df: pd.DataFrame) -> pd.DataFrame:
    trimmed_result_df = result_df[['strategy_name', 'snippet_ID', 'model_raw_response', 'parsed_response']]
    trimmed_result_df['company'] = trimmed_result_df['model_raw_response'].apply(lambda x: get_json_field(x, 'company'))
    trimmed_result_df['role'] = trimmed_result_df['model_raw_response'].apply(lambda x: get_json_field(x, 'role'))
    trimmed_result_df['years_experience_required'] = trimmed_result_df['model_raw_response'].apply(lambda x: get_json_field(x, 'years_experience_required'))
    return trimmed_result_df	

async def llm_as_a_judge(llm_response, golden_response):
    """
    Use an LLM[GPT-4o] to evaluate the LLM response against the expected golden response for every job_snippet
    """
    evaluation_prompt = f"""You are an AI evaluator. Your task is to rate the response generated by a different LLM on extracting the company, role, and years of experience required from the given job snippet.
    You will be provided with the actual response from the LLM, and the golden response, which is the expected response.  
    Rate the LLM response on a scale of 1 to 25, with 1 for totally incorrect and 25 for completely correct.
    Consider the following key details
    1.	Was it able to extract information requested.
    2.	Was it able to return the response in a parseable JSON format without any additional text.
    3.  Do not worry about any minor formatting differences between the actual and golden responses.
    4.  If you see any reasoning information, ignore that as it was used to arrive at the extracted values.
    llm_response = {llm_response}\n
    golden_response = {golden_response}
    Return the response as a JSON object with two keys: "rating" containing the rating value and "reason" containing the explanation for the rating.
    """
    resp = await _client.chat.completions.create(
						model="gpt-4o",
						messages=[							
							{"role": "user",   "content": evaluation_prompt},
							], 
      					response_format={"type": "json_object"},
      )
    response_json = json.loads(resp.choices[0].message.content.strip())
    
    return response_json["rating"], response_json["reason"]

async def evaluate_strategy(strategy_name, strategy_df, golden_ds_df):
    comparison_df = strategy_df.merge(
        golden_ds_df,
        left_on="snippet_ID",
        right_on="id",
        how="left",
        suffixes=("_actual", "_gold"),
    )
    for field in ("company", "role"):
        actual = comparison_df[f"{field}_actual"].fillna("").astype(str).str.strip().str.lower()
        expected = comparison_df[f"{field}_gold"].fillna("").astype(str).str.strip().str.lower()        
        comparison_df[f"{field}_eval"] = actual.eq(expected).astype(int)
        
    for field in ("years_experience_required",):
        actual = (
            pd.to_numeric(comparison_df[f"{field}_actual"], errors="coerce")
            .astype("Int64")
            .astype("string")
            .fillna("")
        )
        expected = (
            pd.to_numeric(comparison_df[f"{field}_gold"], errors="coerce")
            .astype("Int64")
            .astype("string")
            .fillna("")
        )
        comparison_df[f"{field}_eval"] = actual.eq(expected).astype(int)

    comparison_df["accuracy"] = comparison_df[
        ["company_eval", "role_eval", "years_experience_required_eval"]
    ].sum(axis=1)
    comparison_df["parsed_response_eval"] = (
        comparison_df["parsed_response"].notna()
        & comparison_df["parsed_response"].ne("null")
    ).astype(int)

    comparison_df_gold = comparison_df[
        ["company_gold", "role_gold", "years_experience_required_gold"]
    ].rename(columns=lambda x: x.replace("_gold", ""))
    llm_response_json = json.dumps(comparison_df["model_raw_response"].iloc[0])
    golden_response_json = json.dumps(comparison_df_gold.iloc[0].to_dict())
    comparison_df["judge_score"], comparison_df["judge_reason"] = await llm_as_a_judge(
        llm_response=llm_response_json,
        golden_response=golden_response_json,
    )
    comparison_df.to_csv(f"data/comp_{strategy_name}.csv", index=False)
    return comparison_df


async def field_eval(trimmed_result_df, golden_ds_df):
    strategy_dfs = {
				f"{strategy_name.removesuffix('_prompt')}_df": trimmed_result_df.loc[
					trimmed_result_df["strategy_name"].eq(strategy_name)
				].copy()
				for strategy_name in PROMPTS
			}	
    tasks = [
        evaluate_strategy(strategy_name, strategy_df, golden_ds_df)
        for strategy_name, strategy_df in strategy_dfs.items()
    ]
    return await asyncio.gather(*tasks)

async def save_filtered_results_to_csv(result_df):
    strategy_dfs = {
					f"{strategy_name.removesuffix('_prompt')}_df": result_df.loc[
						result_df["strategy_name"].eq(strategy_name)
					].copy()
					for strategy_name in PROMPTS
				}	
    for strategy_name, strategy_df in strategy_dfs.items():
        strategy_df.to_csv(f"data/result_{strategy_name.removesuffix('_prompt')}.csv", index=False)
        
async def main():
    jobsnippets_df = load_job_snippets()
    all_results = []

    for i in range(len(jobsnippets_df)):
    # for i in range(1):
        jobsnippet = jobsnippets_df.loc[i, "snippet"]
        snippet_id = jobsnippets_df.loc[i, "id"]
        results = await run_all_strategies(jobsnippet, snippet_id)
        all_results.extend(results)

    result_df = pd.DataFrame([result.model_dump() for result in all_results])
    result_df.to_csv("data/results.csv", index=False)

    await save_filtered_results_to_csv(result_df)
    # result_df = pd.read_csv("data/results.csv")
    trimmed_result_df = get_trimmed_result_df(result_df)
    trimmed_result_df.to_csv("data/trimmed_result_df.csv", index=False)
    await field_eval(trimmed_result_df, load_golden_set())

if __name__ == "__main__":
    asyncio.run(main())
    