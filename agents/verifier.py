import json
from llm.client import chat
from agents.executor import ExecutorAgent


def verify(plan, results):
    """Use the LLM to analyze plan & results, and attempt to repair missing steps by re-running them."""

    analysis_prompt = f"""
You are a verifier agent. Given the plan:
{json.dumps(plan, indent=2)}
and the current results:
{json.dumps(results, indent=2)}

Return ONLY a JSON object with keys:
- status: "ok" or "partial"
- missing_tools: array of tool names that are missing
- notes: short human-readable explanation
"""

    text = chat(analysis_prompt)

    # Try to parse JSON from LLM response
    try:
        analysis = json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end != -1:
            try:
                analysis = json.loads(text[start:end])
            except Exception:
                analysis = {"status": "partial", "missing_tools": [], "notes": "Verifier failed to return valid JSON"}
        else:
            analysis = {"status": "partial", "missing_tools": [], "notes": "Verifier failed to return valid JSON"}

    missing = analysis.get("missing_tools", [])

    # If missing steps reported, attempt to re-run them
    if missing:
        # Check which tools are actually missing from results
        existing_tools = {r.get("tool") for r in results if "result" in r}
        actually_missing = [tool for tool in missing if tool not in existing_tools]
        
        if actually_missing:
            missing_steps = [s for s in plan.get("steps", []) if s.get("tool") in actually_missing]
            if missing_steps:
                executor = ExecutorAgent()
                repaired = executor.execute({"steps": missing_steps})
                # append repaired results
                results.extend(repaired)
                # re-run analysis after repair
                final_prompt = f"""
After re-running missing steps, the plan is:
{json.dumps(plan, indent=2)}
Results are now:
{json.dumps(results, indent=2)}

Return a final JSON with keys: status, missing_tools (should be empty if repaired), notes.
"""
                text2 = chat(final_prompt)
                try:
                    analysis2 = json.loads(text2)
                except Exception:
                    start = text2.find("{")
                    end = text2.rfind("}") + 1
                    if start != -1 and end != -1:
                        try:
                            analysis2 = json.loads(text2[start:end])
                        except Exception:
                            analysis2 = {"status": "partial", "missing_tools": [], "notes": "Verifier failed to return valid JSON on second pass"}
                    else:
                        analysis2 = {"status": "partial", "missing_tools": [], "notes": "Verifier failed to return valid JSON on second pass"}

            return {
                "status": analysis2.get("status", "partial"),
                "missing_tools": analysis2.get("missing_tools", []),
                "notes": analysis2.get("notes", "")
            }

    return {
        "status": analysis.get("status", "partial"),
        "missing_tools": missing,
        "notes": analysis.get("notes", "")
    }
