from rest_framework import serializers

from .models import PixMessage


class PartySerializer(serializers.Serializer):
    nome = serializers.CharField(source="name")
    cpfCnpj = serializers.CharField(source="cpf_cnpj")
    ispb = serializers.CharField()
    agencia = serializers.CharField()
    contaTransacional = serializers.CharField(source="conta_transacional")
    tipoConta = serializers.CharField(source="tipo_conta")


class PixMessageSerializer(serializers.ModelSerializer):
    endToEndId = serializers.CharField(source="end_to_end_id")
    valor = serializers.DecimalField(source="amount", max_digits=14, decimal_places=2)
    pagador = serializers.SerializerMethodField()
    recebedor = serializers.SerializerMethodField()
    campoLivre = serializers.CharField(source="free_text")
    txId = serializers.CharField(source="tx_id")
    dataHoraPagamento = serializers.DateTimeField(source="payment_at")

    class Meta:
        model = PixMessage
        fields = [
            "endToEndId",
            "valor",
            "pagador",
            "recebedor",
            "campoLivre",
            "txId",
            "dataHoraPagamento",
        ]
        read_only_fields = fields

    def get_pagador(self, obj: PixMessage):
        return {
            "nome": obj.payer_name,
            "cpfCnpj": obj.payer_cpf_cnpj,
            "ispb": obj.payer_ispb,
            "agencia": obj.payer_agencia,
            "contaTransacional": obj.payer_conta_transacional,
            "tipoConta": obj.payer_tipo_conta,
        }

    def get_recebedor(self, obj: PixMessage):
        return {
            "nome": obj.receiver_name,
            "cpfCnpj": obj.receiver_cpf_cnpj,
            "ispb": obj.receiver_ispb,
            "agencia": obj.receiver_agencia,
            "contaTransacional": obj.receiver_conta_transacional,
            "tipoConta": obj.receiver_tipo_conta,
        }


