from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.db.models import User

router = APIRouter()

@router.get("/u/{user_id}", response_class=HTMLResponse)
def public_profile_page(user_id: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Build HTML without f-string to avoid JS template literal conflicts
    head = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Profile • HabitVerse</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 text-slate-800">
  <header class="bg-white/10 backdrop-blur-md border-b border-white/20">
    <div class="max-w-5xl mx-auto px-4 py-6 flex items-center justify-between">
      <a href="/dashboard" class="text-xl font-semibold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-fuchsia-600">HabitVerse</a>
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
  <main class="max-w-5xl mx-auto px-4 py-6 sm:py-8 pb-24">
    <div id="user-head" class="bg-white rounded-xl shadow-sm p-6"></div>
    <div class="bg-white rounded-xl shadow-sm p-6 mt-6">
      <h2 class="text-xl font-semibold mb-4">Posts</h2>
      <div id="user-posts" class="space-y-3"><div class="text-slate-600 text-sm">Memuat…</div></div>
    </div>
  </main>
  <script>
"""
    uid_line = "    const uid = " + repr(user_id) + ";\n"
    tail = """
    function avatarHtml(u){
      if(u && u.avatar_url){ return `<img src="${u.avatar_url}" class="w-12 h-12 rounded-full object-cover"/>`; }
      const n = (u && u.name ? u.name : '?').slice(0,1).toUpperCase();
      return `<div class="w-12 h-12 rounded-full bg-indigo-200 flex items-center justify-center text-base text-indigo-800">${n}</div>`;
    }
    function postHtml(p){
      return `
        <div class="rounded-2xl glass p-4 border border-white/20 ring-1 ring-white/10" data-post-id="${p.id}"> 
          <div class="flex items-center gap-3 mb-2"> 
            ${avatarHtml(p.user)}
            <div>
              <div class="text-sm font-medium">${p.user.name}</div>
              <div class="text-xs text-slate-500">${new Date(p.created_at).toLocaleString()}</div>
            </div>
          </div>
          ${p.content ? `<div class="text-sm">${p.content}</div>` : ''}
          ${p.image_url ? `<img src="${p.image_url}" class="mt-2 rounded-lg max-h-72 object-cover w-full"/>` : ''}
          <div class="mt-3 flex items-center gap-4 text-sm text-slate-600"> 
            <button class="btn-like ${p.you_liked? 'text-indigo-600 font-medium':''}">❤️ ${p.like_count}</button>
            <button class="btn-comment">💬 ${p.comment_count}</button>
            <button class="btn-share">↗️ Share</button>
          </div>
          <div class="comments mt-3 hidden">
            <div class="comments-list space-y-2 text-sm"></div>
            <div class="flex gap-2 mt-2">
              <input class="comment-input flex-1 border rounded px-2 py-1 text-sm" placeholder="Tulis komentar..."/>
              <button class="btn-send-comment px-3 py-1.5 rounded-lg btn-primary text-sm">Kirim</button>
            </div>
          </div>
        </div>`;
    }
    async function loadUser(){
      const head = document.querySelector('#user-head');
      try{
        const res = await fetch(`/api/users/${uid}`, { credentials:'include' });
        if(!res.ok){ head.innerHTML = '<div class="text-sm text-slate-600">User not found</div>'; return; }
        const u = await res.json();
        head.innerHTML = `
          <div class="flex items-center gap-4"> 
            ${avatarHtml(u)}
            <div>
              <div class="text-2xl font-bold">${u.name} </div>
              ${u.profile ? `<div class="text-slate-600">${u.profile}</div>` : ''}
            </div>
          </div>
        `;
      }catch(e){ head.innerHTML = '<div class="text-sm text-slate-600">Gagal memuat user</div>'; }
    }
    async function loadPosts(){
      const wrap = document.querySelector('#user-posts');
      try{
        const res = await fetch(`/api/posts/user/${uid}`, { credentials:'include' });
        if(!res.ok){ wrap.innerHTML = '<div class="text-sm text-slate-600">Gagal memuat postingan</div>'; return; }
        const items = await res.json();
        if(!items.length){ wrap.innerHTML = '<div class="text-sm text-slate-600">Belum ada postingan.</div>'; return; }
        wrap.innerHTML = items.map(postHtml).join('');
        bindPostEvents(wrap);
      }catch(e){ wrap.innerHTML = '<div class="text-sm text-slate-600">Gagal memuat postingan</div>'; }
    }
    function bindPostEvents(scope){
      scope.querySelectorAll('[data-post-id]').forEach(card => {
        const postId = card.getAttribute('data-post-id');
        card.querySelector('.btn-like').addEventListener('click', async () => {
          const liked = card.querySelector('.btn-like').classList.contains('text-indigo-600');
          const method = liked ? 'DELETE' : 'POST';
          const res = await fetch(`/api/posts/${postId}/like`, { method, credentials:'include' });
          if(res.ok){ loadPosts(); }
        });
        card.querySelector('.btn-comment').addEventListener('click', async () => {
          const box = card.querySelector('.comments');
          box.classList.toggle('hidden');
          if(!box.classList.contains('hidden')){
            const res = await fetch(`/api/posts/${postId}/comments`, { credentials:'include' });
            if(res.ok){
              const comments = await res.json();
              const list = card.querySelector('.comments-list');
              list.innerHTML = comments.map(c=>`<div><span class="font-medium">${c.user.name} </span> <span class="text-slate-500 text-xs">${new Date(c.created_at).toLocaleString()} </span><div>${c.content} </div></div>`).join('');
            }
          }
        });
        card.querySelector('.btn-send-comment').addEventListener('click', async () => {
          const input = card.querySelector('.comment-input');
          const content = input.value.trim(); if(!content) return;
          const res = await fetch(`/api/posts/${postId}/comments`, { method:'POST', headers:{'Content-Type':'application/json'}, credentials:'include', body: JSON.stringify({ content }) });
          if(res.ok){ input.value=''; card.querySelector('.btn-comment').click(); }
        });
        card.querySelector('.btn-share').addEventListener('click', async () => {
          const url = `${window.location.origin}/u/${uid}#post-${postId}`;
          if(navigator.share){ try{ await navigator.share({ title:'HabitVerse', url }); }catch(_){/* ignore */} }
          else{ navigator.clipboard.writeText(url); alert('Link disalin'); }
        });
      });
    }
    loadUser(); loadPosts();
  </script>
</body>
</html>
"""
    return HTMLResponse(content=head + uid_line + tail)
