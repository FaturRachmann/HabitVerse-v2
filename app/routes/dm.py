# app/routes/dm.py
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
      <style>
        html,body{{font-family:ui-sans-serif,system-ui,Segoe UI,Roboto,Helvetica,Arial}}
        .glass{{background:rgba(255,255,255,.6);backdrop-filter:blur(12px);border:1px solid rgba(15,23,42,.06)}}
        .btn-primary{{background-image:linear-gradient(135deg,#6366F1,#A855F7); color:#fff}}
      </style>
    </head>
    <body class=\"bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 text-slate-800 min-h-screen\">\n
      <header class=\"glass sticky top-0 z-30\">\n        <div class=\"max-w-5xl mx-auto px-4 py-4 flex items-center justify-between\">\n          <a href=\"/dashboard\" class=\"font-semibold text-indigo-600\">HabitVerse</a>\n          <div class=\"text-sm text-slate-600\">Direct Messages</div>\n        </div>\n      </header>\n
      <main class=\"max-w-5xl mx-auto px-4 py-6 sm:py-8 pb-24\">{body}</main>\n
      <!-- Mobile bottom nav -->\n      <nav class=\"sm:hidden fixed bottom-0 inset-x-0 bg-white/80 backdrop-blur border-t border-slate-200/60 shadow-lg\">\n        <div class=\"max-w-5xl mx-auto grid grid-cols-5\">\n          <a href=\"/dashboard\" class=\"flex flex-col items-center justify-center py-3 text-[11px] text-slate-700\">Home</a>\n          <a href=\"/habits\" class=\"flex flex-col items-center justify-center py-3 text-[11px] text-slate-700\">Habits</a>\n          <a href=\"/community\" class=\"flex flex-col items-center justify-center py-3 text-[11px] text-slate-700\">Community</a>\n          <a href=\"/coach\" class=\"flex flex-col items-center justify-center py-3 text-[11px] text-slate-700\">Coach</a>\n          <a href=\"/profile\" class=\"flex flex-col items-center justify-center py-3 text-[11px] text-slate-700\">Profile</a>\n        </div>\n      </nav>\n    </body>\n    </html>
    """


@router.get("/dm", response_class=HTMLResponse)
async def dm_home(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    body = """
    <div class=\"grid gap-4 md:grid-cols-3\">\n      <!-- Sidebar: Friends + Search -->\n      <aside class=\"md:col-span-1 space-y-3\">\n        <div class=\"flex items-center justify-between\">\n          <h2 class=\"text-lg font-semibold\">Chats</h2>\n          <a href=\"/friends\" class=\"text-sm text-indigo-600 hover:text-indigo-700\">Find friends</a>\n        </div>\n        <div>\n          <input id=\"dm-search\" class=\"w-full border rounded-lg px-3 py-2\" placeholder=\"Search users...\" />\n        </div>\n        <div id=\"dm-search-results\" class=\"rounded-2xl glass divide-y hidden\"></div>\n        <div class=\"text-sm text-slate-500\">Your friends</div>\n        <div id=\"dm-friends\" class=\"rounded-2xl glass divide-y\">\n          <div class=\"p-3 text-sm text-slate-500\">Loading friends...</div>\n        </div>\n      </aside>\n
      <!-- Messages area -->\n      <section class=\"md:col-span-2 rounded-2xl glass p-4 flex flex-col h-[60vh]\">\n        <div id=\"dm-header\" class=\"pb-3 border-b mb-3 hidden\"></div>\n        <div id=\"dm-messages\" class=\"flex-1 overflow-auto space-y-2\">\n          <div class=\"text-center text-sm text-slate-500 my-4\">Start a conversation. Group chats and 1:1 will be supported.</div>\n        </div>\n        <div class=\"mt-3 flex items-center gap-2\">\n          <input id=\"dm-input\" class=\"flex-1 border rounded-lg px-3 py-2\" placeholder=\"Type a message... (coming soon)\" disabled />\n          <button id=\"dm-send\" class=\"px-4 py-2 rounded-lg btn-primary opacity-60 cursor-not-allowed\" disabled>Send</button>\n        </div>\n      </section>\n    </div>
    <script>
      const qs = (k)=> new URLSearchParams(location.search).get(k);

      async function loadFriends(){
        try{
          const res = await fetch('/api/friends', { credentials:'include' });
          const wrap = document.getElementById('dm-friends');
          if(!res.ok){ wrap.innerHTML = '<div class="p-3 text-sm text-red-600">Failed to load friends</div>'; return; }
          const friends = await res.json();
          if(!friends.length){ wrap.innerHTML = '<div class="p-3 text-sm text-slate-500">No friends yet. Go add some!</div>'; return; }
          wrap.innerHTML = friends.map(f=>`
            <a class="flex items-center gap-3 p-3 hover:bg-white/70" href="/dm?to=${f.id}">
              ${f.avatar_url ? `<img src="${f.avatar_url}" class="w-8 h-8 rounded-full object-cover"/>` : `<div class=\"w-8 h-8 rounded-full bg-indigo-200 flex items-center justify-center text-xs text-indigo-800\">${(f.name||'?').slice(0,1).toUpperCase()}</div>`}
              <div>
                <div class="text-sm font-medium">${f.name}</div>
                <div class="text-xs text-slate-500">Level ${f.level} • ${f.xp} XP</div>
              </div>
            </a>
          `).join('');
        }catch(e){
          document.getElementById('dm-friends').innerHTML = '<div class="p-3 text-sm text-red-600">Error loading friends</div>';
        }
      }

      // Live search users
      let searchTimer;
      document.getElementById('dm-search').addEventListener('input',(e)=>{
        clearTimeout(searchTimer);
        const q = e.target.value.trim();
        const box = document.getElementById('dm-search-results');
        if(q.length < 2){ box.classList.add('hidden'); box.innerHTML=''; return; }
        searchTimer = setTimeout(async()=>{
          try{
            const res = await fetch(`/api/users/search?q=${encodeURIComponent(q)}`, { credentials:'include' });
            if(!res.ok){ box.classList.remove('hidden'); box.innerHTML='<div class="p-3 text-sm text-red-600">Search failed</div>'; return; }
            const users = await res.json();
            if(!users.length){ box.classList.remove('hidden'); box.innerHTML='<div class="p-3 text-sm text-slate-500">No users found</div>'; return; }
            box.classList.remove('hidden');
            box.innerHTML = users.map(u=>`
              <div class="p-3 hover:bg-white/70 flex items-center justify-between">
                <a href="/u/${u.id}" class="flex items-center gap-3 group">
                  ${u.avatar_url ? `<img src="${u.avatar_url}" class="w-8 h-8 rounded-full object-cover"/>` : `<div class=\"w-8 h-8 rounded-full bg-indigo-200 flex items-center justify-center text-xs text-indigo-800\">${(u.name||'?').slice(0,1).toUpperCase()}</div>`}
                  <div>
                    <div class="text-sm font-medium group-hover:underline">${u.name}</div>
                    <div class="text-xs text-slate-500">Level ${u.level} • ${u.xp} XP</div>
                  </div>
                </a>
                <a href="/dm?to=${u.id}" class="text-xs text-indigo-600 hover:text-indigo-700">Message</a>
              </div>
            `).join('');
          }catch(e){ box.classList.remove('hidden'); box.innerHTML='<div class="p-3 text-sm text-red-600">Search error</div>'; }
        }, 300);
      });

      async function loadTarget(){
        const to = qs('to');
        const header = document.getElementById('dm-header');
        if(!to){ header.classList.add('hidden'); return; }
        try{
          const res = await fetch(`/api/users/${to}`, { credentials:'include' });
          if(!res.ok){ header.classList.remove('hidden'); header.innerHTML = '<div class="text-sm text-red-600">User not found</div>'; return; }
          const u = await res.json();
          header.classList.remove('hidden');
          header.innerHTML = `
            <div class="flex items-center justify-between">
              <a href="/u/${u.id}" class="flex items-center gap-3 group">
                ${u.avatar_url ? `<img src="${u.avatar_url}" class="w-9 h-9 rounded-full object-cover"/>` : `<div class=\"w-9 h-9 rounded-full bg-indigo-200 flex items-center justify-center text-xs text-indigo-800\">${(u.name||'?').slice(0,1).toUpperCase()}</div>`}
                <div>
                  <div class="text-sm font-medium group-hover:underline">${u.name}</div>
                  <div class="text-xs text-slate-500">Level ${u.level} • ${u.xp} XP</div>
                </div>
              </a>
              <a href="/friends" class="text-xs text-slate-500 hover:text-slate-700">Manage</a>
            </div>
          `;
          enableMessaging(u);
        }catch(e){ header.classList.remove('hidden'); header.innerHTML = '<div class="text-sm text-red-600">Failed to load user</div>'; }
      }

      function renderMessages(list, currentUserId){
        const wrap = document.getElementById('dm-messages');
        if(!list.length){ wrap.innerHTML = '<div class="text-center text-sm text-slate-500 my-4">No messages yet. Say hi! 👋</div>'; return; }
        wrap.innerHTML = list
          .slice() // ensure it's an array
          .reverse() // oldest first for display
          .map(m=>{
            const mine = m.sender_id === currentUserId;
            return `
              <div class="flex ${mine ? 'justify-end' : 'justify-start'}">
                <div class="max-w-[75%] px-3 py-2 rounded-xl text-sm ${mine ? 'bg-indigo-600 text-white' : 'bg-white/80 border'}">
                  <div>${m.content.replace(/</g,'&lt;')}</div>
                  <div class="text-[10px] opacity-70 mt-1">${new Date(m.created_at).toLocaleTimeString()}</div>
                </div>
              </div>
            `;
          }).join('');
        wrap.scrollTop = wrap.scrollHeight;
      }

      async function loadMessagesLoop(otherId){
        try{
          const res = await fetch(`/api/messages/with/${otherId}`, { credentials:'include' });
          if(!res.ok) return;
          const items = await res.json();
          // current user id is not exposed here; infer from sender/recipient by finding a friend anchor selected is not ideal.
          // Simpler approach: we request /api/users/${otherId} above; use a crude way to infer: pick any message and if sender != otherId -> that's me.
          let me = null;
          if(items.length){
            const any = items[0];
            me = (any.sender_id === otherId) ? any.recipient_id : any.sender_id;
          }
          renderMessages(items, me);
        }catch(e){ /* ignore */ }
      }

      function enableMessaging(user){
        const input = document.getElementById('dm-input');
        const btn = document.getElementById('dm-send');
        input.disabled = false;
        btn.disabled = false;
        btn.classList.remove('opacity-60','cursor-not-allowed');

        async function send(){
          const text = input.value.trim();
          if(!text) return;
          btn.disabled = true;
          try{
            const res = await fetch(`/api/messages/send?to=${encodeURIComponent(user.id)}&content=${encodeURIComponent(text)}`, {
              method:'POST',
              credentials:'include'
            });
            if(res.ok){
              input.value = '';
              // refresh messages quickly
              loadMessagesLoop(user.id);
            }
          } finally {
            btn.disabled = false;
          }
        }

        btn.addEventListener('click', send);
        input.addEventListener('keydown', (e)=>{ if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); send(); } });

        // initial load and polling
        loadMessagesLoop(user.id);
        setInterval(()=> loadMessagesLoop(user.id), 4000);
      }

      loadFriends();
      loadTarget();
    </script>
    """
    return HTMLResponse(content=page_shell("Direct Messages", body))
