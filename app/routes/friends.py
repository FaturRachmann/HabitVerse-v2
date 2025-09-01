from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.db.models import User

router = APIRouter()

@router.get("/friends", response_class=HTMLResponse)
def friends_page(
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
            <title>Friends - HabitVerse</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-slate-50 min-h-screen">
            <nav class="bg-white shadow-sm border-b px-6 py-4">
                <div class="flex items-center justify-between max-w-6xl mx-auto">
                    <div class="flex items-center space-x-8">
                        <h1 class="text-xl font-bold text-blue-600">HabitVerse</h1>
                        <div class="flex space-x-6">
                            <a href="/dashboard" class="text-slate-600 hover:text-blue-600">Dashboard</a>
                            <a href="/habits" class="text-slate-600 hover:text-blue-600">Habits</a>
                            <a href="/community" class="text-slate-600 hover:text-blue-600">Community</a>
                            <a href="/friends" class="text-blue-600 font-medium">Friends</a>
                            <a href="/profile" class="text-slate-600 hover:text-blue-600">Profile</a>
                        </div>
                    </div>
                    <div class="flex items-center space-x-4">
                        <span class="text-sm text-slate-600">Level {current_user.level}</span>
                        <span class="text-sm text-slate-600">{current_user.xp} XP</span>
                        <a href="/auth/logout" class="text-sm text-red-600 hover:text-red-700">Logout</a>
                    </div>
                </div>
            </nav>

            <div class="max-w-6xl mx-auto p-6">
                <div class="flex items-center justify-between mb-6">
                    <div>
                        <h1 class="text-2xl font-semibold">Friends</h1>
                        <p class="text-slate-600">Connect with other HabitVerse users</p>
                    </div>
                    <button id="btn-search-users" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                        Find Friends
                    </button>
                </div>

                <!-- Friend Requests Section -->
                <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
                    <h2 class="text-lg font-semibold mb-4">Friend Requests</h2>
                    <div id="friend-requests" class="space-y-3">
                        <p class="text-slate-500">Loading friend requests...</p>
                    </div>
                </div>

                <!-- Friends List Section -->
                <div class="bg-white rounded-xl shadow-sm p-6">
                    <h2 class="text-lg font-semibold mb-4">Your Friends</h2>
                    <div id="friends-list" class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        <p class="text-slate-500">Loading friends...</p>
                    </div>
                </div>
            </div>

            <!-- Search Users Modal -->
            <div id="modal-search-users" class="hidden fixed inset-0 z-50 flex items-center justify-center">
                <div class="absolute inset-0 bg-black/40"></div>
                <div class="relative z-10 w-full max-w-2xl mx-auto p-6 rounded-2xl bg-white shadow-2xl">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-lg font-semibold">Find Friends</h3>
                        <button id="btn-close-search" class="text-slate-500 hover:text-slate-700">✕</button>
                    </div>
                    
                    <div class="mb-4">
                        <input id="search-input" type="text" placeholder="Search by name or email..." 
                               class="w-full border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500" />
                    </div>
                    
                    <div id="search-results" class="max-h-96 overflow-y-auto space-y-3">
                        <p class="text-slate-500 text-center py-8">Enter at least 2 characters to search</p>
                    </div>
                </div>
            </div>

            <script>
                // Load friend requests
                async function loadFriendRequests() {{
                    try {{
                        const res = await fetch('/api/friends/requests', {{ credentials: 'include' }});
                        if (res.ok) {{
                            const requests = await res.json();
                            const container = document.getElementById('friend-requests');
                            
                            if (requests.length === 0) {{
                                container.innerHTML = '<p class="text-slate-500">No pending friend requests</p>';
                                return;
                            }}
                            
                            container.innerHTML = requests.map(req => `
                                <div class="flex items-center justify-between p-4 border rounded-lg">
                                    <a href="/u/${{req.requester.id}}" class="flex items-center space-x-3 group">
                                        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                                            ${{req.requester.avatar_url ? 
                                                `<img src="${{req.requester.avatar_url}}" class="w-10 h-10 rounded-full object-cover" />` :
                                                `<span class="text-white font-medium">${{req.requester.name[0].toUpperCase()}}</span>`
                                            }}
                                        </div>
                                        <div>
                                            <p class="font-medium group-hover:underline">${{req.requester.name}}</p>
                                            <p class="text-sm text-slate-600">Level ${{req.requester.level}} • ${{req.requester.xp}} XP</p>
                                        </div>
                                    </a>
                                    <div class="flex space-x-2">
                                        <button onclick="acceptFriendRequest('${{req.friendship_id}}')" 
                                                class="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700">
                                            Accept
                                        </button>
                                        <button onclick="rejectFriendRequest('${{req.friendship_id}}')" 
                                                class="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700">
                                            Reject
                                        </button>
                                    </div>
                                </div>
                            `).join('');
                        }}
                    }} catch (error) {{
                        console.error('Failed to load friend requests:', error);
                    }}
                }}

                // Load friends list
                async function loadFriends() {{
                    try {{
                        const res = await fetch('/api/friends', {{ credentials: 'include' }});
                        if (res.ok) {{
                            const friends = await res.json();
                            const container = document.getElementById('friends-list');
                            
                            if (friends.length === 0) {{
                                container.innerHTML = '<p class="text-slate-500 col-span-full text-center py-8">No friends yet. Start by finding some friends!</p>';
                                return;
                            }}
                            
                            container.innerHTML = friends.map(friend => `
                                <div class="p-4 border rounded-lg hover:shadow-md transition-shadow">
                                    <a href="/u/${{friend.id}}" class="flex items-center space-x-3 mb-3 group">
                                        <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                                            ${{friend.avatar_url ? 
                                                `<img src="${{friend.avatar_url}}" class="w-12 h-12 rounded-full object-cover" />` :
                                                `<span class="text-white font-medium">${{friend.name[0].toUpperCase()}}</span>`
                                            }}
                                        </div>
                                        <div>
                                            <p class="font-medium group-hover:underline">${{friend.name}}</p>
                                            <p class="text-sm text-slate-600">Level ${{friend.level}} • ${{friend.xp}} XP</p>
                                        </div>
                                    </a>
                                    ${{friend.profile ? `<p class="text-sm text-slate-600 mb-2">${{friend.profile}}</p>` : ''}}
                                    <div class="flex items-center gap-4">
                                      <a href="/dm?to=${{friend.id}}" class="text-sm text-indigo-600 hover:text-indigo-700">Message</a>
                                      <button onclick="removeFriend('${{friend.id}}')" 
                                              class="text-sm text-red-600 hover:text-red-700">
                                          Remove Friend
                                      </button>
                                    </div>
                                </div>
                            `).join('');
                        }}
                    }} catch (error) {{
                        console.error('Failed to load friends:', error);
                    }}
                }}

                // Search users
                let searchTimeout;
                document.getElementById('search-input').addEventListener('input', (e) => {{
                    clearTimeout(searchTimeout);
                    const query = e.target.value.trim();
                    
                    if (query.length < 2) {{
                        document.getElementById('search-results').innerHTML = 
                            '<p class="text-slate-500 text-center py-8">Enter at least 2 characters to search</p>';
                        return;
                    }}
                    
                    searchTimeout = setTimeout(async () => {{
                        try {{
                            const res = await fetch(`/api/users/search?q=${{encodeURIComponent(query)}}`, {{ credentials: 'include' }});
                            if (res.ok) {{
                                const users = await res.json();
                                const container = document.getElementById('search-results');
                                
                                if (users.length === 0) {{
                                    container.innerHTML = '<p class="text-slate-500 text-center py-8">No users found</p>';
                                    return;
                                }}
                                
                                container.innerHTML = users.map(user => `
                                    <div class="flex items-center justify-between p-3 border rounded-lg">
                                        <a href="/u/${{user.id}}" class="flex items-center space-x-3 group">
                                            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                                                ${{user.avatar_url ? 
                                                    `<img src="${{user.avatar_url}}" class="w-10 h-10 rounded-full object-cover" />` :
                                                    `<span class="text-white font-medium">${{user.name[0].toUpperCase()}}</span>`
                                                }}
                                            </div>
                                            <div>
                                                <p class="font-medium group-hover:underline">${{user.name}}</p>
                                                <p class="text-sm text-slate-600">Level ${{user.level}} • ${{user.xp}} XP</p>
                                            </div>
                                        </a>
                                        <div class="flex items-center gap-3">
                                            <a href="/dm?to=${{user.id}}" class="text-sm text-indigo-600 hover:text-indigo-700">Message</a>
                                            ${{getFriendshipButton(user)}}
                                        </div>
                                    </div>
                                `).join('');
                            }}
                        }} catch (error) {{
                            console.error('Search failed:', error);
                        }}
                    }}, 300);
                }});

                function getFriendshipButton(user) {{
                    switch(user.friendship_status) {{
                        case 'friends':
                            return '<span class="text-sm text-green-600">Friends</span>';
                        case 'request_sent':
                            return '<span class="text-sm text-yellow-600">Request Sent</span>';
                        case 'request_received':
                            return '<span class="text-sm text-blue-600">Request Received</span>';
                        default:
                            return `<button onclick="sendFriendRequest('${{user.id}}')" class="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">Add Friend</button>`;
                    }}
                }}

                // Friend request actions
                async function sendFriendRequest(userId) {{
                    try {{
                        const res = await fetch(`/api/friends/request/${{userId}}`, {{
                            method: 'POST',
                            credentials: 'include'
                        }});
                        if (res.ok) {{
                            alert('Friend request sent!');
                            document.getElementById('search-input').dispatchEvent(new Event('input'));
                        }} else {{
                            const error = await res.json();
                            alert(error.detail || 'Failed to send friend request');
                        }}
                    }} catch (error) {{
                        alert('Network error');
                    }}
                }}

                async function acceptFriendRequest(friendshipId) {{
                    try {{
                        const res = await fetch(`/api/friends/accept/${{friendshipId}}`, {{
                            method: 'POST',
                            credentials: 'include'
                        }});
                        if (res.ok) {{
                            loadFriendRequests();
                            loadFriends();
                        }}
                    }} catch (error) {{
                        alert('Failed to accept friend request');
                    }}
                }}

                async function rejectFriendRequest(friendshipId) {{
                    try {{
                        const res = await fetch(`/api/friends/reject/${{friendshipId}}`, {{
                            method: 'POST',
                            credentials: 'include'
                        }});
                        if (res.ok) {{
                            loadFriendRequests();
                        }}
                    }} catch (error) {{
                        alert('Failed to reject friend request');
                    }}
                }}

                async function removeFriend(friendId) {{
                    if (!confirm('Are you sure you want to remove this friend?')) return;
                    
                    try {{
                        const res = await fetch(`/api/friends/${{friendId}}`, {{
                            method: 'DELETE',
                            credentials: 'include'
                        }});
                        if (res.ok) {{
                            loadFriends();
                        }}
                    }} catch (error) {{
                        alert('Failed to remove friend');
                    }}
                }}

                // Modal handlers
                document.getElementById('btn-search-users').addEventListener('click', () => {{
                    document.getElementById('modal-search-users').classList.remove('hidden');
                    document.getElementById('search-input').focus();
                }});

                document.getElementById('btn-close-search').addEventListener('click', () => {{
                    document.getElementById('modal-search-users').classList.add('hidden');
                    document.getElementById('search-input').value = '';
                    document.getElementById('search-results').innerHTML = 
                        '<p class="text-slate-500 text-center py-8">Enter at least 2 characters to search</p>';
                }});

                // Load data on page load
                loadFriendRequests();
                loadFriends();
            </script>
        </body>
        </html>
        """
    )
