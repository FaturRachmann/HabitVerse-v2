# app/routes/coach.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.db.models import User

router = APIRouter()


def page_shell(title: str, body: str) -> str:
    return f"""
    <!doctype html>
    <html lang=\"en\">
    <head>
      <meta charset=\"utf-8\">
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
      <title>{title} • HabitVerse</title>
      <script src=\"https://cdn.tailwindcss.com\"></script>
      <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap\" rel=\"stylesheet\">
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
      <footer class="py-8 text-center text-sm text-slate-500">Your daily nudge • Small steps, big change ✨</footer>
    </body>
    </html>
    """


@router.get("/coach", response_class=HTMLResponse)
async def coach(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI Coach page (goal input + chat stub)."""
    body = """
      <div class=\"mb-6\">
        <h1 class=\"text-2xl font-semibold\">AI Coach</h1>
        <p class=\"text-slate-600\">Tulis tujuanmu, dapatkan roadmap dan dukungan.</p>
      </div>
      <div class=\"grid gap-6 md:grid-cols-2\">
        <section class=\"p-5 rounded-2xl glass\"> 
          <h2 class=\"font-semibold\">Goal to Roadmap</h2>
          <form id=\"goal-form\" class=\"mt-3 space-y-3\" onsubmit=\"event.preventDefault();fakeRoadmap();\">
            <input name=\"goal\" id=\"goal\" class=\"w-full rounded-lg border-slate-300 focus:border-indigo-500 focus:ring-indigo-500\" placeholder=\"Contoh: Lari 5K dalam 30 hari\">
            <button class=\"px-4 py-2 rounded-lg btn-primary\">Buat Roadmap</button>
          </form>
          <div id=\"roadmap\" class=\"mt-4 text-sm text-slate-700 space-y-2\"></div>
        </section>
        <section class=\"p-5 rounded-2xl glass\"> 
          <h2 class=\"font-semibold\">Motivation Chat</h2>
          <div id=\"chat\" class=\"mt-3 h-64 overflow-auto space-y-3\">
            <div class=\"flex gap-2 items-start\"><div class=\"px-3 py-2 rounded-xl bg-white/60\">Halo %s! Apa yang ingin kamu capai hari ini?</div></div>
          </div>
          <form class=\"mt-3 flex gap-2\" onsubmit=\"event.preventDefault();fakeReply();\">
            <input id=\"msg\" class=\"flex-1 rounded-lg border-slate-300 focus:border-indigo-500 focus:ring-indigo-500\" placeholder=\"Tulis pesan...\">
            <button class=\"px-4 py-2 rounded-lg btn-primary\">Kirim</button>
          </form>
        </section>
      </div>
      <script>
        function fakeRoadmap(){
          const g = document.getElementById('goal').value || 'Tujuanmu';
          const el = document.getElementById('roadmap');
          el.innerHTML = `<div class=\"font-medium\">Roadmap 4 Minggu:</div>
            <ul class=\"list-disc pl-5 space-y-1\">
              <li>Minggu 1: Dasar & kebiasaan kecil terkait \"${g}\"</li>
              <li>Minggu 2: Tambah intensitas + track progres</li>
              <li>Minggu 3: Simulasi target + recovery</li>
              <li>Minggu 4: Final push + evaluasi</li>
            </ul>`;
        }
        function fakeReply(){
          const chat = document.getElementById('chat');
          const msg = document.getElementById('msg');
          if(!msg.value) return;
          const user = document.createElement('div');
          user.className = 'flex gap-2 items-start justify-end';
          user.innerHTML = `<div class=\"px-3 py-2 rounded-xl bg-indigo-600 text-white\">${msg.value}</div>`;
          chat.appendChild(user);
          const coach = document.createElement('div');
          coach.className = 'flex gap-2 items-start';
          coach.innerHTML = `<div class=\"px-3 py-2 rounded-xl bg-white/60\">Mantap! Fokus ke langkah kecil hari ini ya. Aku akan cek lagi besok 🔥</div>`;
          setTimeout(()=> chat.appendChild(coach), 400);
          msg.value='';
          chat.scrollTop = chat.scrollHeight;
        }
      </script>
    """ % (
        current_user.name,
    )

    return HTMLResponse(content=page_shell("AI Coach", body))
