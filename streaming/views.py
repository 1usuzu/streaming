import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from aiortc import RTCPeerConnection, RTCSessionDescription
# from aiortc.contrib.media import MediaRelay

# === Phần trạng thái (State) toàn cục ===
# Giống như trong code aiohttp của bạn, chúng ta lưu state trong bộ nhớ.
# ⚠️ CẢNH BÁO: Xem lưu ý quan trọng ở cuối.
pcs = set()
# relay = MediaRelay()
rooms = {}  # room_id -> {"pc": pc, "tracks": [...]}
# ========================================

def index(request):
    """Phục vụ trang Streamer."""
    return render(request, "streamer.html")

def viewer_page(request):
    """Phục vụ trang Viewer."""
    return render(request, "viewer.html")

@csrf_exempt  # Bỏ qua kiểm tra CSRF vì client gửi JSON
async def offer(request):
    """
    Streamer gửi offer. Đây là một ASYNC view.
    """
    if request.method != "POST":
        return HttpResponse("Method Not Allowed", status=405)

    params = json.loads(request.body)
    room_id = params["room_id"]
    offer_sdp = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)
    stream_tracks = []

    @pc.on("track")
    def on_track(track):
        print(f"📡 [{room_id}] Streamer sending:", track.kind)

        # stream_tracks.append(relay.subscribe(track))
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

    # Đặt offer của streamer làm remote description
    await pc.setRemoteDescription(offer_sdp)

    # Tạo answer và đặt làm local description
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    # Lưu lại PC và các track đã relay
    rooms[room_id] = {
        "pc": pc,
        "tracks": stream_tracks
    }

    print(f"✅ Streamer connected to room '{room_id}'")

    # Trả về answer cho streamer
    return JsonResponse({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })


@csrf_exempt  # Bỏ qua kiểm tra CSRF
async def viewer(request):
    """
    Viewer kết nối để xem. Đây cũng là một ASYNC view.
    """
    if request.method != "POST":
        return HttpResponse("Method Not Allowed", status=405)

    params = json.loads(request.body)
    room_id = params["room_id"]
    offer_sdp = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    if room_id not in rooms:
        return JsonResponse({"error": f"Room '{room_id}' not found"}, status=404)

    # Lấy các track đã được relay của streamer
    streamer_tracks = rooms[room_id]["tracks"]

    pc = RTCPeerConnection()
    pcs.add(pc)

    # Thêm các track của streamer vào PC của viewer
    for track in streamer_tracks:
        pc.addTrack(track)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"👀 [{room_id}] Viewer state: {pc.connectionState}")
        if pc.connectionState in ("failed", "closed", "disconnected"):
            await pc.close()
            pcs.discard(pc)

    # Đặt offer của viewer làm remote description
    await pc.setRemoteDescription(offer_sdp)

    # Tạo answer và đặt làm local description
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    print(f"👀 Viewer connected to room '{room_id}'")

    # Trả về answer cho viewer
    return JsonResponse({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })