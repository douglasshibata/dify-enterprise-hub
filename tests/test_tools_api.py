import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import EXPECTED_API_KEY

client = TestClient(app)


def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "enterprise-tools-api"


def test_vacation_balance_unauthorized():
    response = client.post(
        "/api/v1/hr/vacation-balance",
        json={"employee_id": "EMP-10492"},
    )
    assert response.status_code == 403 or response.status_code == 401


def test_vacation_balance_invalid_token():
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.post(
        "/api/v1/hr/vacation-balance",
        headers=headers,
        json={"employee_id": "EMP-10492"},
    )
    assert response.status_code == 401
    assert "Token de autenticação corporativo inválido" in response.json()["detail"]


def test_vacation_balance_authorized_known_employee():
    headers = {"Authorization": f"Bearer {EXPECTED_API_KEY}"}
    response = client.post(
        "/api/v1/hr/vacation-balance",
        headers=headers,
        json={"employee_id": "EMP-10492"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == "EMP-10492"
    assert data["employee_name"] == "Carlos Silva de Oliveira"
    assert data["accrued_days"] == 22
    assert data["next_expiry_date"] == "2027-04-30"
    assert data["can_schedule"] is True


def test_vacation_balance_invalid_id_format():
    headers = {"Authorization": f"Bearer {EXPECTED_API_KEY}"}
    response = client.post(
        "/api/v1/hr/vacation-balance",
        headers=headers,
        json={"employee_id": "INVALID-FORMAT"},
    )
    assert response.status_code == 422


def test_vacation_balance_fallback():
    headers = {"Authorization": f"Bearer {EXPECTED_API_KEY}"}
    response = client.post(
        "/api/v1/hr/vacation-balance",
        headers=headers,
        json={"employee_id": "EMP-9999"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["employee_id"] == "EMP-9999"
    assert data["can_schedule"] is True


def test_submit_reimbursement_authorized():
    headers = {"Authorization": f"Bearer {EXPECTED_API_KEY}"}
    response = client.post(
        "/api/v1/finance/submit-reimbursement",
        headers=headers,
        json={
            "employee_id": "EMP-10492",
            "expense_category": "TRANSPORTE",
            "amount": 185.50,
            "invoice_number": "NF-10492-01",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["protocol_id"] == "REIMB-0492-8821"
    assert data["status"] == "UNDER_AUDIT"
    assert data["sla_hours"] == 48


def test_submit_reimbursement_invalid_amount():
    headers = {"Authorization": f"Bearer {EXPECTED_API_KEY}"}
    response = client.post(
        "/api/v1/finance/submit-reimbursement",
        headers=headers,
        json={
            "employee_id": "EMP-10492",
            "expense_category": "TRANSPORTE",
            "amount": -50.0,
            "invoice_number": "NF-10492-01",
        },
    )
    assert response.status_code == 422
