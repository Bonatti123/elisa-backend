from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.routers.auth import get_current_user
from api.schemas.promotions import (
    CampaignCreate,
    CampaignResponse,
    EvaluateRequest,
    EvaluateResponse,
    PromotionCreate,
    PromotionResponse,
    PromotionUpdate,
)
from api.utils.promotions_engine import PromotionsEngine
from clients.models import Campaign, Promotion, User

router = APIRouter()


def require_superadmin(user: User = Depends(get_current_user)) -> User:
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de superadmin",
        )
    return user


@router.get("/promotions/", response_model=list[PromotionResponse])
def list_promotions(
    is_active: bool | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    qs = Promotion.objects.all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    qs = qs.select_related("campaign").order_by("-created_at")[skip : skip + limit]
    return list(qs)


@router.get("/promotions/{promotion_id}", response_model=PromotionResponse)
def get_promotion(promotion_id: str):
    try:
        promotion = Promotion.objects.select_related("campaign").get(id=promotion_id)
    except Promotion.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promoción no encontrada",
        )
    return promotion


@router.post(
    "/promotions/",
    response_model=PromotionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_promotion(
    body: PromotionCreate,
    _: User = Depends(require_superadmin),
):
    data = body.model_dump()
    campaign_id = data.pop("campaign_id", None)
    if campaign_id:
        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaña no encontrada",
            )
        data["campaign"] = campaign
    promotion = Promotion.objects.create(**data)
    return promotion


@router.put("/promotions/{promotion_id}", response_model=PromotionResponse)
def update_promotion(
    promotion_id: str,
    body: PromotionUpdate,
    _: User = Depends(require_superadmin),
):
    try:
        promotion = Promotion.objects.get(id=promotion_id)
    except Promotion.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promoción no encontrada",
        )

    data = body.model_dump(exclude_unset=True)
    campaign_id = data.pop("campaign_id", None)
    if campaign_id is not None:
        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaña no encontrada",
            )
        data["campaign"] = campaign

    for attr, value in data.items():
        setattr(promotion, attr, value)
    promotion.save()
    return promotion


@router.delete("/promotions/{promotion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_promotion(
    promotion_id: str,
    _: User = Depends(require_superadmin),
):
    try:
        promotion = Promotion.objects.get(id=promotion_id)
    except Promotion.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promoción no encontrada",
        )
    promotion.is_active = False
    promotion.save()


@router.post("/promotions/evaluate", response_model=EvaluateResponse)
def evaluate_promotions(body: EvaluateRequest):
    result = PromotionsEngine.evaluate_promotions(
        client_id=body.client_id,
        amount=body.amount,
        context_type=body.context_type,
        web_type_id=body.web_type_id,
        service_product_id=body.service_product_id,
    )
    return result


@router.get("/campaigns/", response_model=list[CampaignResponse])
def list_campaigns(
    is_active: bool | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    qs = Campaign.objects.all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    qs = qs.order_by("-created_at")[skip : skip + limit]
    return list(qs)


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: str):
    try:
        campaign = Campaign.objects.get(id=campaign_id)
    except Campaign.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaña no encontrada",
        )
    return campaign


@router.post(
    "/campaigns/",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_campaign(
    body: CampaignCreate,
    _: User = Depends(require_superadmin),
):
    campaign = Campaign.objects.create(**body.model_dump())
    return campaign


@router.put("/campaigns/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: str,
    body: CampaignCreate,
    _: User = Depends(require_superadmin),
):
    try:
        campaign = Campaign.objects.get(id=campaign_id)
    except Campaign.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaña no encontrada",
        )
    for attr, value in body.model_dump().items():
        setattr(campaign, attr, value)
    campaign.save()
    return campaign


@router.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(
    campaign_id: str,
    _: User = Depends(require_superadmin),
):
    try:
        campaign = Campaign.objects.get(id=campaign_id)
    except Campaign.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaña no encontrada",
        )
    campaign.is_active = False
    campaign.save()
