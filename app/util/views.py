import random
import string
from datetime import datetime, timezone as dt_timezone
from typing import List

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from data.models import PixMessage
from util.utils import generate_random_string, generate_end_to_end_id, is_valid_ispb


@csrf_exempt
@require_POST
@transaction.atomic
def generate_messages(request, ispb: str, number: int):
    if not is_valid_ispb(ispb):
        return JsonResponse({"detail": "Invalid ispb. Expected 8 digits."}, status=400)

    if number < 1 or number > 1000:
        return JsonResponse({"detail": "Invalid number. Range allowed: 1..1000."}, status=400)

    created: List[PixMessage] = []
    for _ in range(number):
        amount_cents = random.randint(100, 100000)
        amount = amount_cents / 100
        payer_ispb = "12345678"
        tx_id = generate_random_string(18)
        message = PixMessage(
            end_to_end_id=generate_end_to_end_id(ispb),
            tx_id=tx_id,
            amount=amount,
            payment_at=timezone.now(),
            free_text="",
            payer_name="Roberto Filho",
            payer_cpf_cnpj="12345678901",
            payer_ispb=payer_ispb,
            payer_agencia="0001",
            payer_conta_transacional="1231231",
            payer_tipo_conta="CACC",
            receiver_name="Roberto Pereira",
            receiver_cpf_cnpj="01987654321",
            receiver_ispb=ispb,
            receiver_agencia="0001",
            receiver_conta_transacional="4564564",
            receiver_tipo_conta="SVGS",
        )
        created.append(message)

    if not created:
        return JsonResponse({"inserted": 0, "detail": "No messages to insert."}, status=200)

    PixMessage.objects.bulk_create(created, batch_size=1000)
    return JsonResponse({"inserted": len(created)}, status=201)