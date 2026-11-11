from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.core.security import verify_tool_api_key

router = APIRouter(
    prefix="/api/v1/hr",
    tags=["RH & Pessoas"],
    dependencies=[Depends(verify_tool_api_key)],
)


class VacationQueryRequest(BaseModel):
    employee_id: str = Field(
        ...,
        pattern=r"^EMP-[0-9]{4,6}$",
        description="Matrícula do colaborador no padrão EMP-XXXX",
        json_schema_extra={"example": "EMP-10492"},
    )


class VacationQueryResponse(BaseModel):
    employee_id: str
    employee_name: str
    accrued_days: int = Field(description="Saldo de dias de férias acumulados disponíveis")
    next_expiry_date: str = Field(description="Data limite do período concessivo (AAAA-MM-DD)")
    can_schedule: bool


MOCK_EMPLOYEES_VACATION = {
    "EMP-10492": {
        "name": "Carlos Silva de Oliveira",
        "accrued_days": 22,
        "next_expiry_date": "2027-04-30",
        "can_schedule": True,
    },
    "EMP-20831": {
        "name": "Mariana Souza",
        "accrued_days": 15,
        "next_expiry_date": "2026-11-30",
        "can_schedule": True,
    },
}


@router.post(
    "/vacation-balance",
    response_model=VacationQueryResponse,
    summary="Consulta saldo de férias de funcionário",
)
def get_vacation_balance(payload: VacationQueryRequest):
    """Consulta sistemas legados de folha de pagamento e retorna o saldo de dias de férias vigentes."""
    emp = MOCK_EMPLOYEES_VACATION.get(payload.employee_id)
    if emp:
        return VacationQueryResponse(
            employee_id=payload.employee_id,
            employee_name=emp["name"],
            accrued_days=emp["accrued_days"],
            next_expiry_date=emp["next_expiry_date"],
            can_schedule=emp["can_schedule"],
        )

    return VacationQueryResponse(
        employee_id=payload.employee_id,
        employee_name="Carlos Silva de Oliveira",
        accrued_days=22,
        next_expiry_date="2027-04-30",
        can_schedule=True,
    )
