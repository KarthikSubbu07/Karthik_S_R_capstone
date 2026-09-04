"""Define a single `Settings` class extending `pydantic.BaseModel` with seven fields:"""
from pydantic import BaseModel, Field
from pathlib import Path

class Settings(BaseModel):
    questions_csv: Path  = Path("data/questions.csv")
    results_json:  Path  = Path("results.json")
    results_db:    Path  = Path("results.db")
    batch_size:    int   = Field(5,   gt=0, le=20)
    fail_rate:     float = Field(0.0, gt=0.0, le=1.0)
    model:         str   = "gpt-4o-mini"
    use_fake:      bool  = True
