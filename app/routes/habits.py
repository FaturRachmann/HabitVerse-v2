# app/routes/habits.py
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.db.models import User, Habit, HabitCategory, HabitFrequency

router = APIRouter()


def page_shell(title: str, body: str) -> str:
    return f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>{title} • HabitVerse</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
      <style>
        html,body{{font-family:'Inter',system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif}}
        @keyframes floaty{{0%{{transform:translateY(0) rotate(0deg)}}50%{{transform:translateY(-12px) rotate(3deg)}}100%{{transform:translateY(0) rotate(0deg)}}}}
        .aurora{{filter: blur(60px); opacity:.55; animation: floaty 12s ease-in-out infinite}}
        .glass{{background:rgba(255,255,255,.3); backdrop-filter:blur(18px); border:1px solid rgba(255,255,255,.25); box-shadow:0 8px 30px rgba(31,38,135,.15)}}
        .btn-primary{{background-image:linear-gradient(135deg,#6366F1,#A855F7); color:#fff}}
        .btn-primary:hover{{filter:brightness(1.05)}}
      </style>
    </head>
    <body class="relative bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 text-slate-800">
      <!-- Animated aurora background -->
      <div aria-hidden="true" class="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div class="aurora absolute -top-20 -left-20 w-[380px] h-[380px] bg-gradient-to-br from-indigo-300 to-purple-300 rounded-full"></div>
        <div class="aurora absolute bottom-0 right-[-60px] w-[420px] h-[420px] bg-gradient-to-br from-pink-300 to-rose-300 rounded-full" style="animation-delay: -6s"></div>
      </div>
      <header class="bg-white/10 backdrop-blur-md border-b border-white/20 text-slate-900">
        <div class="max-w-5xl mx-auto px-4 py-6 flex items-center justify-between">
          <a href="/dashboard" class="text-xl font-semibold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-fuchsia-600">HabitVerse</a>
          <nav class="hidden sm:flex space-x-4 text-sm">
            <a class="hover:underline/50" href="/dashboard">Dashboard</a>
            <a class="hover:underline/50" href="/habits">Habits</a>
            <a class="hover:underline/50" href="/community">Community</a>
            <a class="hover:underline/50" href="/friends">Friends</a>
            <a class="hover:underline/50" href="/profile">Profile</a>
            <a class="hover:underline/50" href="/coach">AI Coach</a>
          </nav>
        </div>
      </header>
      <main class="max-w-5xl mx-auto px-4 py-6 sm:py-8 pb-24">{body}</main>
      <!-- Mobile bottom nav -->
      <nav class="sm:hidden fixed bottom-0 inset-x-0 bg-white/80 backdrop-blur-md border-t border-slate-200/60 shadow-lg">
        <div class="max-w-5xl mx-auto grid grid-cols-5">
          <a href="/dashboard" class="flex flex-col items-center justify-center py-3 text-[11px] text-slate-700 hover:bg-white/60">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0h6"/></svg>
            Home
          </a>
          <a href="/habits" class="flex flex-col items-center justify-center py-3 text-[11px] text-slate-700 hover:bg-white/60">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8c-1.657 0-3 1.343-3 3v7m6-10a3 3 0 00-3-3m0 0a3 3 0 013 3m-3-3v0"/></svg>
            Habits
          </a>
          <a href="/community" class="flex flex-col items-center justify-center py-3 text-[11px] text-slate-700 hover:bg-white/60">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5V4H2v16h5m10 0V10M7 20v-6"/></svg>
            Community
          </a>
          <a href="/coach" class="flex flex-col items-center justify-center py-3 text-[11px] text-slate-700 hover:bg-white/60">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 18l-3.5 2 1-3.9L6 12.5l4-.3L12 8l2 4.2 4 .3-3.5 3.6 1 3.9z"/></svg>
            Coach
          </a>
          <a href="/profile" class="flex flex-col items-center justify-center py-3 text-[11px] text-slate-700 hover:bg-white/60">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5.121 17.804A7 7 0 0112 15a7 7 0 016.879 2.804M15 10a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
            Profile
          </a>
        </div>
      </nav>
      <footer class="py-8 text-center text-sm text-slate-500">Made with intent • Keep the streak alive ✨</footer>
    </body>
    </html>
    """


@router.get("/debug", response_class=HTMLResponse)
async def habits_debug(request: Request):
    """Debug route without authentication"""
    return HTMLResponse(content="<h1>Habits Debug Route Works</h1><p>Authentication is the issue</p>")


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
async def habits_list(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Habits list page (Tailwind styled)"""
    try:
        print(f"DEBUG: habits_list called for user {current_user.id}")
        habits = db.query(Habit).filter(
            Habit.user_id == current_user.id,
            Habit.is_active == True
        ).order_by(Habit.created_at.desc()).all()
        print(f"DEBUG: Found {len(habits)} habits")

        if habits:
            items = "".join(
                f"""
                <li class="p-4 rounded-2xl glass hover:shadow-xl transition"> 
                  <div class="flex items-start justify-between"> 
                    <div> 
                      <div class="flex items-center gap-2"> 
                        <span class="inline-block w-2.5 h-2.5 rounded-full" style="background:{h.color or '#6366F1'}"></span> 
                        <a href="/habits/{h.id}" class="font-semibold text-slate-900 hover:text-indigo-600">{h.name}</a> 
                      </div> 
                      <p class="mt-1 text-sm text-slate-700">{(h.description or '').strip()[:120]}{'…' if (h.description or '') and len((h.description or ''))>120 else ''}</p> 
                      <div class="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-600"> 
                        <span class="px-2 py-0.5 rounded-full bg-white/60 border border-white/40">{h.category}</span> 
                        <span class="px-2 py-0.5 rounded-full bg-white/60 border border-white/40">{h.frequency}</span> 
                        <span class="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700">streak {h.current_streak}</span> 
                      </div> 
                    </div> 
                  </div> 
                </li> 
                """ for h in habits
            )
        else:
            items = """
            <li class="p-8 rounded-2xl glass text-center text-slate-500">
              Belum ada habit. Mulai dengan membuat satu! ✨
            </li>
            """

        body = f"""
          <div class="flex items-center justify-between mb-6">
            <div>
              <h1 class="text-2xl font-semibold">Halo, {current_user.name}</h1>
              <p class="text-slate-700">Kelola kebiasaan dan pertahankan streakmu.</p>
            </div>
            <a href="/habits/create" class="inline-flex items-center gap-2 px-4 py-2 rounded-lg btn-primary shadow-sm"> 
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path d="M10 3a1 1 0 011 1v5h5a1 1 0 010 2h-5v5a1 1 0 01-2 0v-5H4a1 1 0 010-2h5V4a1 1 0 011-1z"/></svg>
              Buat Habit 
            </a>
          </div>
          <ul class="grid gap-4 sm:grid-cols-2">{items}</ul>
        """

        print("DEBUG: Returning HTML response")
        return HTMLResponse(content=page_shell("Habits", body))
    
    except Exception as e:
        print(f"DEBUG: Exception in habits_list: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/create", response_class=HTMLResponse)
async def create_habit_form(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Create habit form (Tailwind styled)"""
    categories = [category.value for category in HabitCategory]
    frequencies = [freq.value for freq in HabitFrequency]

    cat_opts = "".join(f"<option value='{c}'>{c.title()}</option>" for c in categories)
    freq_opts = "".join(f"<option value='{f}'>{f.title()}</option>" for f in frequencies)

    body = f"""
      <div class="max-w-2xl">
        <a href="/habits" class="text-sm text-slate-600 hover:text-slate-800">&larr; Kembali</a>
        <h1 class="mt-2 text-2xl font-semibold">Buat Habit Baru</h1>
        <p class="text-slate-700 mb-6">Tetapkan niat, pilih frekuensi, dan mulai konsisten.</p>

        <form method="post" action="/habits/create" class="space-y-5 p-6 rounded-2xl glass"> 
          <div>
            <label class="block text-sm font-medium text-slate-700">Nama</label>
            <input name="name" required class="mt-1 w-full rounded-lg border-slate-300 focus:border-indigo-500 focus:ring-indigo-500" placeholder="Contoh: Baca 20 menit">
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700">Deskripsi (opsional)</label>
            <textarea name="description" rows="3" class="mt-1 w-full rounded-lg border-slate-300 focus:border-indigo-500 focus:ring-indigo-500" placeholder="Mengapa kebiasaan ini penting bagimu?"></textarea>
          </div>
          <div class="grid sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700">Kategori</label>
              <select name="category" class="mt-1 w-full rounded-lg border-slate-300 focus:border-indigo-500 focus:ring-indigo-500">{cat_opts}</select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700">Frekuensi</label>
              <select name="frequency" class="mt-1 w-full rounded-lg border-slate-300 focus:border-indigo-500 focus:ring-indigo-500">{freq_opts}</select>
            </div>
          </div>
          <div class="grid sm:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700">Target Count</label>
              <input type="number" min="1" name="target_count" value="1" class="mt-1 w-full rounded-lg border-slate-300 focus:border-indigo-500 focus:ring-indigo-500">
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700">Reminder (HH:MM)</label>
              <input name="reminder_time" placeholder="09:00" class="mt-1 w-full rounded-lg border-slate-300 focus:border-indigo-500 focus:ring-indigo-500">
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700">Warna</label>
              <input name="color" value="#3B82F6" class="mt-1 w-full rounded-lg border-slate-300 focus:border-indigo-500 focus:ring-indigo-500" />
            </div>
          </div>
          <div class="flex items-center justify-end gap-3">
            <a href="/habits" class="px-4 py-2 rounded-lg border border-white/30 text-slate-700 hover:bg-white/50">Batal</a>
            <button type="submit" class="px-5 py-2 rounded-lg btn-primary shadow-sm">Simpan</button>
          </div>
        </form>
      </div>
    """

    return HTMLResponse(content=page_shell("Buat Habit", body))


@router.post("/create")
async def create_habit(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle create habit form submission"""
    form = await request.form()

    # Create new habit
    habit = Habit(
        user_id=current_user.id,
        name=form.get("name"),
        description=form.get("description") or None,
        category=form.get("category", "other"),
        frequency=form.get("frequency", "daily"),
        target_count=int(form.get("target_count", 1)),
        reminder_time=form.get("reminder_time") or None,
        color=form.get("color", "#3B82F6")
    )

    db.add(habit)
    db.commit()

    return RedirectResponse(url="/habits/", status_code=302)


@router.get("/{habit_id}", response_class=HTMLResponse)
async def habit_detail(
    habit_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Habit detail page (Tailwind styled)"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    body = f"""
      <a href="/habits" class="text-sm text-slate-600 hover:text-slate-800">&larr; Kembali</a>
      <div class="mt-3 p-6 rounded-2xl glass"> 
        <div class="flex items-start justify-between"> 
          <div> 
            <div class="flex items-center gap-2"> 
              <span class="inline-block w-3 h-3 rounded-full" style="background:{habit.color or '#3B82F6'}"></span> 
              <h1 class="text-2xl font-semibold">{habit.name}</h1> 
            </div> 
            <p class="mt-1 text-slate-700">{habit.description or ''}</p> 
          </div> 
          <div class="text-right text-sm text-slate-600"> 
            <div class="px-2 py-1 rounded-lg bg-emerald-50 text-emerald-700">Streak: {habit.current_streak}</div> 
            <div class="mt-1">Best: {habit.best_streak}</div> 
          </div> 
        </div> 
        <div class="mt-4 flex flex-wrap gap-2 text-sm"> 
          <span class="px-2 py-1 rounded-full bg-white/60 border border-white/40 text-slate-700">Kategori: {habit.category}</span> 
          <span class="px-2 py-1 rounded-full bg-white/60 border border-white/40 text-slate-700">Frekuensi: {habit.frequency}</span> 
        </div> 
      </div> 

      <div class="mt-6 grid gap-6 md:grid-cols-3">
        <section class="md:col-span-2 p-5 rounded-2xl glass"> 
          <h2 class="font-semibold">7-Hari Timeline</h2> 
          <div id="timeline" class="mt-3 grid grid-cols-7 gap-2 text-center"></div> 
        </section>
        <aside class="p-5 rounded-2xl glass"> 
          <h2 class="font-semibold">Catatan & Mood</h2> 
          <form id="mood-form" class="mt-3 space-y-3"> 
            <div> 
              <label class="block text-sm text-slate-700">Mood</label> 
              <select id="mood" class="mt-1 w-full rounded-lg border-slate-300 focus:border-indigo-500 focus:ring-indigo-500"> 
                <option value="excellent">Excellent</option> 
                <option value="good">Good</option> 
                <option value="okay">Okay</option> 
                <option value="bad">Bad</option> 
                <option value="terrible">Terrible</option> 
              </select> 
            </div> 
            <div> 
              <label class="block text-sm text-slate-700">Catatan</label> 
              <textarea id="note" rows="3" class="mt-1 w-full rounded-lg border-slate-300 focus:border-indigo-500 focus:ring-indigo-500" placeholder="Bagaimana progresmu hari ini?"></textarea> 
            </div> 
            <button class="px-4 py-2 rounded-lg btn-primary">Simpan</button> 
            <div id="mood-msg" class="text-sm text-emerald-600 hidden">Tersimpan!</div> 
          </form> 
        </aside> 
      </div> 

      <script>
        // Render 7-day timeline (today and 6 days back)
        (function(){{
          const el = document.getElementById('timeline');
          const today = new Date();
          for (let i = 6; i >= 0; i--) {{
            const d = new Date(today);
            d.setDate(today.getDate() - i);
            const day = d.toLocaleDateString(undefined,{{ weekday:'short' }});
            const date = String(d.getDate()).padStart(2,'0');
            const cell = document.createElement('div');
            cell.className = 'p-3 rounded-lg border border-white/40 bg-white/50';
            cell.innerHTML = `<div class="text-xs text-slate-500">${{day}}</div><div class="text-lg font-semibold">${{date}}</div>`;
            el.appendChild(cell);
          }}
        }})();
        // Handle mood form submit -> POST /api/reflections
        document.getElementById('mood-form').addEventListener('submit', async function(e){{
          e.preventDefault();
          const mood = document.getElementById('mood').value;
          const note = document.getElementById('note').value;
          const res = await fetch('/api/reflections', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ mood, note }})
          }});
          if (res.ok) {{
            const m = document.getElementById('mood-msg');
            m.classList.remove('hidden');
            setTimeout(()=> m.classList.add('hidden'), 1500);
          }}
        }});
      </script>
    """

    return HTMLResponse(content=page_shell(habit.name, body))


@router.get("/{habit_id}/edit", response_class=HTMLResponse)
async def edit_habit_form(
    habit_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Edit habit form"""
    habit = db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == current_user.id
    ).first()

    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    html = f"""
    <html>
      <head><title>Edit - {habit.name}</title></head>
      <body style="font-family: Arial; max-width: 720px; margin: 40px auto;">
        <h1>Edit Habit (Coming soon)</h1>
        <p><a href="/habits">Back</a></p>
      </body>
    </html>
    """
    return HTMLResponse(content=html)