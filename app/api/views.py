from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods
from django.views.decorators.csrf import csrf_exempt

from data.models import PixStream
from util.utils import generate_random_string, stream_fetch_and_response, consume_and_close_stream

@require_GET
@transaction.atomic
def stream_start(request, ispb: str):
    active_count = PixStream.objects.select_for_update().filter(ispb=ispb, active=True).count()
    
    if active_count >= 6:
        return JsonResponse({"detail": "Too Many Streams"}, status=429)

    stream = PixStream.objects.create(interation_id=generate_random_string(12), ispb=ispb)
    return stream_fetch_and_response(request, stream)


@csrf_exempt
@require_http_methods(["GET", "DELETE"])
@transaction.atomic
def stream_continue_or_delete(request, ispb: str, interation_id: str):
    try:
        stream = PixStream.objects.select_for_update().get(interation_id=interation_id, ispb=ispb)
    except PixStream.DoesNotExist:
        return JsonResponse({"detail": "Stream not found"}, status=404)

    if request.method == "DELETE":
        consume_and_close_stream(stream)
        return JsonResponse({})

    if not stream.active:
        return JsonResponse({"detail": "Stream closed"}, status=410)

    return stream_fetch_and_response(request, stream)