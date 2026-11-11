import os
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security_scheme = HTTPBearer()
EXPECTED_API_KEY = os.getenv("SERVICE_API_KEY", "default-dev-key")


def verify_tool_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
) -> str:
    expected = os.getenv("SERVICE_API_KEY", EXPECTED_API_KEY)
    if credentials.credentials != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação corporativo inválido para execução de ferramentas.",
        )
    return credentials.credentials
