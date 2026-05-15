"""Router de FastAPI para el módulo de Alertas."""

from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas.alerts import AlertResponse, AlertListResponse
from api.routers.auth import get_current_user
from clients.models import User
from alerts.models import Alert

router = APIRouter()


def _serialize_alert(alert: Alert) -> AlertResponse:
    """Convierte un modelo Alert a su schema de respuesta."""
    return AlertResponse(
        id=str(alert.id),
        supplier_id=str(alert.supplier.id),
        supplier_name=alert.supplier.business_name,
        alert_type=alert.alert_type,
        message=alert.message,
        is_read=alert.is_read,
        created_at=alert.created_at.isoformat(),
    )


@router.get("/", response_model=AlertListResponse)
def list_alerts(user: User = Depends(get_current_user)):
    """Obtiene todas las alertas ordenadas por fecha descendente."""
    alerts = Alert.objects.select_related("supplier").all()
    return AlertListResponse(
        alerts=[_serialize_alert(a) for a in alerts],
        total=alerts.count(),
        unread_count=alerts.filter(is_read=False).count(),
    )


@router.get("/unread", response_model=list[AlertResponse])
def list_unread_alerts(user: User = Depends(get_current_user)):
    """Obtiene solo las alertas no leídas."""
    alerts = Alert.objects.select_related("supplier").filter(is_read=False)
    return [_serialize_alert(a) for a in alerts]


@router.patch("/{alert_id}/read", response_model=AlertResponse)
def mark_alert_as_read(alert_id: str, user: User = Depends(get_current_user)):
    """Marca una alerta como leída."""
    try:
        alert = Alert.objects.get(id=alert_id)
    except Alert.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada",
        )
    alert.is_read = True
    alert.save()
    return _serialize_alert(alert)


@router.post("/mark-all-read", response_model=AlertListResponse)
def mark_all_alerts_as_read(user: User = Depends(get_current_user)):
    """Marca todas las alertas como leídas."""
    Alert.objects.filter(is_read=False).update(is_read=True)
    alerts = Alert.objects.select_related("supplier").all()
    return AlertListResponse(
        alerts=[_serialize_alert(a) for a in alerts],
        total=alerts.count(),
        unread_count=0,
    )
