from app.models.users import Roles

def can_manage(user, owner_id):
    """Gestao de usuarios: apenas admin ou o proprio usuario."""
    return user.role == Roles.ADMIN or user.id == owner_id

def can_edit_lead(user, owner_id):
    """Leads, atividades e propostas: admin e manager acessam de todos; sales, so os proprios."""
    return user.role in (Roles.ADMIN, Roles.MANAGER) or user.id == owner_id

def can_view_all_leads(user):
    """Listagem geral de leads: admin e manager veem todos; sales ve apenas os proprios."""
    return user.role in (Roles.ADMIN, Roles.MANAGER)

def can_manage_manager(user):
    return user.role in (Roles.ADMIN, Roles.MANAGER)

def can_manage_admin(user):
    return user.role == Roles.ADMIN