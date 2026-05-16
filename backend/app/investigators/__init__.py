from app.investigators.breach import BreachInvestigator
from app.investigators.dark_web import DarkWebInvestigator
from app.investigators.domain import DomainInvestigator
from app.investigators.email import EmailInvestigator
from app.investigators.phone import PhoneInvestigator
from app.investigators.social import SocialInvestigator
from app.investigators.username import UsernameInvestigator

DEFAULT_INVESTIGATORS = [
    EmailInvestigator(),
    PhoneInvestigator(),
    UsernameInvestigator(),
    BreachInvestigator(),
    DomainInvestigator(),
    SocialInvestigator(),
    DarkWebInvestigator(),
]
