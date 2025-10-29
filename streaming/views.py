import json
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from aiortc import RTCPeerConnection, RTCSessionDescription
from asgiref.sync import sync_to_async

# View cho trang chủ
def welcome_page(request):
    """Phục vụ trang Chào mừng (trang chủ mới)."""
    return render(request, "welcome.html")

# View để điều hướng sau khi đăng nhập
@login_required
def handle_login_redirect(request):
    """
    Điều hướng người dùng dựa trên vai trò của họ sau khi đăng nhập.
    """
    if request.user.groups.filter(name='Streamers').exists():
        return redirect('stream_page') # Streamer đi đến trang stream
    else:
        return redirect('viewer_page') # Viewer đi đến trang xem

# === Phần trạng thái (State) toàn cục ===
pcs = set()
rooms = {}  

@login_required 
def index(request): # Trang Streamer
    """Phục vụ trang Streamer."""
    if not request.user.groups.filter(name='Streamers').exists():
        messages.error(request, "Chỉ tài khoản 'Streamer' mới có thể truy cập trang này.")
        return redirect('viewer_page') 
        
    return render(request, "streamer.html")

def register_view(request):
    """Đăng ký tài khoản với vai trò (Streamer/Viewer)."""
    if request.user.is_authenticated:
        return redirect('login_redirect')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        role = request.POST.get('role', '') 

        if not username or not password:
            messages.error(request, 'Vui lòng điền username và password.')
        elif password != password2:
            messages.error(request, 'Mật khẩu không khớp.')
        elif not role: 
            messages.error(request, 'Vui lòng chọn vai trò (Streamer hoặc Viewer).')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Tên người dùng đã tồn tại.')
        else:
            try:
                user = User.objects.create_user(username=username, password=password)
                if role == 'streamer':
                    group_name = 'Streamers'
                else:
                    group_name = 'Viewers'
                group, created = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
                login(request, user)
                messages.success(request, f'Đăng ký thành công với vai trò {role}!')
                return redirect('login_redirect')        
            except Exception as e:
                messages.error(request, f"Đã xảy ra lỗi: {e}")

    return render(request, 'register.html')

def logout_view(request):
    """Đăng xuất người dùng và chuyển hướng về trang chủ."""
    logout(request)
    return redirect('welcome')

@login_required 
def viewer_page(request):
    """Phục vụ trang Viewer."""
    return render(request, "viewer.html")

async def offer(request):
    """
    Streamer gửi offer. Đây là một ASYNC view.
    """
    # 1. Kiểm tra đăng nhập (an toàn)
    is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
    if not is_authenticated:
        return HttpResponseForbidden("Bạn phải đăng nhập để stream.")
    
    # 2. Kiểm tra vai trò (an toàn)
    @sync_to_async
    def is_streamer(user):
        return user.groups.filter(name='Streamers').exists()

    if not await is_streamer(request.user):
        return HttpResponseForbidden("Chỉ 'Streamer' mới có thể gửi offer.")
        
    if request.method != "POST":
        return HttpResponse("Method Not Allowed", status=405)

    params = json.loads(request.body)
    room_id = params["room_id"]
    offer_sdp = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)
    stream_tracks = []
    
    # 3. Lấy username (an toàn)
    room_owner_username = await sync_to_async(lambda: request.user.username)() 

    @pc.on("track")
    def on_track(track):
        print(f"📡 [{room_id}] Streamer sending:", track.kind)
        stream_tracks.append(track)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"⚙️ [{room_id}] Streamer state: {pc.connectionState}")
        if pc.connectionState in ("failed", "closed", "disconnected"):
            print(f"❌ Streamer in room '{room_id}' disconnected, cleaning up...")
            if room_id in rooms:
                del rooms[room_id]
            await pc.close()
            pcs.discard(pc)

    await pc.setRemoteDescription(offer_sdp)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    rooms[room_id] = {
        "pc": pc,
        "tracks": stream_tracks,
        "owner": room_owner_username 
    }

    print(f"✅ Streamer '{room_owner_username}' connected to room '{room_id}'")
    return JsonResponse({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })


# === Sửa hàm viewer ===
async def viewer(request):
    """
    Viewer kết nối để xem. Đây cũng là một ASYNC view.
    """
    # 1. Kiểm tra đăng nhập (an toàn)
    is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
    if not is_authenticated:
        return HttpResponseForbidden("Bạn phải đăng nhập để xem.")

    if request.method != "POST":
        return HttpResponse("Method Not Allowed", status=405)

    params = json.loads(request.body)
    room_id = params["room_id"]
    offer_sdp = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    if room_id not in rooms:
        return JsonResponse({"error": f"Room '{room_id}' not found"}, status=404)

    streamer_tracks = rooms[room_id]["tracks"]
    pc = RTCPeerConnection()
    pcs.add(pc)

    for track in streamer_tracks:
        pc.addTrack(track)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"👀 [{room_id}] Viewer state: {pc.connectionState}")
        if pc.connectionState in ("failed", "closed", "disconnected"):
            await pc.close()
            pcs.discard(pc)

    await pc.setRemoteDescription(offer_sdp)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # 2. Lấy username (an toàn)
    viewer_username = await sync_to_async(lambda: request.user.username)()
    print(f"👀 Viewer '{viewer_username}' connected to room '{room_id}'")

    return JsonResponse({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })