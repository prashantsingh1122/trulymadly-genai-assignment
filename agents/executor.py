from tools.github_tool import search_repositories
from tools.weather_tool import get_weather


class ExecutorAgent:

    def execute(self, plan: dict):
        results = []

        for step in plan.get("steps", []):

            tool = step.get("tool")

            try:
                if tool == "github_search":
                    query = step.get("query")
                    limit = step.get("limit", 3)

                    data = search_repositories(query, limit)

                    results.append({
                        "tool": "github_search",
                        "result": data
                    })

                elif tool == "weather":
                    city = step.get("city")

                    data = get_weather(city)

                    results.append({
                        "tool": "weather",
                        "result": data
                    })

                else:
                    results.append({
                        "tool": tool,
                        "error": "Unknown tool"
                    })

            except Exception as e:
                results.append({
                    "tool": tool,
                    "error": str(e)
                })

        return results
