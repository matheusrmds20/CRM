from app.models.users import Roles

def can_manage(user, owner_id):
    return user.role in (Roles.ADMIN) or user.id == owner_id

def can_manage_manager(user):
    return user.role in (Roles.ADMIN, Roles.MANAGER)

def can_manage_admin(user):
    return user.role in (Roles.ADMIN)

