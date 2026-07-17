"""Motor de promociones para evaluar descuentos aplicables a clientes.
Evalúa condiciones de negocio, calcula descuentos y retorna la mejor
promoción disponible según el mayor ahorro posible para el cliente.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any

from django.db.models import Q

from clients.models import Promotion


@dataclass(order=True)
class AppliedPromotion:
    """Representa una promoción que fue aplicada con el descuento ya calculado.
    Se usa dataclass con order=True para poder ordenar por ahorro de mayor a menor.
    """
    savings: Decimal = field(compare=True)
    promotion_id: str = field(compare=False)
    name: str = field(compare=False)
    description: str = field(compare=False)
    benefit_description: str = field(compare=False)
    discount_type: str = field(compare=False)
    discount_value: Decimal = field(compare=False)
    applies_to: str = field(compare=False)
    final_amount: Decimal = field(compare=False)


class PromotionsEngine:
    """Motor que evalúa promociones activas y calcula descuentos para un cliente.
    Analiza todas las promociones vigentes, verifica si cada una cumple las
    condiciones del cliente y contexto, y retorna la lista ordenada por ahorro.
    """

    @staticmethod
    def evaluate_promotions(
        client_id: str,
        amount: Decimal,
        context_type: str = "quote",
        web_type_id: str | None = None,
        service_product_id: str | None = None,
    ) -> dict[str, Any]:
        """Evalúa todas las promociones activas para un cliente y contexto dado.
        Filtra por vigencia de fechas, estado activo y tipo de contexto.
        Retorna la lista de promociones aplicables y la mejor opción.
        """
        now = datetime.now()

        # Busca promociones activas que estén dentro de su rango de fechas válido
        promotions = Promotion.objects.filter(
            Q(valid_from__isnull=True) | Q(valid_from__lte=now),
            Q(valid_to__isnull=True) | Q(valid_to__gte=now),
            is_active=True,
            applies_to=context_type,
        )

        applicable: list[AppliedPromotion] = []
        for promotion in promotions:
            # Verifica si la promoción cumple todas las condiciones del cliente
            if PromotionsEngine._check_conditions(
                promotion, client_id, amount, web_type_id, service_product_id
            ):
                discount = PromotionsEngine._calculate_discount(promotion, amount)
                # El ahorro no puede superar el monto total de la compra
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

        # Ordena las promociones de mayor a menor ahorro para mostrar la mejor primero
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
        """Verifica si una promoción aplica según las condiciones configuradas.
        Evalúa: montos mínimos y máximos de compra, tipo de cliente,
        tipo de web y frecuencia de pago. Si alguna condición falla retorna False.
        """
        # Validar que el monto de compra esté dentro del rango permitido
        if promotion.min_purchase_amount is not None and amount < promotion.min_purchase_amount:
            return False

        if promotion.max_purchase_amount is not None and amount > promotion.max_purchase_amount:
            return False

        # Validar que el tipo de cliente coincida con el objetivo de la promoción
        if promotion.client_type is not None:
            try:
                from clients.models import Client

                client = Client.objects.get(id=client_id)
                if client.client_type != promotion.client_type:
                    return False
            except Client.DoesNotExist:
                return False

        # Validar que el tipo de web coincida si la promoción lo requiere
        if promotion.web_type_id and web_type_id is not None:
            if web_type_id != promotion.web_type_id:
                return False

        # Validar que la frecuencia de pago del cliente coincida
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
        """Calcula el descuento según el tipo configurado en la promoción.
        Si es porcentaje, aplica el porcentaje sobre el monto.
        Si es fijo, resta el monto fijo (sin superar el total).
        Si el tipo no es válido, retorna cero.
        """
        if promotion.discount_type == "percentage":
            discount = amount * (promotion.discount_value / Decimal("100"))
            # Aplica el tope máximo de descuento si está configurado
            if promotion.max_discount_amount is not None:
                discount = min(discount, promotion.max_discount_amount)
            return discount
        elif promotion.discount_type == "fixed":
            return min(promotion.discount_value, amount)
        return Decimal("0")
