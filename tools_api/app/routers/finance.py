from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.core.security import verify_tool_api_key

router = APIRouter(
    prefix="/api/v1/finance",
    tags=["Finanças & Controladoria"],
    dependencies=[Depends(verify_tool_api_key)],
)


class ReimbursementSubmitRequest(BaseModel):
    employee_id: str = Field(
        ...,
        pattern=r"^EMP-[0-9]{4,6}$",
        description="Matrícula do colaborador no padrão EMP-XXXX",
        json_schema_extra={"example": "EMP-10492"},
    )
    expense_category: str = Field(
        ...,
        description="Ex: ALIMENTACAO, TRANSPORTE, HOSPEDAGEM",
        json_schema_extra={"example": "TRANSPORTE"},
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Valor total da nota fiscal",
        json_schema_extra={"example": 150.0},
    )
    invoice_number: str = Field(
        ...,
        description="Número da nota fiscal ou recibo",
        json_schema_extra={"example": "NF-99882"},
    )


class ReimbursementSubmitResponse(BaseModel):
    protocol_id: str
    status: str
    sla_hours: int


@router.post(
    "/submit-reimbursement",
    response_model=ReimbursementSubmitResponse,
    summary="Registra solicitação de reembolso de despesa",
)
def submit_reimbursement(payload: ReimbursementSubmitRequest):
    """Encaminha notas fiscais de despesas corporativas para a esteira de aprovação do Financeiro."""
    return ReimbursementSubmitResponse(
        protocol_id=f"REIMB-{payload.employee_id[-4:]}-8821",
        status="UNDER_AUDIT",
        sla_hours=48,
    )
