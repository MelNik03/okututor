from django.http import JsonResponse, HttpResponseRedirect
from django.conf import settings
from .zoom_service import ZoomService
from firebase_admin import firestore

def zoom_authorize(request):
    zoom_service = ZoomService()
    auth_url = zoom_service.get_authorization_url()
    return HttpResponseRedirect(auth_url)

def zoom_callback(request):
    code = request.GET.get("code")
    zoom_service = ZoomService()
    token_data = zoom_service.get_access_token(code)
    access_token = token_data.get("access_token")

    # Сохраняем токен в Firestore (например, для пользователя)
    db = firestore.client()
    db.collection("zoom_tokens").document("admin").set({
        "access_token": access_token,
        "refresh_token": token_data.get("refresh_token"),
    })
    return JsonResponse({"status": "success", "access_token": access_token})

def create_zoom_meeting(request):
    db = firestore.client()
    token_doc = db.collection("zoom_tokens").document("admin").get()
    access_token = token_doc.to_dict().get("access_token")

    zoom_service = ZoomService()
    meeting = zoom_service.create_meeting(
        access_token=access_token,
        user_id="me",  # Для текущего пользователя
        topic="Okututor Lesson",
        start_time="2025-05-10T10:00:00Z",
        duration=60,
    )

    # Сохраняем данные встречи в Firestore
    db.collection("meetings").document(str(meeting["id"])).set({
        "meeting_id": meeting["id"],
        "join_url": meeting["join_url"],
        "start_url": meeting["start_url"],
        "course_id": request.GET.get("course_id", ""),
    })

    return JsonResponse({
        "meeting_id": meeting["id"],
        "join_url": meeting["join_url"],
        "start_url": meeting["start_url"],
    })