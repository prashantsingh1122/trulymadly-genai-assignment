import json
import time
from llm.client import chat
from jsonschema import validate, ValidationError

PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "tool": {"type": "string"},
                    "query": {"type": "string"},
                    "limit": {"type": "integer"},
                    "city": {"type": "string"}
                },
                "required": ["tool"],
                "additionalProperties": False
            }
        }
    },
    "required": ["steps"],
    "additionalProperties": False
}


def create_plan(task: str, max_retries: int = 3, retry_delay: float = 1.0):
    """Create a JSON plan for the task using the LLM and validate it against a schema.

    Retries the LLM prompt up to `max_retries` times if the output is not valid JSON or doesn't
    conform to the `PLAN_SCHEMA`.
    """

    # Enhanced prompt with better examples and clearer instructions
    prompt = f"""You are a planning agent. Your job is to analyze the user's task and create a step-by-step plan using the available tools.

AVAILABLE TOOLS:
- github_search(query, limit) - Search GitHub repositories. Use 'query' for search terms, 'limit' for number of results (default 3).
- weather(city) - Get current weather information for a city.

RESPONSE FORMAT:
You must respond with ONLY a JSON object. No explanations, no extra text, just JSON.

JSON Schema:
{json.dumps(PLAN_SCHEMA, indent=2)}

EXAMPLES:
Task: "Find python repositories and weather in London"
Response: {{"steps": [{{"tool": "github_search", "query": "python", "limit": 3}}, {{"tool": "weather", "city": "London"}}]}}

Task: "Get weather in New York"  
Response: {{"steps": [{{"tool": "weather", "city": "New York"}}]}}

Task: "Search for javascript repositories"
Response: {{"steps": [{{"tool": "github_search", "query": "javascript", "limit": 3}}]}}

INSTRUCTIONS:
1. Read the task carefully
2. Identify which tools are needed
3. Extract specific parameters (city names, search queries)
4. Generate the appropriate JSON response
5. Do NOT add any tools that aren't mentioned in the task
6. Use the exact tool names: "github_search" and "weather"

TASK TO PROCESS:
{task}

JSON RESPONSE:"""

    last_text = None
    for attempt in range(1, max_retries + 1):
        last_text = chat(prompt)

        # Try to parse JSON directly
        try:
            plan = json.loads(last_text)
        except Exception:
            # Fallback: try to extract first {...}
            start = last_text.find("{")
            end = last_text.rfind("}") + 1
            if start != -1 and end != -1:
                try:
                    plan = json.loads(last_text[start:end])
                except Exception:
                    plan = None
            else:
                plan = None

        if plan is None:
            if attempt < max_retries:
                time.sleep(retry_delay * attempt)
                continue
            else:
                raise ValueError(f"Planner failed to produce JSON plan. Last output:\n{last_text}")

        # Validate schema
        try:
            validate(instance=plan, schema=PLAN_SCHEMA)
            
            # Additional validation: check if the plan makes sense for the task
            if _is_plan_reasonable_for_task(task, plan):
                return plan
            else:
                if attempt < max_retries:
                    time.sleep(retry_delay * attempt)
                    continue
                else:
                    # Fallback to rule-based planning if LLM keeps failing
                    return _fallback_plan(task)
                    
        except ValidationError as e:
            if attempt < max_retries:
                time.sleep(retry_delay * attempt)
                continue
            else:
                # Fallback to rule-based planning if LLM keeps failing
                return _fallback_plan(task)


def _is_plan_reasonable_for_task(task: str, plan: dict) -> bool:
    """Check if the plan makes sense for the given task"""
    
    task_lower = task.lower()
    steps = plan.get("steps", [])
    
    # Check if weather is requested but not in plan, or vice versa
    weather_keywords = ["weather", "temperature", "climate", "forecast"]
    github_keywords = ["github", "repository", "repo", "search", "code", "programming"]
    
    task_requests_weather = any(keyword in task_lower for keyword in weather_keywords)
    task_requests_github = any(keyword in task_lower for keyword in github_keywords)
    
    plan_has_weather = any(step.get("tool") == "weather" for step in steps)
    plan_has_github = any(step.get("tool") == "github_search" for step in steps)
    
    # Extract specific entities from task
    cities = ["london", "new york", "tokyo", "mumbai", "berlin", "paris", "delhi", "prayagraj", "york"]
    languages = ["python", "javascript", "rust", "react", "go", "java", "typescript"]
    
    # Check for specific city mentions
    task_city = None
    for city in cities:
        if city in task_lower:
            task_city = city.title()
            break
    
    # Check for specific language mentions  
    task_language = None
    for lang in languages:
        if lang in task_lower:
            task_language = lang
            break
    
    # Validate weather steps
    if task_requests_weather and plan_has_weather:
        for step in steps:
            if step.get("tool") == "weather":
                plan_city = step.get("city", "").lower()
                if task_city and task_city.lower() != plan_city:
                    return False  # Wrong city
    
    # Validate github steps
    if task_requests_github and plan_has_github:
        for step in steps:
            if step.get("tool") == "github_search":
                plan_query = step.get("query", "").lower()
                if task_language and task_language != plan_query:
                    return False  # Wrong language
    
    # Basic logic check - if LLM gives generic response when specific task is given
    if task_city and task_city.lower() != "delhi" and plan_has_weather:
        for step in steps:
            if step.get("tool") == "weather" and step.get("city", "").lower() == "delhi":
                return False  # Generic Delhi response when specific city requested
    
    if task_language and task_language != "python" and plan_has_github:
        for step in steps:
            if step.get("tool") == "github_search" and step.get("query", "").lower() == "python":
                return False  # Generic python response when specific language requested
    
    return True


def _fallback_plan(task: str) -> dict:
    """Rule-based fallback planning when LLM fails"""
    
    task_lower = task.lower()
    steps = []
    
    # Check if task mentions weather
    weather_keywords = ["weather", "temperature", "climate", "forecast"]
    cities = ["london", "new york", "tokyo", "mumbai", "berlin", "paris", "delhi", "prayagraj", "new york", "york"]
    
    if any(keyword in task_lower for keyword in weather_keywords):
        # Find city in task
        city = None
        for city_name in cities:
            if city_name in task_lower:
                city = city_name.title()
                break
        
        if not city:
            city = "London"  # default
        
        steps.append({"tool": "weather", "city": city})
    
    # Check if task mentions GitHub/search
    github_keywords = ["github", "repository", "repo", "search", "code", "programming"]
    languages = ["python", "javascript", "rust", "react", "go", "java", "typescript"]
    
    if any(keyword in task_lower for keyword in github_keywords):
        # Find programming language in task
        query = None
        for lang in languages:
            if lang in task_lower:
                query = lang
                break
        
        if not query:
            query = "python"  # default
        
        steps.append({"tool": "github_search", "query": query, "limit": 3})
    
    return {"steps": steps}
