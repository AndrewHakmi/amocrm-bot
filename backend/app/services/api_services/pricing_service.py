from decimal import Decimal
from typing import Optional, Annotated
from fastapi import Depends
from app.services.uow.unit_of_work import AbstractUnitOfWork
from app.services.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork

class PricingService:
    def __init__(self, uow_cls: type[AbstractUnitOfWork]): self.uow_cls = uow_cls

    async def estimate(self, *, device_type:str, model:str, symptom:str, zone:Optional[str]=None) -> dict:
        async with self.uow_cls() as uow:
            # 1) resolve issue
            issue = await uow.issues.find_one_or_none({"slug": symptom}) or \
                    await uow.issues.find_one_or_none({"title__ilike": symptom})
            onsite_possible = bool(getattr(issue, "onsite_default", True)) if issue else True

            # 2) resolve device/model
            device = await uow.devices.find_one_or_none({"name": device_type})
            d_id = getattr(device, "id", None)
            model_db = None
            if d_id:
                model_db = await uow.models.find_one_or_none({"device_id": d_id, "name": model})
            m_id = getattr(model_db, "id", None)
            i_id = getattr(issue, "id", None)

            # 3) rules: model+issue → device+issue → issue
            rule = None
            if m_id and i_id:
                rule = await uow.price_rules.find_one_or_none({"model_id": m_id, "issue_id": i_id})
            if not rule and d_id and i_id:
                rule = await uow.price_rules.find_one_or_none({"device_id": d_id, "model_id": None, "issue_id": i_id})
            if not rule and i_id:
                rule = await uow.price_rules.find_one_or_none({"device_id": None, "model_id": None, "issue_id": i_id})

            res = {
                "onsite_possible": onsite_possible,
                "min": None, "max": None,
                "currency": "KZT", "eta_min": None, "eta_max": None, "warranty_months": None,
            }
            if not rule: return res

            price_min = rule.min_price or rule.base_price
            price_max = rule.max_price or rule.base_price
            res["currency"] = rule.currency or res["currency"]
            res["eta_min"], res["eta_max"] = rule.eta_min, rule.eta_max
            res["warranty_months"] = rule.warranty_months

            if zone:
                z = await uow.zones.find_one_or_none({"name": zone})
                extra = getattr(z, "extra_fee", None)
                if extra:
                    if price_min is not None: price_min = Decimal(price_min) + Decimal(extra)
                    if price_max is not None: price_max = Decimal(price_max) + Decimal(extra)

            res["min"] = float(price_min) if price_min is not None else None
            res["max"] = float(price_max) if price_max is not None else None
            return res

def get_pricing_service(): return PricingService(SQLAlchemyUnitOfWork)
PricingServiceDep = Annotated[PricingService, Depends(get_pricing_service)]