# app/routes/community.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.db.models import User, Challenge, ChallengeMember

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
      <main class="max-w-5xl mx-auto px-4 py-6 sm:py-8 pb-24">{body}</main>
      <!-- Floating chat button -->
      <a href="/dm" class="fixed bottom-20 right-4 sm:right-8 z-40 inline-flex items-center justify-center w-14 h-14 rounded-full btn-primary shadow-xl">
        💬
      </a>
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
      <footer class=\"py-8 text-center text-sm text-slate-500\">Grow together • Join a challenge ✨</footer>
    </body>
    </html>
    """


@router.get("/community", response_class=HTMLResponse)
async def community(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Community page with challenges and leaderboard placeholders"""
    
    # Fetch real challenges from database
    challenges = db.query(Challenge).filter(
        Challenge.is_public == True
    ).order_by(Challenge.created_at.desc()).limit(8).all()
    
    # Build challenge cards with user-specific buttons
    trending_cards = ""
    if challenges:
        for challenge in challenges:
            is_owner = challenge.owner_id == current_user.id
            # Check if user is already a member
            is_member = db.query(ChallengeMember).filter(
                ChallengeMember.challenge_id == challenge.id,
                ChallengeMember.user_id == current_user.id
            ).first() is not None
            
            # Determine button to show
            if is_owner:
                button = f'<button onclick="editChallenge(\'{challenge.id}\')" class="px-3 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600">Edit</button>'
            elif is_member:
                button = '<span class="px-3 py-1 text-xs bg-green-100 text-green-700 rounded">Joined</span>'
            else:
                button = f'<button onclick="joinChallenge(\'{challenge.id}\')" class="px-3 py-1 text-xs bg-indigo-500 text-white rounded hover:bg-indigo-600">Join</button>'
            
            trending_cards += f'''
            <div class="block p-4 rounded-2xl glass backdrop-blur-xl border border-white/20 shadow-lg ring-1 ring-white/10 hover:shadow-xl transition">
                <div class="flex justify-between items-start mb-2">
                    <div class="font-medium">{challenge.name}</div>
                    {button}
                </div>
                <div class="text-sm text-slate-600">{challenge.member_count} peserta • {challenge.reward_xp} XP</div>
                <div class="text-xs text-slate-500 mt-1">{"Public" if challenge.is_public else "Private"}</div>
                {f'<div class="text-xs text-slate-400 mt-1">{challenge.description[:50]}...</div>' if challenge.description else ''}
            </div>
            '''
    else:
        trending_cards = '<p class="text-slate-500 text-center py-8">No challenges yet. Create the first one!</p>'

    leaderboard = ''.join([
        f'<div class="p-3 flex items-center justify-between"><div class="flex items-center gap-3"><div class="w-7 h-7 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-sm">{i}</div><div><div class="text-sm font-medium">{name}</div><div class="text-xs text-slate-500">{xp} XP</div></div></div><div class="text-sm text-slate-500">{streak}🔥</div></div>'
        for i,(name,xp,streak) in enumerate([(current_user.name, 1200, 21),("Alya",1100,16),("Budi",980,12),("Sari",860,10)], start=1)
    ])

    # Build body without f-strings to avoid JS brace conflicts
    body = (
        """
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold">Community</h1>
          <p class="text-slate-600">Ikuti tantangan dan naik ke leaderboard.</p>
        </div>
        <button id="btn-create-challenge" class="px-4 py-2 rounded-lg btn-primary shadow-sm">Buat Challenge</button>
      </div>

      <!-- Create Challenge Modal -->
      <div id="modal-create-challenge" class="hidden fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/40"></div>
        <div class="relative z-10 w-full max-w-md mx-auto p-6 rounded-2xl bg-white shadow-2xl">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-lg font-semibold">Buat Challenge Baru</h3>
            <button id="btn-close-create" class="text-slate-500 hover:text-slate-700">✕</button>
          </div>
          <div class="space-y-3">
            <div class="mb-4">
              <label class="block text-sm font-medium mb-2">Community (optional for public challenges)</label>
              <select id="community-id" class="w-full border rounded-lg px-3 py-2">
                <option value="">No community (public challenge only)</option>
              </select>
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium mb-2">Challenge Name</label>
              <input id="challenge-name" class="w-full border rounded-lg px-3 py-2" placeholder="Challenge name" required />
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium mb-2">Description</label>
              <textarea id="challenge-description" class="w-full border rounded-lg px-3 py-2" placeholder="Challenge description"></textarea>
            </div>
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label class="block text-sm font-medium mb-2">Start Date</label>
                <input id="start-date" type="date" class="w-full border rounded-lg px-3 py-2" required />
              </div>
              <div>
                <label class="block text-sm font-medium mb-2">End Date</label>
                <input id="end-date" type="date" class="w-full border rounded-lg px-3 py-2" required />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label class="block text-sm font-medium mb-2">Reward XP</label>
                <input id="reward-xp" type="number" class="w-full border rounded-lg px-3 py-2" value="50" min="1" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-2">Max Members</label>
                <input id="max-members" type="number" class="w-full border rounded-lg px-3 py-2" placeholder="Optional" min="1" />
              </div>
            </div>
            <div class="mb-4">
              <label class="flex items-center">
                <input id="is-public" type="checkbox" class="mr-2" />
                <span class="text-sm">Public challenge (anyone can join)</span>
              </label>
            </div>
            <button id="btn-submit-create" class="w-full mt-2 px-4 py-2 rounded-lg btn-primary">Buat</button>
          </div>
        </div>
      </div>

      <!-- Edit Challenge Modal -->
      <div id="modal-edit-challenge" class="hidden fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/40"></div>
        <div class="relative z-10 w-full max-w-md mx-auto p-6 rounded-2xl bg-white shadow-2xl">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-lg font-semibold">Edit Challenge</h3>
            <button id="btn-cancel-edit" class="text-slate-500 hover:text-slate-700">✕</button>
          </div>
          <form id="form-edit-challenge" class="space-y-3">
            <input id="edit-challenge-id" type="hidden" />
            <div class="mb-4">
              <label class="block text-sm font-medium mb-2">Challenge Name</label>
              <input id="edit-challenge-name" class="w-full border rounded-lg px-3 py-2" placeholder="Challenge name" required />
            </div>
            <div class="mb-4">
              <label class="block text-sm font-medium mb-2">Description</label>
              <textarea id="edit-challenge-description" class="w-full border rounded-lg px-3 py-2" placeholder="Challenge description"></textarea>
            </div>
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label class="block text-sm font-medium mb-2">Start Date</label>
                <input id="edit-start-date" type="date" class="w-full border rounded-lg px-3 py-2" required />
              </div>
              <div>
                <label class="block text-sm font-medium mb-2">End Date</label>
                <input id="edit-end-date" type="date" class="w-full border rounded-lg px-3 py-2" required />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label class="block text-sm font-medium mb-2">Reward XP</label>
                <input id="edit-reward-xp" type="number" class="w-full border rounded-lg px-3 py-2" value="50" min="1" />
              </div>
              <div>
                <label class="block text-sm font-medium mb-2">Max Members</label>
                <input id="edit-max-members" type="number" class="w-full border rounded-lg px-3 py-2" placeholder="Optional" min="1" />
              </div>
            </div>
            <div class="mb-4">
              <label class="flex items-center">
                <input id="edit-is-public" type="checkbox" class="mr-2" />
                <span class="text-sm">Public challenge (anyone can join)</span>
              </label>
            </div>
            <button id="btn-submit-edit" class="w-full mt-2 px-4 py-2 rounded-lg btn-primary">Simpan</button>
          </form>
        </div>
      </div>

      <div class="mt-6 space-y-8">
        <!-- Trending at top -->
        <section class="space-y-3">
          <h2 class="text-lg font-semibold">Trending Challenges</h2>
          <div class="grid gap-3 sm:grid-cols-2">
        """
        + trending_cards +
        """
          </div>
        </section>

        <!-- Composer -->
        <section class="space-y-2">
          <div class="rounded-2xl glass p-4">
            <div class="flex flex-col sm:flex-row gap-2">
              <input id="composer-content" class="flex-1 border rounded px-3 py-2" placeholder="Bagikan progres atau pikiranmu..."/>
              <input id="composer-file" type="file" accept="image/*" class="sm:w-72 border rounded px-3 py-2 bg-white"/>
              <button id="btn-post" class="px-4 py-2 rounded-lg btn-primary">Post</button>
            </div>
          </div>
        </section>

        <!-- Feed list -->
        <div id="feed-list" class="space-y-3"></div>
      </section>

      <!-- Leaderboard below feed -->
      <section class="space-y-3">
        <h2 class="text-lg font-semibold">Leaderboard Minggu Ini</h2>
        <div class="rounded-2xl glass backdrop-blur-xl border border-white/20 shadow-lg ring-1 ring-white/10 divide-y divide-white/30">
"""
        + leaderboard +
        """
        </div>
      </section>
    </div>

    <script>
      const $ = (q) => document.querySelector(q);
      document.querySelector('#btn-create-challenge').addEventListener('click', async () => {
        // Load user's communities for dropdown
        try {
          const res = await fetch('/api/challenges/user/communities', {
            method: 'GET',
            credentials: 'include'
          });
          if (res.ok) {
            const communities = await res.json();
            const select = document.querySelector('#community-id');
            select.innerHTML = '<option value="">No community (public challenge only)</option>';
            
            communities.forEach(community => {
              const option = document.createElement('option');
              option.value = community.id;
              option.textContent = `${community.name}`;
              select.appendChild(option);
            });
          } else {
            console.error('Failed to load communities:', res.status);
            const select = document.querySelector('#community-id');
            select.innerHTML = '<option value="">No community (public challenge only)</option>';
          }
        } catch (error) {
          console.error('Failed to load communities:', error);
          const select = document.querySelector('#community-id');
          select.innerHTML = '<option value="">No community (public challenge only)</option>';
        }
        
        document.querySelector('#modal-create-challenge').classList.remove('hidden');
      });

      document.querySelector('#btn-close-create').addEventListener('click', () => {
        document.querySelector('#modal-create-challenge').classList.add('hidden');
      });

      document.querySelector('#btn-submit-create').addEventListener('click', async () => {
        const communityId = document.querySelector('#community-id').value.trim();
        const name = document.querySelector('#challenge-name').value.trim();
        const start = document.querySelector('#start-date').value;
        const end = document.querySelector('#end-date').value;
        const desc = document.querySelector('#challenge-description').value.trim();
        const reward = document.querySelector('#reward-xp').value || 50;
        const maxMembers = document.querySelector('#max-members').value || null;
        const isPublic = document.querySelector('#is-public').checked;

        console.log('Form values:', { communityId, name, start, end, desc, reward, maxMembers, isPublic });

        // Only require community for private challenges
        if (!isPublic && !communityId) {
          alert('Private challenges require a community selection');
          return;
        }

        if (!name || !start || !end) {
          alert('Please fill in Name, Start Date, and End Date');
          return;
        }

        const params = new URLSearchParams({ 
          name, 
          start_date: start, 
          end_date: end,
          reward_xp: String(reward),
          is_public: String(isPublic)
        });
        if (desc) params.append('description', desc);
        if (maxMembers) params.append('max_members', String(maxMembers));
        if (communityId) params.append('community_id', communityId);

        try {
          const res = await fetch('/api/challenges/create?' + params.toString(), {
            method: 'POST',
            credentials: 'include'
          });

          if (res.ok) {
            alert('Challenge created successfully!');
            document.querySelector('#modal-create-challenge').classList.add('hidden');
            location.reload();
          } else {
            const error = await res.json();
            alert('Failed to create challenge: ' + (error.detail || 'Unknown error'));
          }
        } catch (error) {
          alert('Network error: ' + error.message);
        }
      });

      // Join Challenge Function
      window.joinChallenge = async function(challengeId) {
        try {
          const res = await fetch(`/api/challenges/${challengeId}/join`, {
            method: 'POST',
            credentials: 'include'
          });

          if (res.ok) {
            alert('Successfully joined challenge!');
            location.reload();
          } else {
            const error = await res.json();
            alert('Failed to join challenge: ' + (error.detail || 'Unknown error'));
          }
        } catch (error) {
          alert('Network error: ' + error.message);
        }
      };

      // Edit Challenge Function
      window.editChallenge = async function(challengeId) {
        try {
          // Fetch challenge details
          const res = await fetch(`/api/challenges/${challengeId}/details`, {
            method: 'GET',
            credentials: 'include'
          });

          if (res.ok) {
            const challenge = await res.json();
            
            // Populate edit form
            document.querySelector('#edit-challenge-id').value = challenge.id;
            document.querySelector('#edit-challenge-name').value = challenge.name;
            document.querySelector('#edit-challenge-description').value = challenge.description || '';
            document.querySelector('#edit-start-date').value = challenge.start_date;
            document.querySelector('#edit-end-date').value = challenge.end_date;
            document.querySelector('#edit-reward-xp').value = challenge.reward_xp;
            document.querySelector('#edit-max-members').value = challenge.max_members || '';
            document.querySelector('#edit-is-public').checked = challenge.is_public;
            
            // Show modal
            document.querySelector('#modal-edit-challenge').classList.remove('hidden');
          } else {
            const error = await res.json();
            alert('Failed to load challenge details: ' + (error.detail || 'Unknown error'));
          }
        } catch (error) {
          alert('Network error: ' + error.message);
        }
      };

      document.querySelector('#btn-cancel-edit').addEventListener('click', () => {
        document.querySelector('#modal-edit-challenge').classList.add('hidden');
      });

      document.querySelector('#form-edit-challenge').addEventListener('submit', async (e) => {
        e.preventDefault();
        const challengeId = document.querySelector('#edit-challenge-id').value;
        const name = document.querySelector('#edit-challenge-name').value.trim();
        const start = document.querySelector('#edit-start-date').value;
        const end = document.querySelector('#edit-end-date').value;
        const desc = document.querySelector('#edit-challenge-description').value.trim();
        const reward = document.querySelector('#edit-reward-xp').value || 50;
        const maxMembers = document.querySelector('#edit-max-members').value || null;
        const isPublic = document.querySelector('#edit-is-public').checked;

        if (!name || !start || !end) {
          alert('Please fill in Name, Start Date, and End Date');
          return;
        }

        const params = new URLSearchParams({ 
          name, 
          start_date: start, 
          end_date: end,
          reward_xp: String(reward),
          is_public: String(isPublic)
        });
        if (desc) params.append('description', desc);
        if (maxMembers) params.append('max_members', String(maxMembers));

        try {
          const res = await fetch(`/api/challenges/${challengeId}/edit?${params.toString()}`, {
            method: 'PUT',
            credentials: 'include'
          });

          if (res.ok) {
            alert('Challenge updated successfully!');
            document.querySelector('#modal-edit-challenge').classList.add('hidden');
            location.reload();
          } else {
            const error = await res.json();
            alert('Failed to update challenge: ' + (error.detail || 'Unknown error'));
          }
        } catch (error) {
          alert('Network error: ' + error.message);
        }
      });

      // Feed logic
      async function loadFeed() {
        try {
          const res = await fetch('/api/posts/feed', { credentials: 'include' });
          if (!res.ok) {
            const txt = await res.text().catch(()=> '');
            throw new Error(`Failed to load feed (${res.status}) ${txt || ''}`);
          }
          const data = await res.json();
          renderFeed(data);
        } catch (e) {
          document.querySelector('#feed-list').innerHTML = `<div class=\"rounded-2xl glass p-4\">Gagal memuat feed. <button class=\"ml-2 px-2 py-1 text-sm rounded border\" onclick=\"loadFeed()\">Coba lagi</button><div class=\"mt-1 text-xs text-slate-500\">${(e&&e.message)||''}</div></div>`;
        }
      }

      function avatarHtml(u){
        if(u.avatar_url){return `<img src="${u.avatar_url}" class="w-9 h-9 rounded-full object-cover"/>`}
        return `<div class=\"w-9 h-9 rounded-full bg-indigo-200 flex items-center justify-center text-xs text-indigo-800\">${(u.name||'?').slice(0,1).toUpperCase()}</div>`
      }

      function postHtml(p){
        return `
          <div class="rounded-2xl glass p-4 border border-white/20 ring-1 ring-white/10" data-post-id="${p.id}">
            <div class="flex items-center gap-3 mb-2">
              <a href="/u/${p.user.id}">${avatarHtml(p.user)}</a>
              <div>
                <div class="text-sm font-medium"><a href="/u/${p.user.id}" class="hover:underline">${p.user.name}</a></div>
                <div class="text-xs text-slate-500">${new Date(p.created_at).toLocaleString()}</div>
              </div>
            </div>
            ${p.content ? `<div class=\"text-sm\">${p.content}</div>` : ''}
            ${p.image_url ? `<img src=\"${p.image_url}\" class=\"mt-2 rounded-lg max-h-72 object-cover w-full\"/>` : ''}
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

      function renderFeed(items){
        const wrap = document.querySelector('#feed-list');
        if(!items || !items.length){
          wrap.innerHTML = `<div class=\"rounded-2xl glass p-4 text-sm text-slate-600\">Belum ada postingan.</div>`; return;
        }
        wrap.innerHTML = items.map(postHtml).join('');

        // bind events
        wrap.querySelectorAll('[data-post-id]').forEach(card => {
          const postId = card.getAttribute('data-post-id');
          card.querySelector('.btn-like').addEventListener('click', async () => {
            const liked = card.querySelector('.btn-like').classList.contains('text-indigo-600');
            const method = liked ? 'DELETE' : 'POST';
            try {
              const res = await fetch(`/api/posts/${postId}/like`, { method, credentials: 'include' });
              if(res.ok) { loadFeed(); }
              else {
                const err = await res.json().catch(()=>({detail:''}));
                alert('Gagal memproses like: ' + (err.detail || res.status));
              }
            } catch (e) {
              alert('Network error saat like: ' + (e&&e.message||e));
            }
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
                  list.innerHTML = comments.map(c=>`<div><span class=\"font-medium\">${c.user.name}</span> <span class=\"text-slate-500 text-xs\">${new Date(c.created_at).toLocaleString()}</span><div>${c.content}</div></div>`).join('');
                } else {
                  const err = await res.json().catch(()=>({detail:''}));
                  alert('Gagal memuat komentar: ' + (err.detail || res.status));
                }
              } catch (e) {
                alert('Network error saat memuat komentar: ' + (e&&e.message||e));
              }
            }
          });
          card.querySelector('.btn-send-comment').addEventListener('click', async () => {
            const input = card.querySelector('.comment-input');
            const content = input.value.trim();
            if(!content) return;
            try {
              const res = await fetch(`/api/posts/${postId}/comments`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ content })
              });
              if(res.ok){ input.value=''; card.querySelector('.btn-comment').click(); }
              else {
                const err = await res.json().catch(()=>({detail:''}));
                alert('Gagal mengirim komentar: ' + (err.detail || res.status));
              }
            } catch (e) {
              alert('Network error saat mengirim komentar: ' + (e&&e.message||e));
            }
          });
        });
      }

      document.querySelector('#btn-post').addEventListener('click', async ()=>{
        const content = document.querySelector('#composer-content').value.trim();
        const fileInput = document.querySelector('#composer-file');
        const file = fileInput && fileInput.files && fileInput.files[0] ? fileInput.files[0] : null;
        if(!content && !file){ alert('Tulis sesuatu atau unggah gambar.'); return; }
        try {
          const btn = document.querySelector('#btn-post');
          btn.disabled = true; btn.textContent = 'Posting…';
          let image_url = null;
          if (file) {
            const fd = new FormData();
            fd.append('file', file);
            const up = await fetch('/api/uploads/image', { method:'POST', credentials:'include', body: fd });
            if(!up.ok){
              const err = await up.json().catch(()=>({detail:''}));
              throw new Error('Gagal mengunggah gambar: ' + (err.detail || up.status));
            }
            const uploaded = await up.json();
            image_url = uploaded.url;
          }
          const res = await fetch('/api/posts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ content, image_url })
          });
          if(res.ok){
            document.querySelector('#composer-content').value='';
            if(fileInput) fileInput.value='';
            loadFeed();
          } else {
            const err = await res.json().catch(()=>({detail:''}));
            alert('Gagal membuat postingan: ' + (err.detail || res.status));
          }
        } catch (e) {
          alert('Network error saat membuat postingan: ' + (e&&e.message||e));
        } finally {
          const btn = document.querySelector('#btn-post');
          btn.disabled = false; btn.textContent = 'Post';
        }
      });

      loadFeed();
    </script>
"""
    )

    return HTMLResponse(content=page_shell("Community", body))
