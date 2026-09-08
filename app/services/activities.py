from sqlalchemy.orm import Session
from app.api.exceps import ItemAlreadyExistsError, ItemNotFoundError, NoPermissionError
from app.repositories.activities import ActivityRepository
from app.repositories.leads import LeadsRepository
from app.schemas.activities import ActivityCreate, ActivityUpdate
from app.utils.permissions import can_manage

class ActivityService:
    def __init__(self, db: Session):
        self.repository = ActivityRepository(db)
        self.leads_repository = LeadsRepository(db)



    def create_activity(self, user, data: ActivityCreate):

        lead = self.leads_repository.get_lead_by_id(data.lead_id)
        if not lead:
            raise ItemNotFoundError("Nenhum lead encontrado")


        if not can_manage(user, lead.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")


        return self.repository.create_activity(user.id, data)


    def get_activity_by_id(self, user, activity_id: int):

        activity = self.repository.get_activity_by_id(activity_id)
        if not activity:
            raise ItemNotFoundError("Nenhum activity encontrado")


        if not can_manage(user, activity.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")


        return activity

    def get_activity_by_lead_id(self, user, lead_id: int):

        activities = self.repository.get_activity_by_lead_id(lead_id)
        if not activities:
            raise ItemNotFoundError("Nenhum activity encontrado")


        if not all(can_manage(user, activity.user_id) for activity in activities):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")


        return activities

    def get_my_activities(self, user):
        activities = self.repository.get_my_activities(user.id)

        if not activities:
            raise ItemNotFoundError("Nenhum activity encontrado")

        return activities

    def get_activity_by_user_id(self, user, user_id: int = None ):
        target_id = user.id if user_id is None else user_id


        activities = self.repository.get_activity_by_user_id(target_id)
        
        if not activities:
            raise ItemNotFoundError("Nenhum activity encontrado")


        if not can_manage(user, target_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return activities

    def update_activity(self, activity_id: int, user, data: ActivityUpdate):

        activity = self.repository.get_activity_by_id(activity_id)
        if not activity:
            raise ItemNotFoundError("Nenhum activity encontrado")

        if not can_manage(user, activity.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")


        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(activity, field, value)

        return self.repository.update_activity(activity)

    def delete_activity(self, activity_id: int, user):

        activity = self.repository.get_activity_by_id(activity_id)
        if not activity:
            raise ItemNotFoundError("Nenhum activity encontrado")


        if not can_manage(user, activity.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return self.repository.delete_activity(activity)