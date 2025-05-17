from fastapi import APIRouter, HTTPException
from models.fqas import FQA, FQACreate 
from services.fqas import FQAsService

router = APIRouter(prefix="/fqas", tags=["FQAs"])
@router.post("/", response_model=FQACreate)
def create_fqa(payload: FQACreate):
    return FQAsService.create(payload)
@router.get("/", response_model=list[FQACreate])
def get_all_fqas():
    return FQAsService.get_all()
@router.get("/{fqa_id}", response_model=FQACreate)
def get_fqa_by_id(fqa_id: int):
    fqa = FQAsService.get_by_id(fqa_id)
    if not fqa:
        raise HTTPException(status_code=404, detail="FQA not found")
    return fqa