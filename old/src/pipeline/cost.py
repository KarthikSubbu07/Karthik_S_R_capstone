"""W4 STARTER — src/pipeline/cost.py

Real cost computation. response.usage tells you tokens; this module turns
tokens into USD.

Lab Step 2c builds this out.
"""

# Order-of-magnitude rates as of late 2025. Confirm against
# https://artificialanalysis.ai before quoting in production.
# These are USD per 1M tokens.
RATES = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "llama3.2:3b": (0.0, 0.0),
}


def compute_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Convert a usage tuple into USD.

    Args:
        model: One of the keys in RATES.
        prompt_tokens: From response.usage.prompt_tokens.
        completion_tokens: From response.usage.completion_tokens.

    Returns:
        Cost in USD as a float. Returns 0.0 if the model isn't known
        (don't raise — that would break batch runs).

    Examples:
        # gpt-4o-mini at $0.15/M in, $0.60/M out
        # 100 prompt tokens + 50 completion tokens
        # = (100 * 0.15 + 50 * 0.60) / 1_000_000
        # = (15 + 30) / 1_000_000
        # = 0.000045 USD
    """
    try:
        in_rate, out_rate = RATES.get(model, (0.0, 0.0))
        total = (prompt_tokens * in_rate + completion_tokens * out_rate) / 1_000_000
        return total
    except Exception:
        return 0.0
    
