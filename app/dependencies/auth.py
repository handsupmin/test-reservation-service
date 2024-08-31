from fastapi import Request, HTTPException


def get_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="토큰이 없거나 유효하지 않습니다.")

    token = auth_header.split("Bearer ")[1]

    if not isinstance(token, str):
        raise ValueError("유효하지 않은 토큰입니다.")

    return token
