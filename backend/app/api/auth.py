"""Single-account authentication endpoints."""

from datetime import timedelta
from secrets import compare_digest

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import session_dependency
from app.core.config import get_settings
from app.core.security import (
    hash_password,
    hash_session_token,
    new_session_token,
    verify_password,
)
from app.models.auth import AuthAccount, AuthSession
from app.schemas.auth import AccountRead, PasswordChange, SetupCredentials, Credentials
from app.db.base import utc_now

router = APIRouter(prefix="/auth", tags=["auth"])
SESSION_COOKIE = "checkin_session"


def auth_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"detail": "Invalid email or password", "code": "AUTHENTICATION_FAILED"},
        headers={"WWW-Authenticate": "Bearer"},
    )


def set_session_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=settings.auth_session_ttl_hours * 3600,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        path="/",
    )


async def create_session(
    account: AuthAccount, session: AsyncSession, response: Response
) -> None:
    token = new_session_token()
    session.add(
        AuthSession(
            account_id=account.id,
            token_hash=hash_session_token(token),
            expires_at=utc_now()
            + timedelta(hours=get_settings().auth_session_ttl_hours),
        )
    )
    await session.commit()
    set_session_cookie(response, token)


async def current_account(
    request: Request, session: AsyncSession = Depends(session_dependency)
) -> AuthAccount:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise auth_error()
    result = await session.execute(
        select(AuthAccount)
        .join(AuthSession, AuthSession.account_id == AuthAccount.id)
        .where(
            AuthSession.token_hash == hash_session_token(token),
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > utc_now(),
        )
    )
    account = result.scalar_one_or_none()
    if account is None:
        raise auth_error()
    return account


@router.post("/setup", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def setup_account(
    data: SetupCredentials,
    response: Response,
    x_setup_token: str | None = Header(default=None),
    session: AsyncSession = Depends(session_dependency),
) -> AuthAccount:
    """Create the only account once, using an out-of-band setup secret."""
    settings = get_settings()
    if (
        not settings.auth_setup_token
        or not x_setup_token
        or not compare_digest(x_setup_token, settings.auth_setup_token)
    ):
        raise HTTPException(
            status_code=404, detail={"detail": "Not found", "code": "NOT_FOUND"}
        )
    count = await session.scalar(select(func.count()).select_from(AuthAccount))
    if count:
        raise HTTPException(
            status_code=409,
            detail={"detail": "Account already exists", "code": "ACCOUNT_EXISTS"},
        )
    account = AuthAccount(email=data.email, password_hash=hash_password(data.password))
    session.add(account)
    await session.flush()
    await create_session(account, session, response)
    return account


@router.post("/login", response_model=AccountRead)
async def login(
    data: Credentials,
    response: Response,
    session: AsyncSession = Depends(session_dependency),
) -> AuthAccount:
    account = await session.scalar(
        select(AuthAccount).where(AuthAccount.email == data.email)
    )
    if account is None or not verify_password(data.password, account.password_hash):
        raise auth_error()
    await create_session(account, session, response)
    return account


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(session_dependency),
) -> Response:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        await session.execute(
            update(AuthSession)
            .where(
                AuthSession.token_hash == hash_session_token(token),
                AuthSession.revoked_at.is_(None),
            )
            .values(revoked_at=utc_now())
        )
        await session.commit()
    response.delete_cookie(SESSION_COOKIE, path="/")
    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=response.headers)


@router.get("/me", response_model=AccountRead)
async def me(account: AuthAccount = Depends(current_account)) -> AuthAccount:
    return account


@router.post("/password", response_model=AccountRead)
async def change_password(
    data: PasswordChange,
    response: Response,
    account: AuthAccount = Depends(current_account),
    session: AsyncSession = Depends(session_dependency),
) -> AuthAccount:
    if not verify_password(data.current_password, account.password_hash):
        raise HTTPException(
            status_code=400,
            detail={
                "detail": "Current password is incorrect",
                "code": "INVALID_PASSWORD",
            },
        )
    account.password_hash = hash_password(data.new_password)
    account.updated_at = utc_now()
    await session.execute(
        update(AuthSession)
        .where(AuthSession.account_id == account.id, AuthSession.revoked_at.is_(None))
        .values(revoked_at=utc_now())
    )
    await session.flush()
    await create_session(account, session, response)
    return account
