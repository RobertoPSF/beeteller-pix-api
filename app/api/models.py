from django.db import models
from django.utils import timezone


class PixStream(models.Model):

    interation_id = models.CharField(max_length=64, unique=True, db_index=True)
    ispb = models.CharField(max_length=8, db_index=True)
    active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_pull_at = models.DateTimeField(null=True, blank=True)
    terminated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["ispb", "active"]),
        ]

    def __str__(self) -> str:  
        status = "active" if self.active else "closed"
        return f"PixStream({self.interation_id}, ispb={self.ispb}, {status})"


class PixMessage(models.Model):

    class MessageStatus(models.TextChoices):
        PENDING = "pending", "pending"
        RESERVED = "reserved", "reserved"  
        CONSUMED = "consumed", "consumed"  

    end_to_end_id = models.CharField(max_length=64, unique=True, db_index=True)
    tx_id = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    payment_at = models.DateTimeField()

    free_text = models.TextField(blank=True, default="")

    payer_name = models.CharField(max_length=200)
    payer_cpf_cnpj = models.CharField(max_length=14)
    payer_ispb = models.CharField(max_length=8)
    payer_agencia = models.CharField(max_length=10)
    payer_conta_transacional = models.CharField(max_length=50)
    payer_tipo_conta = models.CharField(max_length=10)

    receiver_name = models.CharField(max_length=200)
    receiver_cpf_cnpj = models.CharField(max_length=14)
    receiver_ispb = models.CharField(max_length=8, db_index=True)
    receiver_agencia = models.CharField(max_length=10)
    receiver_conta_transacional = models.CharField(max_length=50)
    receiver_tipo_conta = models.CharField(max_length=10)

    status = models.CharField(
        max_length=16,
        choices=MessageStatus.choices,
        default=MessageStatus.PENDING,
        db_index=True,
    )
    reserved_by = models.ForeignKey(
        PixStream,
        related_name="reserved_messages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    reserved_at = models.DateTimeField(null=True, blank=True)
    consumed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["receiver_ispb", "status", "id"]),
            models.Index(fields=["status", "created_at"]),
        ]
        ordering = ["id"]

    def mark_reserved(self, stream: PixStream) -> None:
        self.status = self.MessageStatus.RESERVED
        self.reserved_by = stream
        self.reserved_at = timezone.now()

    def mark_consumed(self) -> None:
        self.status = self.MessageStatus.CONSUMED
        self.consumed_at = timezone.now()

    def __str__(self) -> str:  
        return f"PixMessage({self.end_to_end_id}, ispb={self.receiver_ispb}, status={self.status})"


