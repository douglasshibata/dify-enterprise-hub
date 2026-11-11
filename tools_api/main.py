"""Enterprise ERP & HR Custom Tools API for Dify.

This FastAPI service exposes business logic (vacation balances, payroll queries,
and reimbursement approval workflows) through OpenAPI/Swagger specifications
compatible with Dify's visual 'Custom Tools' interface.
"""

from __future__ import annotations

import os
from typing import Optional, List
from enum import Enum
from fastapi import FastAPI, HTTPException, Security, status, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field

API_KEY_NAME = "X-Tool-Api-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

EXPECTED_API_KEY = os.getenv("API_KEY", "erp-enterprise-secure-token-2025")

app = FastAPI(
    title="Enterprise ERP & HR Assistant Tools",
    description="Custom Business Logic API integrated into Dify Canvas for automated HR & Finance operations.",
    version="1.0.0",
    servers=[
        {"url": "http://localhost:8080", "description": "Local Direct Port"},
        {"url": "http://dify-tools-api:8080", "description": "Internal Docker Network"},
        {"url": "/tools", "description": "Reverse Proxy Ingress"},
    ],
)


def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """Validate incoming API Key from Dify custom tool invocation."""
    if not api_key or api_key != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Tool-Api-Key header",
        )
    return api_key


# -----------------------------------------------------------------------------
# Data Models
# -----------------------------------------------------------------------------

class EmployeeVacationRequest(BaseModel):
    employee_id: str = Field(
        ...,
        description="ID ou matrícula do colaborador no formato EMP-XXXXX",
        json_schema_extra={"example": "EMP-10492"},
    )
    year: Optional[int] = Field(
        default=2025,
        description="Ano de referência para consulta de férias",
        json_schema_extra={"example": 2025},
    )


class EmployeeVacationResponse(BaseModel):
    employee_id: str
    employee_name: str
    department: str
    total_accrued_days: int
    days_taken: int
    remaining_balance_days: int
    eligible_for_cash_allowance: bool
    status_summary: str


class ReimbursementStatus(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    PAID = "PAID"
    REJECTED = "REJECTED"


class ReimbursementQueryRequest(BaseModel):
    reimbursement_ticket_id: str = Field(
        ...,
        description="Identificador do ticket de reembolso",
        json_schema_extra={"example": "REIMB-2025-9981"},
    )


class ReimbursementResponse(BaseModel):
    ticket_id: str
    employee_id: str
    category: str
    amount: float
    currency: str
    submission_date: str
    status: ReimbursementStatus
    approval_notes: str


class SubmitReimbursementRequest(BaseModel):
    employee_id: str = Field(
        ...,
        description="Matrícula do solicitante",
        json_schema_extra={"example": "EMP-10492"},
    )
    category: str = Field(
        ...,
        description="Categoria da despesa (ex: Alimentação, Transporte, Hospedagem, Certificação)",
        json_schema_extra={"example": "Transporte"},
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Valor monetário do recibo",
        json_schema_extra={"example": 154.50},
    )
    currency: str = Field(
        default="BRL",
        description="Moeda (ex: BRL, USD, EUR)",
        json_schema_extra={"example": "BRL"},
    )
    description: str = Field(
        ...,
        description="Justificativa da despesa corporativa",
        json_schema_extra={"example": "Uber para visita técnica a cliente corporativo"},
    )


class SubmitReimbursementResponse(BaseModel):
    ticket_id: str
    status: ReimbursementStatus
    estimated_payout_days: int
    message: str


# -----------------------------------------------------------------------------
# In-Memory Mock Corporate Database
# -----------------------------------------------------------------------------

MOCK_EMPLOYEES = {
    "EMP-10492": {
        "name": "Mariana Souza",
        "department": "Marketing",
        "total_days": 30,
        "days_taken": 10,
        "eligible_cash": True,
    },
    "EMP-20831": {
        "name": "Carlos Eduardo",
        "department": "Recursos Humanos",
        "total_days": 30,
        "days_taken": 25,
        "eligible_cash": False,
    },
    "EMP-30499": {
        "name": "Juliana Martins",
        "department": "Finanças",
        "total_days": 30,
        "days_taken": 0,
        "eligible_cash": True,
    },
}

MOCK_REIMBURSEMENTS = {
    "REIMB-2025-9981": {
        "employee_id": "EMP-10492",
        "category": "Alimentação",
        "amount": 89.90,
        "currency": "BRL",
        "submission_date": "2025-05-10",
        "status": ReimbursementStatus.APPROVED,
        "notes": "Aprovado pelo gestor imediato. Pagamento agendado para o próximo ciclo de folha.",
    },
    "REIMB-2025-7712": {
        "employee_id": "EMP-30499",
        "category": "Certificação",
        "amount": 1250.00,
        "currency": "BRL",
        "submission_date": "2025-05-12",
        "status": ReimbursementStatus.PENDING_APPROVAL,
        "notes": "Em análise pela gerência de departamento.",
    },
}


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@app.get("/healthz", tags=["System"])
def health_check():
    """Health check endpoint to probe container readiness."""
    return {"status": "ok", "service": "dify-enterprise-tools-api"}


@app.post(
    "/api/v1/hr/vacation-balance",
    response_model=EmployeeVacationResponse,
    summary="Consultar saldo de férias de colaborador",
    description="Permite que o assistente de IA consulte o saldo de férias e elegibilidade a abono pecuniário no ERP de RH.",
    tags=["RH & Pessoas"],
)
def get_vacation_balance(
    payload: EmployeeVacationRequest,
    _: str = Depends(verify_api_key),
):
    emp = MOCK_EMPLOYEES.get(payload.employee_id)
    if not emp:
        # Fallback determinístico para fins de demonstração
        return EmployeeVacationResponse(
            employee_id=payload.employee_id,
            employee_name="Colaborador Demonstrativo",
            department="Operações",
            total_accrued_days=30,
            days_taken=12,
            remaining_balance_days=18,
            eligible_for_cash_allowance=True,
            status_summary="Colaborador possui 18 dias úteis disponíveis para agendamento no exercício fiscal.",
        )

    remaining = emp["total_days"] - emp["days_taken"]
    return EmployeeVacationResponse(
        employee_id=payload.employee_id,
        employee_name=emp["name"],
        department=emp["department"],
        total_accrued_days=emp["total_days"],
        days_taken=emp["days_taken"],
        remaining_balance_days=remaining,
        eligible_for_cash_allowance=emp["eligible_cash"],
        status_summary=f"Colaborador {emp['name']} ({emp['department']}) possui {remaining} dias de férias restantes para usufruto.",
    )


@app.post(
    "/api/v1/finance/reimbursement-status",
    response_model=ReimbursementResponse,
    summary="Consultar status de ticket de reembolso",
    description="Permite verificar se uma nota fiscal ou solicitação de reembolso foi aprovada pelo financeiro.",
    tags=["Finanças & Controladoria"],
)
def get_reimbursement_status(
    payload: ReimbursementQueryRequest,
    _: str = Depends(verify_api_key),
):
    reimb = MOCK_REIMBURSEMENTS.get(payload.reimbursement_ticket_id)
    if not reimb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket de reembolso '{payload.reimbursement_ticket_id}' não encontrado no sistema ERP.",
        )

    return ReimbursementResponse(
        ticket_id=payload.reimbursement_ticket_id,
        employee_id=reimb["employee_id"],
        category=reimb["category"],
        amount=reimb["amount"],
        currency=reimb["currency"],
        submission_date=reimb["submission_date"],
        status=reimb["status"],
        approval_notes=reimb["notes"],
    )


@app.post(
    "/api/v1/finance/submit-reimbursement",
    response_model=SubmitReimbursementResponse,
    summary="Submeter nova solicitação de reembolso",
    description="Registra uma nova despesa corporativa enviada pelo colaborador via chat de IA.",
    tags=["Finanças & Controladoria"],
)
def submit_reimbursement(
    payload: SubmitReimbursementRequest,
    _: str = Depends(verify_api_key),
):
    import random

    ticket_id = f"REIMB-2025-{random.randint(1000, 9999)}"
    MOCK_REIMBURSEMENTS[ticket_id] = {
        "employee_id": payload.employee_id,
        "category": payload.category,
        "amount": payload.amount,
        "currency": payload.currency,
        "submission_date": "2025-05-15",
        "status": ReimbursementStatus.PENDING_APPROVAL,
        "notes": f"Solicitação criada automaticamente via Dify AI Assistant: {payload.description}",
    }

    return SubmitReimbursementResponse(
        ticket_id=ticket_id,
        status=ReimbursementStatus.PENDING_APPROVAL,
        estimated_payout_days=5,
        message=f"Solicitação registrada com sucesso sob o protocolo {ticket_id}. O comprovante foi encaminhado para aprovação.",
    )
