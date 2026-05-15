"""
Canales de notificación para enviar alertas por correo y/o WhatsApp.

Cada canal implementa el método enviar(alerta) y se registra en
CANALES_DISPONIBLES. El notificador recorre los canales habilitados
y envía la alerta por cada uno.
"""

import logging
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


# ─── Canal de correo electrónico ──────────────────────────────────────


class CanalEmail:
    """
    Envía la alerta por correo electrónico a los destinatarios
    configurados en la base de datos o en settings.
    """

    @staticmethod
    def enviar(alerta):
        """
        Envía un correo con los datos de la alerta.
        Si no hay destinatarios configurados, solo registra en log.
        """
        destinatarios = getattr(settings, "ALERT_EMAIL_RECIPIENTS", None)

        if not destinatarios:
            logger.info(
                "CanalEmail: sin destinatarios configurados. "
                "Alerta %s ignorada: %s",
                alerta.id,
                alerta.message[:60],
            )
            return False

        asunto = f"[ELISA] Alerta: {alerta.get_alert_type_display()} - {alerta.supplier.business_name}"
        mensaje = (
            f"Tipo: {alerta.get_alert_type_display()}\n"
            f"Proveedor: {alerta.supplier.business_name}\n"
        )
        if alerta.service:
            mensaje += f"Servicio: {alerta.service.name}\n"
        mensaje += f"\n{alerta.message}\n"
        mensaje += f"\n---\nEsta es una notificación automática del sistema ELISA."

        try:
            send_mail(
                subject=asunto,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=destinatarios,
                fail_silently=False,
            )
            logger.info("CanalEmail: alerta %s enviada a %s", alerta.id, destinatarios)
            return True
        except Exception as e:
            logger.error("CanalEmail: error al enviar alerta %s: %s", alerta.id, e)
            return False


# ─── Canal de WhatsApp ────────────────────────────────────────────────


class CanalWhatsApp:
    """
    Envía la alerta por WhatsApp al número configurado.
    Por ahora solo registra en log como placeholder.
    Para producción, conectar con la API de WhatsApp Cloud / Twilio.
    """

    @staticmethod
    def enviar(alerta):
        """
        Envía un mensaje de WhatsApp con los datos de la alerta.
        Como placeholder, registra en log y retorna True.
        """
        numero = getattr(settings, "ALERT_WHATSAPP_NUMBER", None)

        if not numero:
            logger.info(
                "CanalWhatsApp: sin número configurado. "
                "Alerta %s ignorada: %s",
                alerta.id,
                alerta.message[:60],
            )
            return False

        mensaje = (
            f"🔔 *{alerta.get_alert_type_display()}*\n"
            f"*Proveedor:* {alerta.supplier.business_name}\n"
        )
        if alerta.service:
            mensaje += f"*Servicio:* {alerta.service.name}\n"
        mensaje += f"\n{alerta.message}"

        # ─── Placeholder: integrar API real aquí ───────────────────
        # Ejemplo con Twilio:
        # from twilio.rest import Client
        # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        # client.messages.create(body=mensaje, from_=settings.TWILIO_WHATSAPP_FROM, to=numero)
        #
        # Ejemplo con Meta WhatsApp Cloud API:
        # import requests
        # requests.post(
        #     f"https://graph.facebook.com/v18.0/{settings.WA_PHONE_NUMBER_ID}/messages",
        #     headers={"Authorization": f"Bearer {settings.WA_TOKEN}"},
        #     json={"messaging_product": "whatsapp", "to": numero, "text": {"body": mensaje}},
        # )

        logger.info(
            "CanalWhatsApp: alerta %s enviada a %s (placeholder)", alerta.id, numero
        )
        return True


# ─── Registro de canales disponibles ──────────────────────────────────


CANALES_DISPONIBLES = {
    "email": CanalEmail,
    "whatsapp": CanalWhatsApp,
}


def notificar_alerta(alerta):
    """
    Envía una alerta a través de todos los canales habilitados.
    Retorna un dict con {nombre_canal: True/False} indicando
    el resultado de cada envío.
    """
    resultados = {}

    for nombre_canal, clase_canal in CANALES_DISPONIBLES.items():
        try:
            exito = clase_canal.enviar(alerta)
            resultados[nombre_canal] = exito
        except Exception as e:
            logger.error(
                "Error en canal %s para alerta %s: %s",
                nombre_canal,
                alerta.id,
                e,
            )
            resultados[nombre_canal] = False

    return resultados
