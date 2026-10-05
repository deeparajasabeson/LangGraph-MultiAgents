from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agents import LangGraphSupportAgent, LangGraphSalesAgent, LangGraphCoordinator


class AgentQueryRequest(BaseModel):
    question: str = Field(..., description="Customer query to route through the coordinator.")

class AgentQueryResponse(BaseModel):
    response: str

class DeploymentInfoResponse(BaseModel):
    foundry_project_endpoint: str
    model_deployment: str

class CleanupResponse(BaseModel):
    status: str
    detail: str


async def _create_coordinator() -> LangGraphCoordinator:
    # Initialize and return the coordinator agent
    support_agent = LangGraphSupportAgent("support")
    sales_agent = LangGraphSalesAgent("sales")
    coordinator = LangGraphCoordinator(
        agents=[support_agent, sales_agent]
    )

    await coordinator.initialize()
    await sales_agent.initialize()
    await support_agent.initialize()
    return coordinator


@asynccontextmanager
async def lifespan(_: FastAPI):
    app.state.coordinator = await _create_coordinator()
    yield

app = FastAPI(
    title="LangGraph Multi-Agent API",
    description="FastAPI service for coordinator-based routing with LangGraph agents.",
    version="1.0.0",
    docs_url="/swagger",
    lifespan=lifespan
)

@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}


@app.post("/agent/query", response_model=AgentQueryResponse)
async def route_agent_query(request: AgentQueryRequest) -> AgentQueryResponse:
    coordinator = getattr(app.state, "coordinator", None)
    if coordinator is None:
        try:
            coordinator = await _create_coordinator()
            app.state.coordinator = coordinator
        except Exception as ex:
            raise HTTPException(status_code=500, detail=f"Failed to initialize coordinator agent: {str(ex)}")

    try: 
        response = await coordinator.route_query(request.question)        
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Agent query failed: {ex}") from ex

    return AgentQueryResponse(response=response)


@app.post("/agent/cleanup", response_model=CleanupResponse)
async def cleanup_agents() -> CleanupResponse:
    app.state.coordinator = None

    return CleanupResponse(
        status="success",
        detail="Coordinator reset successfully. Agents will be reinitialized on the next query."
    )
