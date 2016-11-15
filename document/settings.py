from django.conf import settings

AGENDAS_PER_PAGE = getattr(settings, 'AGENDAS_PER_PAGE', 50)
DOSSIERS_PER_PAGE = getattr(settings, 'DOSSIERS_PER_PAGE', 20)
VOTINGS_PER_PAGE = getattr(settings, 'VOTINGS_PER_PAGE', 25)
BESLUITENLIJSTEN_PER_PAGE = getattr(settings, 'BESLUITENLIJSTEN_PER_PAGE', 200)