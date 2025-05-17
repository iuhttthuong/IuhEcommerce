from db import Session
from models.fqas import FQA, FQACreate, FQAModel

class FQARepositories:
    @staticmethod
    def create(payload: FQACreate):
        with Session() as session:
            record = FQA(**payload.dict())
            session.add(record)
            session.commit()
            session.refresh(record)
            return FQAModel.from_orm(record)
    @staticmethod
    def get_all():
        with Session() as session:
            records = session.query(FQA).all()
            return [FQAModel.from_orm(record) for record in records]
    @staticmethod
    def get_by_id(id: int):
        with Session() as session:
            record = session.query(FQA).filter(FQA.id == id).first()
            return FQAModel.from_orm(record) if record else None