from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from data.models import PixStream
from util.utils import generate_random_string, stream_fetch_and_response

@require_GET
@transaction.atomic
def stream_start(request, ispb: str):
    active_count = PixStream.objects.select_for_update().filter(ispb=ispb, active=True).count()
    
    if active_count >= 6:
        return JsonResponse({"detail": "Too Many Streams"}, status=429)

    stream = PixStream.objects.create(interation_id=generate_random_string(12), ispb=ispb)
    return stream_fetch_and_response(request, stream)