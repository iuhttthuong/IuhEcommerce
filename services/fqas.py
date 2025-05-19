from repositories.fqas import FQARepositories
from models.fqas import FQACreate

class FQAsService:
    @staticmethod
    def create(payload: FQACreate) -> FQACreate:
        return FQARepositories.create(payload)

    @staticmethod
    def get_all() -> list[FQACreate]:
        return FQARepositories.get_all()
    
    @staticmethod
    def get_by_id(id: int) -> FQACreate | None:
        return FQARepositories.get_by_id(id)