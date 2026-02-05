from fastapi import FastAPI, Query, Body
from pydantic import BaseModel  
from typing import Optional
from agents.planner import create_plan
from agents.executor import ExecutorAgent
from agents.verifier import verify

app = FastAPI()

class TaskRequest(BaseModel):
    task: str

@app.post('/run')
def run(request: Optional[TaskRequest] = Body(None), task: Optional[str] = Query(None)):
    if request:
        task_to_use = request.task
    elif task:
        task_to_use = task
    else:
        return {'error': 'Task is required'}
    
    plan = create_plan(task_to_use)
    executor = ExecutorAgent()
    results = executor.execute(plan)
    verified = verify(plan, results)
    
    # Clean, concise response
    return {
        'task': task_to_use,
        'plan': plan,
        'results': results,
        'status': verified.get('status', 'unknown')
    }
