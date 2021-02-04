from django import template
from ..models import SessionStatuses

register = template.Library()


@register.simple_tag
def session_status(obj):
    if obj == SessionStatuses.NOT_PUBLISHED:
        return "Non publié"
    elif obj == SessionStatuses.TEASED:
        return "Annoncé"
    elif obj == SessionStatuses.OPEN:
        return "Ouvert"
    elif obj == SessionStatuses.SUBMISSIONS_CLOSED:
        return "Fermé"
    else:
        return "État inconnu"


@register.simple_tag
def session_status_color(obj):
    if obj == SessionStatuses.NOT_PUBLISHED:
        return "#bdc3c7"
    elif obj == SessionStatuses.TEASED:
        return "#f39c12"
    elif obj == SessionStatuses.OPEN:
        return "#27ae60"
    elif obj == SessionStatuses.SUBMISSIONS_CLOSED:
        return "#c0392b"
    else:
        return "#000"


@register.simple_tag
def session_status_message(obj):
    if obj == SessionStatuses.NOT_PUBLISHED:
        return "La session n'est pas encore visible pour les candidats."
    elif obj == SessionStatuses.TEASED:
        return "Vous êtes convoqué à cette session."
    elif obj == SessionStatuses.OPEN:
        return "La session est ouverte. Vous pouvez dès maintenant accéder au sujet et téléverser des documents."  # noqa
    elif obj == SessionStatuses.SUBMISSIONS_CLOSED:
        return "La session n'accepte plus les rendus."
    else:
        return "Session dans un état inconnu."
