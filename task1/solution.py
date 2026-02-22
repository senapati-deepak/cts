import pandas as pd
import json
import os
from pydantic import BaseModel
from openai import OpenAI


# --- Schema Definition ---
class AgentOutput(BaseModel):
    """Enforces the final output format for the Agent."""
    recommended_plan_id: str
    discount_applied_flag: bool
    final_discount_amount: float
    agent_reasoning: str


# --- Tool: Query Customer DB ---
def query_customer_db(user_id: str) -> dict:
    """Simulates the Usage Analyst role querying the local CSV database."""
    # Note: Paths are relative to the script location
    logs = pd.read_csv('./data/tower_logs.csv')
    subs = pd.read_csv('./data/customer_subscriptions.csv')
    transcripts = pd.read_csv('./data/transcripts.csv')
    
    user_log = logs[logs['user_id'] == user_id].iloc[0]
    user_sub = subs[subs['user_id'] == user_id].iloc[0]
    user_transcripts = transcripts[transcripts['user_id'] == user_id]['text_transcript'].tolist()
    
    return {
        "usage_gb": float(user_log['avg_data_gb']),
        "current_plan": user_sub['current_plan_id'],
        "dropped_calls": int(user_log['dropped_calls'] ),
        "complaints": user_transcripts
    }


# --- Helper: Load Prompt ---
def load_system_prompt(filepath: str = "./task1/prompt.txt") -> str:
    """Loads the external prompt asset."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Missing prompt file at {filepath}")
    with open(filepath, "r") as f:
        return f.read()


# --- Agentic Workflow ---
def run_agentic_workflow(user_id: str) -> str:
    """Executes the prompt-driven pipeline using local Ollama LLM."""
    
    # 1. Gather Data (Usage Analyst Role)
    customer_data = query_customer_db(user_id)
    
    # 2. Load System Instructions
    system_prompt = load_system_prompt("./task1/prompt.txt")

    # 3. Connect to local Ollama Server
    llm_base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
    client = OpenAI(base_url=llm_base_url, api_key="ollama")    
    
    response = client.chat.completions.create(
        model="llama3.2",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Customer Data: {json.dumps(customer_data)}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    
    raw_output = response.choices[0].message.content
    llm_decision = json.loads(raw_output)
    
    # 4. Apply Business Logic Guardrail
    # Ensure AI doesn't exceed the $20 discount limit mentioned in requirements
    proposed_discount = float(llm_decision.get("proposed_discount_amount", 0.0))
    final_discount = proposed_discount
    
    if proposed_discount > 20.0:
        final_discount = 20.0
        llm_decision["agent_reasoning"] += f" [GUARDRAIL TRIGGERED: AI proposed ${proposed_discount}, reduced to max $20.]"
    
    # 5. Finalize state for Pydantic Validation
    llm_decision["final_discount_amount"] = final_discount
    llm_decision.pop("proposed_discount_amount", None)
    
    # 6. Enforce output schema and return formatted JSON
    final_output = AgentOutput(**llm_decision)
    return final_output.model_dump_json(indent=2)


if __name__ == "__main__":
    # Ensure Ollama is running and Llama3.2 is pulled before running this
    test_customers = ["CUST_005", "CUST_013", "CUST_376"]
    
    for cid in test_customers:
        try:
            print(f"\n--- Testing {cid} ---")
            result = run_agentic_workflow(cid)
            print(result)
        except Exception as e:
            print(f"Error processing {cid}: {e}")