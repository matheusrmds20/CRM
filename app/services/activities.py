from sqlalchemy.orm import Session
from app.api.exceps import ItemNotFoundError, NoPermissionError
from app.repositories.activities import ActivityRepository
from app.repositories.leads import LeadsRepository
from app.schemas.activities import ActivityCreate, ActivityUpdate
from app.utils.permissions import can_edit_lead

class ActivityService:
    def __init__(self, db: Session):
        self.repository = ActivityRepository(db)
        self.leads_repository = LeadsRepository(db)

    def create_activity(self, user, data: ActivityCreate):

        lead = self.leads_repository.get_lead_by_id(data.lead_id)
        if not lead:
            raise ItemNotFoundError("Nenhum lead encontrado")

        if not can_edit_lead(user, lead.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return self.repository.create_activity(user.id, data)

    def get_activity_by_lead_id(self, user, lead_id: int):

        lead = self.leads_repository.get_lead_by_id(lead_id)
        if not lead:
            raise ItemNotFoundError("Nenhum lead encontrado")

        if not can_edit_lead(user, lead.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return self.repository.get_activity_by_lead_id(lead_id)

    def update_activity(self, activity_id: int, user, data: ActivityUpdate):

        activity = self.repository.get_activity_by_id(activity_id)
        if not activity:
            raise ItemNotFoundError("Nenhum activity encontrado")

        if not can_edit_lead(user, activity.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(activity, field, value)

        return self.repository.update_activity(activity)

    def delete_activity(self, activity_id: int, user):

        activity = self.repository.get_activity_by_id(activity_id)
        if not activity:
            raise ItemNotFoundError("Nenhum activity encontrado")

        if not can_edit_lead(user, activity.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return self.repository.delete_activity(activity)