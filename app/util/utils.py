from datetime import datetime, timezone as dt_timezone
import time
import random
import string
from typing import List

from data.models import PixMessage, PixStream
from data.serializers import PixMessageSerializer

from django.http import JsonResponse, HttpResponse
from django.utils import timezone as dj_timezone


def generate_random_string(length: int = 16) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def generate_end_to_end_id(ispb: str) -> str:
    now = datetime.now(dt_timezone.utc)
    return f"E{ispb}{now.strftime('%Y%m%d%H%M%S')}{generate_random_string(8)}"


def build_pull_next(ispb: str, interation_id: str) -> str:
    return f"/api/pix/{ispb}/stream/{interation_id}"


def accepts_multipart(request) -> bool:
    return request.headers.get("Accept", "application/json").lower() == "multipart/json"


def is_valid_ispb(value: str) -> bool:
    return isinstance(value, str) and len(value) == 8 and value.isdigit()


def consume_and_close_stream(stream: PixStream) -> None:
    PixMessage.objects.filter(reserved_by=stream, status=PixMessage.MessageStatus.RESERVED).update(
        status=PixMessage.MessageStatus.CONSUMED, consumed_at=dj_timezone.now()
    )
    stream.active = False
    stream.terminated_at = dj_timezone.now()
    stream.save(update_fields=["active", "terminated_at"])


def stream_fetch_and_response(request, stream: PixStream):
    stream.last_pull_at = dj_timezone.now()
    stream.save(update_fields=["last_pull_at"])

    accept_raw = request.headers.get("Accept")
    if accept_raw and accept_raw.lower() not in ("application/json", "multipart/json"):
        return JsonResponse({"detail": "Unsupported Accept header. Use application/json or multipart/json."}, status=406)

    is_multipart = (accept_raw or "application/json").lower() == "multipart/json"
    limit = 10 if is_multipart else 1

    deadline = time.monotonic() + 8.0
    messages: List[PixMessage] = []
    while time.monotonic() < deadline:
        messages = list(
            PixMessage.objects.select_for_update(skip_locked=True)
            .filter(
                receiver_ispb=stream.ispb,
                status=PixMessage.MessageStatus.PENDING,
            )
            .order_by("id")[:limit]
        )

        if messages:
            for m in messages:
                m.mark_reserved(stream)
                m.save(update_fields=["status", "reserved_by", "reserved_at"])
            break

        time.sleep(0.2)

    pull_next = build_pull_next(stream.ispb, stream.interation_id)

    if not messages:
        response = HttpResponse(status=204)
        response["Pull-Next"] = pull_next
        return response

    serializer = PixMessageSerializer(messages if is_multipart else messages[0], many=is_multipart)
    data = serializer.data
    response = JsonResponse(data, safe=not is_multipart)
    response["Pull-Next"] = pull_next
    return response