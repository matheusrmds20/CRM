from sqlalchemy.orm import Session

from app.api.exceps import BadRequestError, ItemAlreadyExistsError, ItemNotFoundError, NoPermissionError
from app.repositories.activities import ActivityRepository
from app.repositories.leads import LeadsRepository
from app.schemas.activities import ActivityCreate, ActivityUpdate


class ActivityService:
    def __init__(self, db: Session):
        self.repository = ActivityRepository(db)
        self.leads_repository = LeadsRepository(db)

    def _can_manage(self, user, owner_id):
        return user.role in ("admin", "manager") or user.id == owner_id

    def create_activity(self, user_id: int, data: ActivityCreate):
        if data.type == "":
            raise BadRequestError("Nenhum tipo de activity foi selecionado")

        lead = self.leads_repository.get_lead_by_id(data.lead_id, user_id)
        if not lead:
            raise ItemNotFoundError("Nenhum lead encontrado")

        if lead.user_id != user_id:
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        activity_already_exists = self.repository.get_activity_by_lead_id(user_id, data.lead_id)
        if activity_already_exists:
            raise ItemAlreadyExistsError("Activity ja existe")

        return self.repository.create_activity(user_id, data)

    def get_all_activities(self, user):
        activities = self.repository.get_all_activities(user.id)
        if not activities:
            raise ItemNotFoundError("Nenhum activity encontrado")

        return activities

    def get_activity_by_id(self, user, activity_id: int):
        activity = self.repository.get_activity_by_id(user.id, activity_id)
        if not activity:
            raise ItemNotFoundError("Nenhum activity encontrado")

        if not self._can_manage(user, activity.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return activity

    def get_activity_by_lead_id(self, user, lead_id: int):
        activity = self.repository.get_activity_by_lead_id(user.id, lead_id)
        if not activity:
            raise ItemNotFoundError("Nenhum activity encontrado")

        if not self._can_manage(user, activity.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return activity

    def get_activity_by_user_id(self, user, user_id: int):
        activities = self.repository.get_activity_by_user_id(user_id)
        if not activities:
            raise ItemNotFoundError("Nenhum activity encontrado")

        return activities

    def update_activity(self, activity_id: int, user, data: ActivityUpdate):
        activity = self.repository.get_activity_by_id(user.id, activity_id)
        if not activity:
            raise ItemNotFoundError("Nenhum activity encontrado")

        if not self._can_manage(user, activity.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(activity, field, value)

        return self.repository.update_activity(activity)

    def delete_activity(self, activity_id: int, user):
        activity = self.repository.get_activity_by_id(user.id, activity_id)
        if not activity:
            raise ItemNotFoundError("Nenhum activity encontrado")

        if not self._can_manage(user, activity.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return self.repository.delete_activity(activity)
