from fastapi import FastAPI, Depends
from app.core.security import verify_tool_api_key
from app.routers.hr import (
    router as hr_router,
    VacationQueryRequest,
    VacationQueryResponse,
    get_vacation_balance,
)
from app.routers.finance import (
    router as finance_router,
    ReimbursementSubmitRequest,
    ReimbursementSubmitResponse,
    submit_reimbursement,
)

app = FastAPI(
    title="Enterprise AI Tools Gateway",
    description="Barramento OpenAPI para integração dos Agentes do Dify aos sistemas corporativos.",
    version="1.0.0",
    servers=[{"url": "/tools", "description": "Nginx Ingress Proxy"}],
)

# Include subrouters
app.include_router(hr_router)
app.include_router(finance_router)


@app.get("/healthz", tags=["System"])
def health_check():
    """Health check endpoint to probe container readiness."""
    return {"status": "ok", "service": "enterprise-tools-api"}
