"""Motor de promociones para evaluar descuentos aplicables a clientes.
Evalúa condiciones, calcula descuentos y retorna la mejor promoción disponible.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()

from django.db.models import Q

from clients.models import Promotion


@dataclass(order=True)
class AppliedPromotion:
    """Representa una promoción aplicada con el descuento calculado."""
    savings: Decimal = field(compare=True)  # Ahorro total aplicado
    promotion_id: str = field(compare=False)
    name: str = field(compare=False)
    description: str = field(compare=False)
    benefit_description: str = field(compare=False)  # Descripción del beneficio
    discount_type: str = field(compare=False)
    discount_value: Decimal = field(compare=False)
    applies_to: str = field(compare=False)  # Contexto: quote, service, client
    final_amount: Decimal = field(compare=False)  # Monto final después del descuento


class PromotionsEngine:
    """Motor que evalúa promociones activas y calcula descuentos para un cliente."""

    @staticmethod
    def evaluate_promotions(
        client_id: str,
        amount: Decimal,
        context_type: str = "quote",
        web_type_id: str | None = None,
        service_product_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Evalúa todas las promociones activas para un cliente y contexto dado.
        Retorna la lista de promociones aplicables y la mejor opción.
        """
        now = datetime.now()
        # Filtra promociones activas dentro del rango de fechas válido
        promotions = Promotion.objects.filter(
            Q(valid_from__isnull=True) | Q(valid_from__lte=now),
            Q(valid_to__isnull=True) | Q(valid_to__gte=now),
            is_active=True,
            applies_to=context_type,
        )

        applicable: list[AppliedPromotion] = []
        for promotion in promotions:
            if PromotionsEngine._check_conditions(
                promotion, client_id, amount, web_type_id, service_product_id
            ):
                discount = PromotionsEngine._calculate_discount(promotion, amount)
                savings = min(discount, amount)
                final_amount = amount - savings
                applicable.append(
                    AppliedPromotion(
                        savings=savings,
                        promotion_id=str(promotion.id),
                        name=promotion.name,
                        description=promotion.description,
                        benefit_description=promotion.benefit_description,
                        discount_type=promotion.discount_type,
                        discount_value=promotion.discount_value,
                        applies_to=promotion.applies_to,
                        final_amount=final_amount,
                    )
                )

        # Ordena de mayor a menor ahorro
        applicable.sort(key=lambda p: p.savings, reverse=True)

        best_promotion = applicable[0] if applicable else None

        return {
            "applicable_promotions": [
                {
                    "promotion_id": p.promotion_id,
                    "name": p.name,
                    "description": p.description,
                    "benefit_description": p.benefit_description,
                    "discount_type": p.discount_type,
                    "discount_value": str(p.discount_value),
                    "applies_to": p.applies_to,
                    "savings": str(p.savings),
                    "final_amount": str(p.final_amount),
                }
                for p in applicable
            ],
            "best_promotion": (
                {
                    "promotion_id": best_promotion.promotion_id,
                    "name": best_promotion.name,
                    "description": best_promotion.description,
                    "benefit_description": best_promotion.benefit_description,
                    "discount_type": best_promotion.discount_type,
                    "discount_value": str(best_promotion.discount_value),
                    "applies_to": best_promotion.applies_to,
                    "savings": str(best_promotion.savings),
                    "final_amount": str(best_promotion.final_amount),
                }
                if best_promotion
                else None
            ),
            "original_amount": str(amount),
        }

    @staticmethod
    def _check_conditions(
        promotion: Promotion,
        client_id: str,
        amount: Decimal,
        web_type_id: str | None = None,
        service_product_id: str | None = None,
    ) -> bool:
        """Verifica si una promoción aplica según las condiciones configuradas."""
        # Validar montos mínimo y máximo de compra
        if promotion.min_purchase_amount is not None and amount < promotion.min_purchase_amount:
            return False

        if promotion.max_purchase_amount is not None and amount > promotion.max_purchase_amount:
            return False

        # Validar tipo de cliente
        if promotion.client_type is not None:
            try:
                from clients.models import Client

                client = Client.objects.get(id=client_id)
                if client.client_type != promotion.client_type:
                    return False
            except Client.DoesNotExist:
                return False

        # Validar tipo de web
        if promotion.web_type_id and web_type_id is not None:
            if web_type_id != promotion.web_type_id:
                return False

        # Validar frecuencia de pago del cliente
        if promotion.payment_frequency is not None:
            try:
                from clients.models import Client

                client = Client.objects.get(id=client_id)
                if client.payment_frequency != promotion.payment_frequency:
                    return False
            except Client.DoesNotExist:
                return False

        return True

    @staticmethod
    def _calculate_discount(promotion: Promotion, amount: Decimal) -> Decimal:
        """Calcula el descuento según el tipo (porcentaje o monto fijo)."""
        if promotion.discount_type == "percentage":
            discount = amount * (promotion.discount_value / Decimal("100"))
            if promotion.max_discount_amount is not None:
                discount = min(discount, promotion.max_discount_amount)
            return discount
        elif promotion.discount_type == "fixed":
            return min(promotion.discount_value, amount)
        return Decimal("0")
