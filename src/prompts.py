zero_shot_prompt = """You are an AI Assitant, tasked to extract information from Job Postings accurately and concisely. 
Extract the company name, role, and years of experience required from each job posting and return in JSON format, with the following fields, "company", "role", "years_experience_required".
"""

few_shot_prompt = """You are an AI Assitant, tasked to extract information from Job Postings accurately and concisely. 
Extract the company name, role, and years of experience required from each job posting and return in json format.
Here are some examples:
1. Job Posting: 'Abc Tech Solutions is looking for a Sr Software Engineer with at least 15 years of experience.'
   Output: {"company": "Abc Tech Solutions", "role": "Sr Software Engineer", "years_experience_required": 15}
2. Job Posting: 'Sagility is hiring for a candidate with at least 4+ years of experience.'
   Output: {"company": "Sagility", "role": "null", "years_experience_required": 4}
Now, extract the information from the following job posting."""

structured_prompt = """You are a helpful assistant specializing in extracting structured information from job postings. 
Extract the company name, role, and years of experience required from each job posting and return in json format.
Follow this schema exactly:

{
  "type": "object",
  "properties": {
    "company": {
      "type": "string",
      "description": "The company name, without expansion or any added text, stick to what is in the job posting."
    },
    "role": {
      "type": "string",
      "description": "The job title or role"
    },
    "years_experience_required": {
      "type": ["integer", "null"],
      "minimum": 0,
      "description": "Minimum required years of experience, or null if not stated.  If the description states "Around 6 years"* → 6. *"7+ years"* → 7.* "Between 3 and 5"* → 3 (the minimum)"
    }
  },
  "required": [
    "company",
    "role",
    "years_experience_required"
  ],
  "additionalProperties": false
}

Rules:
- Return only JSON.
- If a particular field is not specified in the job posting, return "null" as the value.

Job posting: \n
"""

cot_prompt = """You are an AI Assitant, tasked to extract information from Job Postings accurately and concisely. 
Extract the company name, role, and years of experience required from each job posting and return in JSON format. 
Think step by step before giving the final answer.
Provide the response in JSON format, with the following fields, "company" as string, "role" as string, "years_experience_required" as integer with minimum years as value and "reasoning", where "reasoning" contains a valid reasoning on how your arrived at this extracted value."""


PROMPTS = {
  "zero_shot_prompt": zero_shot_prompt,
  "few_shot_prompt": few_shot_prompt,
  "structured_prompt": structured_prompt,
  "cot_prompt": cot_prompt,
}