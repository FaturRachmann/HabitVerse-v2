# app/routes/auth.py
from fastapi import APIRouter, Depends, Request, Form, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.db.models import User
from app.config import settings
from datetime import timedelta

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    """Login page (inline HTML while templates are incomplete)"""
    html = """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Login - HabitVerse</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
          html,body{font-family:'Inter',system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
          .glass{background:rgba(255,255,255,.7);backdrop-filter:blur(14px);border:1px solid rgba(255,255,255,.6)}
          .btn-primary{background-image:linear-gradient(135deg,#6366F1,#A855F7);color:#fff}
          .btn-primary:hover{filter:brightness(1.05)}
        </style>
      </head>
      <body class="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center px-4">
        <div class="max-w-md w-full">
          <div class="text-center mb-6">
            <a href="/" class="inline-flex items-center gap-2">
              <span class="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-indigo-600 text-white font-semibold">H</span>
              <span class="text-2xl font-semibold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-fuchsia-600">HabitVerse</span>
            </a>
            <p class="mt-2 text-slate-600">Masuk untuk melanjutkan progresmu</p>
          </div>
          <div class="glass rounded-2xl shadow-xl p-6">
            <form method="post" action="/auth/login" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-slate-700">Email</label>
                <input type="email" name="email" required class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white/80" placeholder="you@example.com">
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700">Password</label>
                <input type="password" name="password" required class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white/80" placeholder="••••••••">
              </div>
              <button type="submit" class="w-full px-4 py-2 rounded-lg btn-primary shadow">Login</button>
            </form>
            <p class="mt-4 text-center text-sm text-slate-600">Belum punya akun? <a class="text-indigo-600 hover:underline" href="/auth/register">Register</a></p>
          </div>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.post("/login")
async def login_submit(
    response: Response,
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle login form submission"""
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        error_html = f"""
        <!doctype html><html><head><meta charset="utf-8"><script src="https://cdn.tailwindcss.com"></script></head>
        <body class="min-h-screen flex items-center justify-center bg-rose-50">
          <div class="max-w-md w-full bg-white rounded-xl border border-rose-200 p-6 text-center">
            <h1 class="text-xl font-semibold text-slate-900">Login</h1>
            <p class="mt-2 text-rose-600">Invalid email or password</p>
            <a class="mt-4 inline-block text-indigo-600 hover:underline" href="/auth/login">Back to login</a>
          </div>
        </body></html>
        """
        return HTMLResponse(content=error_html, status_code=400)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Set cookie and redirect
    redirect = RedirectResponse(url="/dashboard", status_code=302)
    redirect.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )

    return redirect


@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    """Registration page (inline HTML while templates are incomplete)"""
    html = """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Register - HabitVerse</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
          html,body{font-family:'Inter',system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
          .glass{background:rgba(255,255,255,.7);backdrop-filter:blur(14px);border:1px solid rgba(255,255,255,.6)}
          .btn-primary{background-image:linear-gradient(135deg,#6366F1,#A855F7);color:#fff}
          .btn-primary:hover{filter:brightness(1.05)}
        </style>
      </head>
      <body class="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 flex items-center justify-center px-4">
        <div class="max-w-md w-full">
          <div class="text-center mb-6">
            <a href="/" class="inline-flex items-center gap-2">
              <span class="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-indigo-600 text-white font-semibold">H</span>
              <span class="text-2xl font-semibold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-fuchsia-600">HabitVerse</span>
            </a>
            <p class="mt-2 text-slate-600">Buat akun baru untuk mulai membangun kebiasaan</p>
          </div>
          <div class="glass rounded-2xl shadow-xl p-6">
            <form method="post" action="/auth/register" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-slate-700">Name</label>
                <input type="text" name="name" required class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white/80" placeholder="Nama lengkap">
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700">Email</label>
                <input type="email" name="email" required class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white/80" placeholder="you@example.com">
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700">Password</label>
                <input type="password" name="password" required class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white/80" placeholder="Minimal 8 karakter">
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700">Confirm Password</label>
                <input type="password" name="confirm_password" required class="mt-1 w-full px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white/80" placeholder="Ulangi password">
              </div>
              <button type="submit" class="w-full px-4 py-2 rounded-lg btn-primary shadow">Create Account</button>
            </form>
            <p class="mt-4 text-center text-sm text-slate-600">Sudah punya akun? <a class="text-indigo-600 hover:underline" href="/auth/login">Login</a></p>
          </div>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.post("/register")
async def register_submit(
    response: Response,
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle registration form submission"""
    # Validation
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if password != confirm_password:
        errors.append("Passwords do not match")

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        errors.append("Email already registered")

    if errors:
        error_html = (
            """
            <!doctype html><html><head><meta charset='utf-8'><script src='https://cdn.tailwindcss.com'></script></head>
            <body class='min-h-screen flex items-center justify-center bg-amber-50'>
              <div class='max-w-md w-full bg-white rounded-xl border border-amber-200 p-6'>
                <h1 class='text-xl font-semibold text-slate-900'>Register</h1>
            """
            + "".join(f"<p class='mt-2 text-amber-700'>• {e}</p>" for e in errors) +
            """
                <a href='/auth/register' class='mt-4 inline-block text-indigo-600 hover:underline'>Back to register</a>
              </div>
            </body></html>
            """
        )
        return HTMLResponse(content=error_html, status_code=400)

    # Create user
    hashed_password = get_password_hash(password)
    user = User(
        name=name,
        email=email,
        password_hash=hashed_password
    )

    db.add(user)
    db.commit()

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Set cookie and redirect
    redirect = RedirectResponse(url="/dashboard", status_code=302)
    redirect.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )

    return redirect


@router.get("/logout")
async def logout():
    """Logout and redirect"""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="access_token")
    return response