# app/routes/dashboard.py
from datetime import date, timedelta
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
      <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">
      <title>{title} • HabitVerse</title>
      <script src=\"https://cdn.tailwindcss.com\"></script>
      <script src=\"https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.2/dist/confetti.browser.min.js\"></script>
      <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
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
    <body class=\"relative bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 text-slate-800\">
      <!-- Animated aurora background -->
      <div aria-hidden=\"true\" class=\"pointer-events-none fixed inset-0 -z-10 overflow-hidden\">
        <div class=\"aurora absolute -top-20 -left-20 w-[380px] h-[380px] bg-gradient-to-br from-indigo-300 to-purple-300 rounded-full\"></div>
        <div class=\"aurora absolute bottom-0 right-[-60px] w-[420px] h-[420px] bg-gradient-to-br from-pink-300 to-rose-300 rounded-full\" style=\"animation-delay: -6s\"></div>
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
      <main class=\"max-w-5xl mx-auto px-4 py-6 sm:py-8 pb-24\">{body}</main>
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
      <footer class=\"py-8 text-center text-sm text-slate-500\">Made with intent • Keep the streak alive ✨</footer>
    </body>
    </html>
    """


def _level_and_progress(xp: int) -> tuple[int, int, int, float]:
    """Return (level, cur_threshold, next_threshold, progress_percent)."""
    # Match logic from model
    if xp < 100:
        level = 1
        cur_th, next_th = 0, 100
    elif xp < 300:
        level = 2
        cur_th, next_th = 100, 300
    elif xp < 600:
        level = 3
        cur_th, next_th = 300, 600
    elif xp < 1000:
        level = 4
        cur_th, next_th = 600, 1000
    else:
        # level 5 starts at 1000, each level +500 xp
        extra = xp - 1000
        step = extra // 500
        level = 5 + step
        cur_th = 1000 + step * 500
        next_th = cur_th + 500
    progress = 0.0 if next_th == cur_th else ((xp - cur_th) / (next_th - cur_th)) * 100.0
    return level, cur_th, next_th, min(100.0, max(0.0, progress))


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dashboard page (Tailwind styled)"""
    xp = current_user.xp or 0
    level, cur_th, next_th, progress = _level_and_progress(xp)

    body = f"""
      <div class=\"flex items-center justify-between\">
        <div>
          <h1 class=\"text-2xl font-semibold\">Welcome, {current_user.name} 👋</h1>
          <p class=\"text-slate-600\">Lihat progresmu dan lanjutkan streak hari ini.</p>
        </div>
        <a href=\"/habits/create\" class=\"inline-flex items-center gap-2 px-4 py-2 rounded-lg btn-primary shadow-sm\">+ Habit Baru</a>
      </div>

      <div class=\"mt-6 grid gap-4 sm:grid-cols-3\">
        <div class=\"p-5 rounded-2xl glass\">
          <div class=\"text-sm text-slate-500\">Level</div>
          <div class=\"mt-1 text-2xl font-semibold\">{level}</div>
          <div class=\"mt-3 h-2 bg-slate-100 rounded-full overflow-hidden\">
            <div class=\"h-2 bg-indigo-600\" style=\"width:{progress:.0f}%\"></div>
          </div>
          <div class=\"mt-1 text-xs text-slate-500\">{xp - cur_th} / {next_th - cur_th} XP to next level</div>
        </div>
        <div class=\"p-5 rounded-2xl glass\">
          <div class=\"text-sm text-slate-500\">Total XP</div>
          <div class=\"mt-1 text-2xl font-semibold\">{xp}</div>
        </div>
        <div class=\"p-5 rounded-2xl glass\">
          <div class=\"text-sm text-slate-500\">Quote of the Day</div>
          <div id=\"q-text\" class=\"mt-1 text-slate-700\">—</div>
          <div id=\"q-author\" class=\"text-sm text-slate-500\"></div>
          <div class=\"mt-3 border-t border-white/30 pt-3\">
            <div class=\"text-sm text-slate-500\">Daily Tip</div>
            <div id=\"tip-text\" class=\"mt-1 text-slate-700\">—</div>
          </div>
        </div>
      </div>

      <div class=\"mt-6 p-5 rounded-2xl glass\">
        <div class=\"flex items-center justify-between mb-4\">
          <h2 class=\"text-lg font-semibold\">Kalender Aktivitas</h2>
          <div class=\"text-xs text-slate-500\" id=\"heatmap-legend\">Loading…</div>
        </div>
        <div class=\"overflow-x-auto\"> 
          <svg id=\"heatmap\" viewBox=\"0 0 900 140\" preserveAspectRatio=\"xMidYMid meet\" style=\"width:100%; height:auto;\" role=\"img\" aria-label=\"Calendar heatmap\"></svg>
        </div>
      </div>

      <div class=\"mt-6 p-5 rounded-2xl glass\">
        <div class=\"flex items-center justify-between mb-3\">
          <h2 class=\"text-lg font-semibold\">Progres Hari Ini</h2>
          <a href=\"/habits\" class=\"text-xs text-indigo-600 hover:underline\">Kelola</a>
        </div>
        <div id=\"today-progress\" class=\"grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4\"></div>
      </div>

      <div class=\"mt-6 p-5 rounded-2xl glass\">
        <div class=\"flex items-center justify-between mb-3\">
          <h2 class=\"text-lg font-semibold\">Badges</h2>
          <div class=\"text-xs text-slate-500\" id=\"streak-info\">—</div>
        </div>
        <div id=\"badges\" class=\"flex flex-wrap gap-2\"></div>
      </div>

      <div class=\"mt-8 p-6 rounded-2xl glass\">
        <div class=\"flex items-center justify-between mb-3\">
          <h2 class=\"text-lg font-semibold\">Aksi Cepat</h2>
        </div>
        <div class=\"flex flex-wrap gap-3\">
          <a href=\"/habits\" class=\"px-4 py-2 rounded-lg border border-white/30 hover:bg-white/40\">Kelola Habits</a>
          <a href=\"/community\" class=\"px-4 py-2 rounded-lg border border-white/30 hover:bg-white/40\">Community</a>
          <a href=\"/coach\" class=\"px-4 py-2 rounded-lg border border-white/30 hover:bg-white/40\">AI Coach</a>
          <a href=\"/auth/logout\" class=\"px-4 py-2 rounded-lg border border-slate-300 hover:bg-slate-50\">Logout</a>
        </div>
      </div>

      <!-- Floating Add Button -->
      <a href=\"/habits/create\" aria-label=\"Tambah Habit\" class=\"fixed right-5 bottom-20 sm:bottom-8 z-10 inline-flex items-center justify-center w-14 h-14 rounded-full shadow-xl btn-primary\">
        <span class=\"text-2xl\">＋</span>
      </a>

      <script>
        // Confetti (emoji) lightweight
        function confettiBurst(duration = 800) {{
          const emojis = ['✨','🎉','🔥','💪','🌟'];
          const count = 24;
          for (let i=0;i<count;i++) {{
            const span = document.createElement('span');
            span.textContent = emojis[Math.floor(Math.random()*emojis.length)];
            span.style.position = 'fixed';
            span.style.left = (window.innerWidth*0.5 + (Math.random()-0.5)*120) + 'px';
            span.style.top = (window.innerHeight*0.35 + (Math.random()-0.5)*80) + 'px';
            span.style.fontSize = (16 + Math.random()*14) + 'px';
            span.style.pointerEvents = 'none';
            span.style.zIndex = 50;
            document.body.appendChild(span);
            const dx = (Math.random()-0.5)*300;
            const dy = - (Math.random()*300 + 120);
            const rotate = (Math.random()-0.5)*360;
            const start = performance.now();
            requestAnimationFrame(function anim(t) {{
              const p = Math.min(1, (t-start)/duration);
              const ease = 1- Math.pow(1-p, 2);
              span.style.transform = `translate(${{dx*ease}}px, ${{dy*ease}}px) rotate(${{rotate*ease}}deg)`;
              span.style.opacity = String(1-p);
              if (p < 1) requestAnimationFrame(anim); else span.remove();
            }});
          }}
        }}

        // Daily Tip
        const TIPS = [
          'Mulai dengan 2 menit saja hari ini ✨',
          'Fokus ke satu kebiasaan kecil dulu.',
          'Letakkan habit di tempat yang mudah terlihat.',
          'Pasang pengingat di jam terbaik versimu.',
          'Jangan kejar sempurna, kejar konsisten.',
          'Rayakan progres kecilmu hari ini 🎉',
          'Lakukan di waktu yang sama tiap hari ⏰',
          'Siapkan alatnya dari malam sebelumnya.',
        ];
        function loadTip() {{
          const tip = TIPS[Math.floor(Math.random()*TIPS.length)];
          const el = document.getElementById('tip-text');
          if (el) el.textContent = tip;
        }}

        async function loadQuote() {{
          try {{
            const res = await fetch('/api/quotes/today');
            if (!res.ok) return;
            const data = await res.json();
            document.getElementById('q-text').innerText = '“' + data.quote + '”';
            document.getElementById('q-author').innerText = '— ' + (data.author || 'Unknown');
          }} catch (e) {{}}
        }}
        loadQuote();
        loadTip();

        // Heatmap with green->blue->purple gradient and graceful fallback
        async function loadHeatmap(days = 180) {{
          const svg = document.getElementById('heatmap');
          const legend = document.getElementById('heatmap-legend');
          if (!svg) return;
          legend.textContent = 'Loading…';
          try {{
            const res = await fetch(`/api/habits/stats/heatmap?days=${{days}}`);
            if (!res.ok) throw new Error('failed');
            const payload = await res.json();
            const data = payload.data || [];
            renderHeatmap(svg, legend, days, data);
          }} catch (e) {{
            // Render empty grid instead of failing text
            renderHeatmap(svg, legend, days, []);
          }}
        }}

        function renderHeatmap(svg, legend, days, data) {{
          const map = new Map(data.map(d => [d.date, d.count]));
          const cell = 12, gap = 3, top = 12, left = 24;
          const today = new Date();
          const dates = [];
          for (let i = days - 1; i >= 0; i--) {{
            const d = new Date(today);
            d.setDate(d.getDate() - i);
            const iso = d.toISOString().slice(0,10);
            dates.push({{ d, iso }});
          }}
          let max = 0; for (const {{ iso }} of dates) max = Math.max(max, map.get(iso) || 0);
          // levels for gradient (0 -> low green, 4 -> high purple)
          const steps = [0, 1, Math.max(2, Math.ceil(max*0.33)), Math.max(3, Math.ceil(max*0.66)), Math.max(4, Math.max(1,max))];
          function color(c) {{
            if (c <= 0) return '#E5E7EB'; // gray-200
            if (c <= steps[1]) return '#86EFAC'; // green-300
            if (c <= steps[2]) return '#60A5FA'; // blue-400
            if (c <= steps[3]) return '#A78BFA'; // purple-400
            return '#8B5CF6'; // purple-500
          }}
          const weeks = Math.ceil(dates.length / 7);
          const width = left + weeks * (cell + gap) + 20;
          const height = top + 7 * (cell + gap) + 20;
          svg.setAttribute('viewBox', `0 0 ${{width}} ${{height}}`);
          svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
          svg.style.width = '100%';
          svg.style.height = 'auto';
          svg.innerHTML = '';
          // Month labels (approx, every 4 weeks)
          for (let w = 0; w < weeks; w += 4) {{
            const text = document.createElementNS('http://www.w3.org/2000/svg','text');
            text.setAttribute('x', left + w * (cell + gap));
            text.setAttribute('y', 10);
            text.setAttribute('fill', '#64748B');
            text.setAttribute('font-size', '10');
            const dt = new Date(today); dt.setDate(dt.getDate() - (weeks - 1 - w)*7);
            text.textContent = dt.toLocaleString(undefined, {{ month: 'short' }});
            svg.appendChild(text);
          }}
          // Cells
          dates.forEach((obj, idx) => {{
            const week = Math.floor(idx / 7);
            const day = obj.d.getDay();
            const x = left + week * (cell + gap);
            const y = top + day * (cell + gap);
            const c = map.get(obj.iso) || 0;
            const rect = document.createElementNS('http://www.w3.org/2000/svg','rect');
            rect.setAttribute('x', x);
            rect.setAttribute('y', y);
            rect.setAttribute('width', cell);
            rect.setAttribute('height', cell);
            rect.setAttribute('rx', 2);
            rect.setAttribute('ry', 2);
            rect.setAttribute('fill', color(c));
            rect.setAttribute('data-date', obj.iso);
            rect.setAttribute('data-count', c);
            rect.addEventListener('mouseenter', () => {{ svg.title = `${{obj.iso}}: ${{c}}` }});
            svg.appendChild(rect);
          }});
          // Legend
          legend.innerHTML = '';
          const less = document.createElement('span'); less.textContent = 'Less'; less.className='mr-2'; legend.appendChild(less);
          [0,1,2,3,4].forEach(i=>{{
            const box = document.createElement('span');
            box.style.width='12px'; box.style.height='12px'; box.style.borderRadius='3px'; box.style.display='inline-block'; box.style.marginRight='4px';
            const lvl = i===0?0:steps[i]; box.style.background = color(lvl);
            legend.appendChild(box);
          }});
          const more = document.createElement('span'); more.textContent='More'; more.className='ml-1'; legend.appendChild(more);
          // Streak compute for badges
          let streak = 0; for (let i = dates.length-1; i>=0; i--) {{ if ((map.get(dates[i].iso)||0) > 0) streak++; else break; }}
          document.getElementById('streak-info').textContent = `🔥 ${{streak}} hari streak`;
          renderBadges(streak);
        }}

        function renderBadges(streak) {{
          const wrap = document.getElementById('badges'); if (!wrap) return; wrap.innerHTML='';
          const tiers = [3,7,14,30,60,100,200,365];
          tiers.forEach(t => {{
            const got = streak >= t;
            const badge = document.createElement('div');
            badge.className = `px-3 py-1 rounded-full text-xs border ${{got?'bg-indigo-50 border-indigo-200 text-indigo-700':'bg-white/40 border-white/40 text-slate-500'}}`;
            badge.textContent = `🔥 ${{t}}d`;
            wrap.appendChild(badge);
          }});
        }}

        // Per-habit circular progress for today + Complete action
        async function loadTodayProgress() {{
          const container = document.getElementById('today-progress'); if (!container) return;
          container.innerHTML = '';
          try {{
            const res = await fetch('/api/habits'); if (!res.ok) throw new Error('habits');
            const habits = await res.json();
            const todayISO = new Date().toISOString().slice(0,10);
            for (const h of habits) {{
              let count = 0; let target = h.target_count || 1;
              try {{
                const lr = await fetch(`/api/habits/${{h.id}}/logs?days=1`);
                if (lr.ok) {{
                  const logs = await lr.json();
                  const today = logs.find(x => x.date && x.date.startsWith(todayISO));
                  if (today && today.status === 'completed') count = today.count || 1;
                }}
              }} catch(e) {{}}
              const pct = Math.min(100, Math.round((count/Math.max(1,target))*100));
              const card = document.createElement('div');
              card.className = 'p-3 rounded-xl border border-white/40 bg-white/50 flex items-center gap-3';
              const size = 56; const stroke = 6; const r = (size-stroke)/2; const cx=size/2, cy=size/2; const C=2*Math.PI*r; const off=C*(1-pct/100);
              card.innerHTML = `
                <svg width="${{size}}" height="${{size}}" viewBox="0 0 ${{size}} ${{size}}">
                  <circle cx="${{cx}}" cy="${{cy}}" r="${{r}}" stroke="#E5E7EB" stroke-width="${{stroke}}" fill="none" />
                  <circle cx="${{cx}}" cy="${{cy}}" r="${{r}}" stroke="#6366F1" stroke-width="${{stroke}}" fill="none" stroke-linecap="round" stroke-dasharray="${{C}}" stroke-dashoffset="${{C}}" transform="rotate(-90 ${{cx}} ${{cy}})" />
                </svg>
                <div class="min-w-0">
                  <div class="text-sm font-medium truncate">${{h.name}}</div>
                  <div class="text-xs text-slate-500">${{count}} / ${{target}}</div>
                </div>
                <div class="ml-auto flex items-center gap-2">
                  <div class="text-sm font-semibold min-w-[2.5rem] text-right">${{pct}}%</div>
                  ${{pct < 100 ? `<button class=\"px-2 py-1 text-xs rounded-md btn-primary\" data-hid=\"${{h.id}}\">Complete</button>` : ''}}
                </div>
              `;
              container.appendChild(card);
              // animate progress
              const fg = card.querySelectorAll('circle')[1];
              requestAnimationFrame(() => {{ fg.setAttribute('stroke-dashoffset', off); }});
              // small pop when completed
              if (pct >= 100) {{ card.classList.add('ring-2','ring-indigo-300'); setTimeout(()=>card.classList.remove('ring-2','ring-indigo-300'), 800); }}

              // wire Complete button
              const btn = card.querySelector('button[data-hid]');
              if (btn) {{
                btn.addEventListener('click', async () => {{
                  const id = btn.getAttribute('data-hid');
                  btn.disabled = true; btn.textContent = '...';
                  try {{
                    const r = await fetch(`/api/habits/${{id}}/log`, {{
                      method: 'POST',
                      headers: {{ 'Content-Type': 'application/json' }},
                      body: JSON.stringify({{ status: 'completed', count: 1 }})
                    }});
                    if (!r.ok) throw new Error('log failed');
                    confettiBurst(900);
                    await loadHeatmap(182); // refresh heatmap as well
                    await loadTodayProgress(); // re-render cards
                  }} catch (e) {{
                    alert('Gagal menandai selesai. Coba lagi.');
                  }} finally {{
                    // no re-enable; the list will re-render
                  }}
                }});
              }}
            }}
          }} catch (e) {{
            container.innerHTML = '<div class="text-sm text-slate-500">Gagal memuat progres.</div>';
          }}
        }}

        // Level-up confetti based on stored previous level
        (function levelUpCheck() {{
          try {{
            const key = 'hv_prev_level';
            const prev = parseInt(localStorage.getItem(key) || '0', 10);
            const cur = {level};
            if (cur > prev) {{ confettiBurst(); }}
            localStorage.setItem(key, String(cur));
          }} catch(e) {{}}
        }})();

        loadHeatmap(182);
        loadTodayProgress();
      </script>
    """

    return HTMLResponse(content=page_shell("Dashboard", body))
