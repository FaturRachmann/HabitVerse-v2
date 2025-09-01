from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, get_password_hash, verify_password
from app.db.models import User

router = APIRouter()

@router.get("/profile", response_class=HTMLResponse)
def profile_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return HTMLResponse(
        content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Profile - HabitVerse</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
            <style>
                html,body{{font-family:'Inter',system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif}}
                .glass{{background:rgba(255,255,255,.3); backdrop-filter:blur(18px); border:1px solid rgba(255,255,255,.25); box-shadow:0 8px 30px rgba(31,38,135,.15)}}
                .btn-primary{{background-image:linear-gradient(135deg,#6366F1,#A855F7); color:#fff}}
                .btn-primary:hover{{filter:brightness(1.05)}}
            </style>
        </head>
        <body class="relative bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 text-slate-800 min-h-screen">
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

            <main class="max-w-5xl mx-auto px-4 py-6 sm:py-8 pb-24">
                <div class="bg-white rounded-xl shadow-sm p-6">
                    <div class="flex items-center space-x-6 mb-8">
                        <div id="avatar-box" class="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center overflow-hidden">
                            {f'<img src="{current_user.avatar_url}" class="w-20 h-20 rounded-full object-cover" alt="Avatar" />' if current_user.avatar_url else f'<span class="text-2xl font-bold text-white">{current_user.name[0].upper()}</span>'}
                        </div>
                        <div>
                            <h1 class="text-3xl font-bold">{current_user.name}</h1>
                            <p class="text-slate-600">{current_user.email}</p>
                            <div class="flex items-center space-x-4 mt-2">
                                <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">Level {current_user.level}</span>
                                <span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">{current_user.xp} XP</span>
                            </div>
                        </div>
                    </div>

                    <form method="post" action="/profile/update" class="space-y-6">
                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-2">Name</label>
                            <input name="name" type="text" value="{current_user.name}" 
                                   class="w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-2">Email</label>
                            <input name="email" type="email" value="{current_user.email}" 
                                   class="w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-2">Avatar</label>
                            <input id="avatar-file" type="file" accept="image/*" 
                                   class="w-full border border-slate-300 rounded-lg px-4 py-2 bg-white" />
                            <input id="avatar-url" name="avatar_url" type="hidden" value="{current_user.avatar_url or ''}" />
                            <p class="mt-1 text-xs text-slate-500">Pilih gambar untuk diunggah. Perubahan disimpan saat menekan Update Profile.</p>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-2">Profile Bio</label>
                            <textarea name="profile" rows="4" placeholder="Tell us about yourself..."
                                      class="w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500">{current_user.profile or ''}</textarea>
                        </div>

                        <div class="flex space-x-4">
                            <button type="submit" class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                                Update Profile
                            </button>
                            <a href="/dashboard" class="px-6 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 font-medium">
                                Cancel
                            </a>
                        </div>
                    </form>
                </div>

                <!-- Change Password -->
                <div class="bg-white rounded-xl shadow-sm p-6 mt-6">
                    <h2 class="text-xl font-semibold mb-4">Change Password</h2>
                    <form method="post" action="/profile/password" class="grid gap-4 sm:grid-cols-2">
                        <div class="sm:col-span-2">
                            <label class="block text-sm font-medium text-slate-700 mb-2">Current Password</label>
                            <input name="current_password" type="password" required class="w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-2">New Password</label>
                            <input name="new_password" type="password" minlength="8" required class="w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-2">Confirm New Password</label>
                            <input name="confirm_password" type="password" minlength="8" required class="w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
                        </div>
                        <div class="sm:col-span-2">
                            <button type="submit" class="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium">Update Password</button>
                        </div>
                    </form>
                </div>

                <!-- Your Posts -->
                <div class="bg-white rounded-xl shadow-sm p-6 mt-6">
                    <h2 class="text-xl font-semibold mb-4">Your Posts</h2>
                    <div id="my-posts-list" class="space-y-3">
                        <div class="text-slate-600 text-sm">Memuat postingan…</div>
                    </div>
                </div>
            </main>

            <!-- Floating chat button -->
            <a href="/dm" class="fixed bottom-20 right-4 sm:right-8 z-40 inline-flex items-center justify-center w-14 h-14 rounded-full btn-primary shadow-xl">💬</a>
            <!-- Mobile bottom nav -->
            <nav class="sm:hidden fixed bottom-0 inset-x-0 bg-white/80 backdrop-blur-md border-t border-slate-200/60 shadow-lg">
                <div class="max-w-5xl mx-auto grid grid-cols-5">
                    <a href="/dashboard" class="flex flex-col items-center justify-center py-3 text-[11px] text-slate-700 hover:bg-white/60">Home</a>
                    <a href="/habits" class="flex flex-col items-center justify-center py-3 text-[11px] text-slate-700 hover:bg-white/60">Habits</a>
                    <a href="/community" class="flex flex-col items-center justify-center py-3 text-[11px] text-slate-700 hover:bg-white/60">Community</a>
                    <a href="/coach" class="flex flex-col items-center justify-center py-3 text-[11px] text-slate-700 hover:bg-white/60">Coach</a>
                    <a href="/profile" class="flex flex-col items-center justify-center py-3 text-[11px] text-slate-700 hover:bg-white/60">Profile</a>
                </div>
            </nav>
            """
            + """
            <script>
              (function(){
                const fileInput = document.getElementById('avatar-file');
                if(fileInput){
                  fileInput.addEventListener('change', async () => {
                    const f = fileInput.files && fileInput.files[0];
                    if(!f) return;
                    try{
                      const btns = document.querySelectorAll('button[type="submit"]');
                      btns.forEach(b=>{ b.dataset._origText=b.textContent; b.disabled=true; b.textContent='Uploading…'; });
                      const fd = new FormData(); fd.append('file', f);
                      const res = await fetch('/api/uploads/image', { method:'POST', credentials:'include', body: fd });
                      if(!res.ok){
                        const err = await res.json().catch(()=>({detail:''}));
                        alert('Gagal mengunggah avatar: ' + (err.detail || res.status));
                        return;
                      }
                      const data = await res.json();
                      const urlInput = document.getElementById('avatar-url');
                      if(urlInput) urlInput.value = data.url;
                      const box = document.getElementById('avatar-box');
                      if(box) box.innerHTML = `<img src="${data.url}" class="w-20 h-20 rounded-full object-cover" alt="Avatar" />`;
                    }catch(e){
                      alert('Network error saat upload avatar: ' + ((e && e.message) || e));
                    }finally{
                      const btns = document.querySelectorAll('button[type="submit"]');
                      btns.forEach(b=>{ if(b.dataset._origText){ b.textContent=b.dataset._origText; b.disabled=false; delete b.dataset._origText; }});
                    }
                  });
                }

                // Load user's posts
                async function loadMyPosts(){
                  const wrap = document.getElementById('my-posts-list');
                  if(!wrap) return;
                  try{
                    const res = await fetch('/api/posts/me', { credentials: 'include' });
                    if(!res.ok){
                      const t = await res.text().catch(()=> '');
                      throw new Error('Gagal memuat postingan ('+res.status+') '+t);
                    }
                    const items = await res.json();
                    if(!items || !items.length){
                      wrap.innerHTML = '<div class="text-slate-600 text-sm">Belum ada postingan.</div>';
                      return;
                    }
                    function avatarHtml(u){
                      if(u && u.avatar_url){ return `<img src="${u.avatar_url}" class="w-9 h-9 rounded-full object-cover"/>`; }
                      const n = (u && u.name ? u.name : '?').slice(0,1).toUpperCase();
                      return `<div class=\"w-9 h-9 rounded-full bg-indigo-200 flex items-center justify-center text-xs text-indigo-800\">${n}</div>`;
                    }
                    function card(p){
                      return `
                        <div class=\"rounded-2xl glass p-4 border border-white/20 ring-1 ring-white/10\" data-post-id=\"${p.id}\"> 
                          <div class=\"flex items-center gap-3 mb-2\"> 
                            ${avatarHtml(p.user)}
                            <div>
                              <div class=\"text-sm font-medium\">${(p.user && p.user.name) || 'You'} </div>
                              <div class=\"text-xs text-slate-500\">${new Date(p.created_at).toLocaleString()}</div>
                            </div>
                          </div>
                          ${p.content ? `<div class=\\"text-sm\\">${p.content}</div>` : ''}
                          ${p.image_url ? `<img src=\\"${p.image_url}\\" class=\\"mt-2 rounded-lg max-h-72 object-cover w-full\\"/>` : ''}
                          <div class=\"mt-3 flex items-center gap-4 text-sm text-slate-600\"> 
                            <button class=\"btn-like ${p.you_liked? "text-indigo-600 font-medium":""}\">❤️ ${p.like_count} </button>
                            <button class=\"btn-comment\">💬 ${p.comment_count} </button>
                            <button class=\"btn-share\">↗️ Share</button>
                          </div>
                          <div class=\"comments mt-3 hidden\">
                            <div class=\"comments-list space-y-2 text-sm\"></div>
                            <div class=\"flex gap-2 mt-2\"> 
                              <input class=\"comment-input flex-1 border rounded px-2 py-1 text-sm\" placeholder=\"Tulis komentar...\"/>
                              <button class=\"btn-send-comment px-3 py-1.5 rounded-lg btn-primary text-sm\">Kirim</button>
                            </div>
                          </div>
                        </div>`;
                    }
                    wrap.innerHTML = items.map(card).join('');
                    // Bind events like in community feed
                    wrap.querySelectorAll('[data-post-id]').forEach(card => {
                      const postId = card.getAttribute('data-post-id');
                      card.querySelector('.btn-like').addEventListener('click', async () => {
                        const liked = card.querySelector('.btn-like').classList.contains('text-indigo-600');
                        const method = liked ? 'DELETE' : 'POST';
                        try {
                          const res = await fetch(`/api/posts/${postId}/like`, { method, credentials: 'include' });
                          if(res.ok) { loadMyPosts(); }
                          else { const err = await res.json().catch(()=>({detail:''})); alert('Gagal memproses like: ' + (err.detail || res.status)); }
                        } catch (e) { alert('Network error saat like: ' + ((e&&e.message)||e)); }
                      });
                      card.querySelector('.btn-comment').addEventListener('click', async () => {
                        const box = card.querySelector('.comments');
                        box.classList.toggle('hidden');
                        if(!box.classList.contains('hidden')){
                          try {
                            const res = await fetch(`/api/posts/${postId}/comments`, { credentials: 'include' });
                            if(res.ok){
                              const comments = await res.json();
                              const list = card.querySelector('.comments-list');
                              list.innerHTML = comments.map(c=>`<div><span class=\\"font-medium\\">${c.user.name} </span> <span class=\\"text-slate-500 text-xs\\">${new Date(c.created_at).toLocaleString()} </span><div>${c.content} </div></div>`).join('');
                            } else { const err = await res.json().catch(()=>({detail:''})); alert('Gagal memuat komentar: ' + (err.detail || res.status)); }
                          } catch (e) { alert('Network error saat memuat komentar: ' + ((e&&e.message)||e)); }
                        }
                      });
                      card.querySelector('.btn-send-comment').addEventListener('click', async () => {
                        const input = card.querySelector('.comment-input');
                        const content = input.value.trim(); if(!content) return;
                        try {
                          const res = await fetch(`/api/posts/${postId}/comments`, { method:'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'include', body: JSON.stringify({ content }) });
                          if(res.ok){ input.value=''; card.querySelector('.btn-comment').click(); }
                          else { const err = await res.json().catch(()=>({detail:''})); alert('Gagal mengirim komentar: ' + (err.detail || res.status)); }
                        } catch (e) { alert('Network error saat mengirim komentar: ' + ((e&&e.message)||e)); }
                      });
                      card.querySelector('.btn-share').addEventListener('click', async () => {
                        const url = `${window.location.origin}${'/profile'}#post-${postId}`;
                        if(navigator.share){ try{ await navigator.share({ title:'HabitVerse', url }); }catch(_){}}
                        else{ navigator.clipboard.writeText(url); alert('Link disalin'); }
                      });
                    });
                  }catch(e){
                    const wrap = document.getElementById('my-posts-list');
                    if(wrap){ wrap.innerHTML = '<div class=\"text-slate-600 text-sm\">Gagal memuat postingan.</div>'; }
                  }
                }
                loadMyPosts();
              })();
            </script>
            """
            + f"""
        </body>
        </html>
        """
    )

@router.post("/profile/update")
def update_profile(
    name: str = Form(...),
    email: str = Form(...),
    avatar_url: str = Form(""),
    profile: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if email is already taken by another user
    if email != current_user.email:
        existing_user = db.query(User).filter(User.email == email, User.id != current_user.id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already taken")
    
    # Update user profile
    current_user.name = name
    current_user.email = email
    current_user.avatar_url = avatar_url if avatar_url else None
    current_user.profile = profile if profile else None
    
    db.commit()
    return RedirectResponse(url="/profile", status_code=302)


@router.post("/profile/password")
def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate current password
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # Validate new password
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirmation do not match")

    # Update password hash
    current_user.password_hash = get_password_hash(new_password)
    current_user.updated_at = current_user.updated_at  # trigger update
    db.commit()
    return RedirectResponse(url="/profile", status_code=302)
