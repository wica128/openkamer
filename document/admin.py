from django.contrib import admin

from document.models import Dossier
from document.models import Document
from document.models import Kamerstuk
from document.models import Submitter
from document.models import Vote
from document.models import VoteParty
from document.models import VoteIndividual
from document.models import Voting


class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'dossier_id',
        'title_short',
        'date_published',
        'publication_type',
        'submitter',
        'category',
        'publisher',
        'document_url',
        'title_full',
    )


class KamerstukAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'id_main',
        'id_sub',
        'type_short',
        'type_long',
        'document_date',
        'original',
    )

    def document_date(self, obj):
        return obj.document.date_published


class SubmitterAdmin(admin.ModelAdmin):
    list_display = ('person', 'document')


class VotingAdmin(admin.ModelAdmin):
    list_display = ('dossier', 'result', 'date', 'is_dossier_voting', 'kamerstuk')


class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'voting', 'decision', 'number_of_seats', 'details')


class VotePartyAdmin(admin.ModelAdmin):
    list_display = ('id', 'voting', 'party', 'decision', 'number_of_seats', 'details')


class VoteIndividualAdmin(admin.ModelAdmin):
    list_display = ('id', 'voting', 'parliament_member', 'decision', 'number_of_seats', 'details')


admin.site.register(Dossier)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Kamerstuk, KamerstukAdmin)
admin.site.register(Submitter, SubmitterAdmin)

admin.site.register(Vote, VoteAdmin)
admin.site.register(VoteParty, VotePartyAdmin)
admin.site.register(VoteIndividual, VoteIndividualAdmin)
admin.site.register(Voting, VotingAdmin)
