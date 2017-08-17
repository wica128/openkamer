import logging

from django.db import models
from django.db import transaction

from person.models import Person

from document.models import Kamervraag
from document.models import Vote
from document.models import Voting
from document.models import Submitter

from government.models import Government
from parliament.models import PoliticalParty

from stats import util

from stats.plots import kamervraag_vs_time_plot_html
from stats.plots import kamervraag_reply_time_contour_plot_html
from stats.plots import kamervraag_reply_time_histogram_plot_html
from stats.plots import kamervragen_reply_time_per_party


logger = logging.getLogger(__name__)


def update_all():
    logger.info('BEGIN')
    StatsVotingSubmitter.create()
    PartyVoteBehaviour.create_all()
    Plot.create_all()
    logger.info('END')


class PartyVoteBehaviour(models.Model):
    BILL = 'BILL'
    OTHER = 'OTHER'
    VOTING_TYPE_CHOICES = (
        (BILL, 'Wetsvoorstel'),
        (OTHER, 'Overig (Motie, Amendement)')
    )
    party = models.ForeignKey(PoliticalParty)
    submitter = models.ForeignKey(PoliticalParty, related_name='party_vote_behaviour_submitter', blank=True, null=True)
    government = models.ForeignKey(Government)
    voting_type = models.CharField(max_length=5, choices=VOTING_TYPE_CHOICES)
    votes_for = models.IntegerField()
    votes_against = models.IntegerField()
    votes_none = models.IntegerField()

    def total_votes(self):
        return self.votes_for + self.votes_against + self.votes_none

    @staticmethod
    def get_stats_party(party, government=None, voting_type=None):
        """
        Returns voting behaviour stats for a given party during a given government period.

        :param party: the party for which to get the stats
        :param government: (optional) the government period for which to get the stats
        :param voting_type: (optional) the type of voting
        :return: a dictionary with basic voting stats
        """
        vote_behaviours = PartyVoteBehaviour.objects.filter(submitter__isnull=True)
        vote_behaviours = PartyVoteBehaviour.filter_by_type_and_government(vote_behaviours, voting_type=voting_type, government=government)
        return PartyVoteBehaviour.get_stats_party_for_qs(party, vote_behaviours)

    @staticmethod
    def get_stats_party_for_submitter(party_voting, party_submitting, government=None, voting_type=None):
        """
        Returns voting behaviour stats for a given party, for a given submitting party, during a given government period.

        :param party_voting: the party for which to get the stats
        :param party_submitting: the party who submitted/initiated the voting (or related document or bill)
        :param government: the government period for which to get the stats
        :param voting_type: (optional) the type of voting
        :return: a dictionary with basic voting stats
        """
        vote_behaviours = PartyVoteBehaviour.objects.filter(submitter=party_submitting)
        vote_behaviours = PartyVoteBehaviour.filter_by_type_and_government(vote_behaviours, voting_type=voting_type, government=government)
        return PartyVoteBehaviour.get_stats_party_for_qs(party_voting, vote_behaviours)

    @staticmethod
    def filter_by_type_and_government(vote_behaviours, voting_type=None, government=None):
        if government:
            vote_behaviours = vote_behaviours.filter(government=government)
        if voting_type:
            vote_behaviours = vote_behaviours.filter(voting_type=voting_type)
        return vote_behaviours

    @staticmethod
    @transaction.atomic
    def create_all():
        logger.info('BEGIN')
        vote_submitters = StatsVotingSubmitter.objects.all()
        party_ids = list(vote_submitters.values_list('party__id', flat=True))
        PartyVoteBehaviour.objects.all().delete()
        parties = PoliticalParty.objects.filter(id__in=party_ids)
        for party in parties:
            PartyVoteBehaviour.create(party)
        logger.info('END, number of objects created: ' + str(PartyVoteBehaviour.objects.all().count()))

    @staticmethod
    @transaction.atomic
    def create(party):
        logger.info('BEGIN for party: ' + str(party))
        governments = Government.objects.all()
        party_votes_per_gov = []
        for gov in governments:
            party_votes_per_gov.append({'government': gov, 'party_votes': util.get_party_votes_for_government(gov)})
        stats = []
        parties = PoliticalParty.objects.all()
        for party_submitting in parties:
            PartyVoteBehaviour.create_for_submitting_party(party, party_submitting, party_votes_per_gov)
        PartyVoteBehaviour.create_for_submitting_party(party, None, party_votes_per_gov)
        logger.info('END')
        return stats

    @staticmethod
    def create_for_submitting_party(party, party_submitting, party_votes_per_gov):
        for votes_for_gov in party_votes_per_gov:
            for voting_type in PartyVoteBehaviour.VOTING_TYPE_CHOICES:
                PartyVoteBehaviour.create_party_type_gov(
                    party=party,
                    party_votes=votes_for_gov['party_votes'],
                    party_submitting=party_submitting,
                    government=votes_for_gov['government'],
                    voting_type=voting_type[0]
                )

    @staticmethod
    def create_party_type_gov(party, party_votes, party_submitting, government, voting_type):
        if voting_type == PartyVoteBehaviour.BILL:
            party_votes = party_votes.filter(voting__is_dossier_voting=True)
        elif voting_type == PartyVoteBehaviour.OTHER:
            party_votes = party_votes.filter(voting__is_dossier_voting=False)
        else:
            assert False
        party_votes = party_votes.filter(party=party)
        if party_submitting is not None:
            voting_ids = PartyVoteBehaviour.get_voting_ids_submitted_by_party(party_submitting)
            party_votes = party_votes.filter(voting__in=voting_ids).distinct()
        votes_for = party_votes.filter(decision=Vote.FOR)
        votes_against = party_votes.filter( decision=Vote.AGAINST)
        votes_none = party_votes.filter(decision=Vote.NONE)
        PartyVoteBehaviour.objects.create(
            party=party,
            submitter=party_submitting,
            government=government,
            voting_type=voting_type,
            votes_for=votes_for.count(),
            votes_against=votes_against.count(),
            votes_none=votes_none.count()
        )

    @staticmethod
    def get_voting_ids_submitted_by_party(party):
        submitters = StatsVotingSubmitter.objects.filter(party=party).select_related('voting')
        voting_ids = set()
        for submitter in submitters:
            voting_ids.add(submitter.voting.id)
        return voting_ids

    @staticmethod
    def get_stats_party_for_qs(party, vote_behaviours):
        """
        Return the vote behaviour for a given party, based on a queryset.
        Warning: this QuerySet should be filtered on one or no submitter (party), NOT multiple submitter parties.
        This would give incorrect (unexpected) results because one voting can have multiple submitters,
        causing votes to be counted more than once.

        :param party: the party for which to return the vote behaviour
        :param vote_behaviours: PartyVoteBehaviour QuerySet that is filtered on one, and only one submitter party,
        or not filtered by submitter at all
        :return: a dictionary of party vote behaviour
        """
        vote_behaviours = vote_behaviours.filter(party=party)
        # we either filter by no submitter (any party), or one party
        vote_behaviours_any_party = vote_behaviours.filter(submitter__isnull=True)
        if vote_behaviours_any_party:
            vote_behaviours = vote_behaviours_any_party
        n_votes_for = 0
        n_votes_against = 0
        n_votes_none = 0
        for result in vote_behaviours:
            n_votes_for += result.votes_for
            n_votes_against += result.votes_against
            n_votes_none += result.votes_none
        n_votes = n_votes_for + n_votes_against + n_votes_none
        if n_votes == 0:
            for_percent = 0
            against_percent = 0
            none_percent = 0
        else:
            for_percent = n_votes_for / n_votes * 100.0
            against_percent = n_votes_against / n_votes * 100.0
            none_percent = n_votes_none / n_votes * 100.0
        result = {
            'party': party,
            'n_votes': n_votes,
            'n_for': n_votes_for,
            'n_against': n_votes_against,
            'n_none': n_votes_for,
            'for_percent': for_percent,
            'against_percent': against_percent,
            'none_percent': none_percent,
        }
        return result


class StatsVotingSubmitter(models.Model):
    voting = models.ForeignKey(Voting)
    person = models.ForeignKey(Person)
    party = models.ForeignKey(PoliticalParty, blank=True, null=True)

    @staticmethod
    @transaction.atomic
    def create():
        logger.info('BEGIN')
        StatsVotingSubmitter.objects.all().delete()
        votings = Voting.objects.all()
        for voting in votings:
            for submitter in voting.submitters:
                StatsVotingSubmitter.objects.create(
                    voting=voting,
                    person=submitter.person,
                    party=submitter.party
                )
        logger.info('END')


class Plot(models.Model):
    KAMERVRAAG_VS_TIME = 'KVT'
    KAMERVRAAG_REPLY_TIME_HIST = 'KRTH'
    KAMERVRAAG_REPLY_TIME_2DHIST = 'KRT2D'
    KAMERVRAAG_REPLY_TIME_PER_PARTY = 'KRTPP'
    PLOT_TYPES = (
        (KAMERVRAAG_VS_TIME, 'Kamervraag vs Time'),
        (KAMERVRAAG_REPLY_TIME_HIST, 'Kamervraag reply time histogram'),
        (KAMERVRAAG_REPLY_TIME_2DHIST, 'Kamervraag reply time 2D histogram'),
        (KAMERVRAAG_REPLY_TIME_PER_PARTY, 'Kamervraag reply time per party'),
    )
    type = models.CharField(max_length=10, choices=PLOT_TYPES, default=KAMERVRAAG_VS_TIME, db_index=True, unique=True)
    html = models.TextField()
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-datetime_updated']


    @staticmethod
    @transaction.atomic
    def create():
        logger.info('BEGIN')
        Plot.create_kamervragen_plots()
        logger.info('END')

    @staticmethod
    @transaction.atomic
    def create_kamervragen_plots():
        # kamervragen = Kamervraag.objects.filter(kamerantwoord__isnull=False).select_related('document')
        # kamervraag_dates = []
        # for kamervraag in kamervragen:
        #     kamervraag_dates.append(kamervraag.document.date_published)
        # kamervraag_durations = []
        # for kamervraag in kamervragen:
        #     kamervraag_durations.append(kamervraag.duration)
        # plot, created = Plot.objects.get_or_create(type=Plot.KAMERVRAAG_VS_TIME)
        # plot.html = kamervraag_vs_time_plot_html(kamervraag_dates)
        # plot.save()
        # plot, created = Plot.objects.get_or_create(type=Plot.KAMERVRAAG_REPLY_TIME_HIST)
        # plot.html = kamervraag_reply_time_histogram_plot_html(kamervraag_durations)
        # plot.save()
        # plot, created = Plot.objects.get_or_create(type=Plot.KAMERVRAAG_REPLY_TIME_2DHIST)
        # plot.html = kamervraag_reply_time_contour_plot_html(kamervraag_dates, kamervraag_durations)
        # plot.save()

        party_slugs = ['pvv', 'sp', 'cda', 'd66', 'vvd', 'pvda', 'gl', 'cu', 'pvdd']
        party_durations = []
        for party in party_slugs:
            submitters = Submitter.objects.filter(party_slug=party)
            submitter_ids = list(submitters.values_list('id', flat=True))
            kamervragen = Kamervraag.objects.filter(document__submitter__in=submitter_ids, kamerantwoord__isnull=False).select_related('document').distinct()
            # kamervraag_dates = []
            # for kamervraag in kamervragen:
            #     kamervraag_dates.append(kamervraag.document.date_published)
            kamervraag_durations = []
            for kamervraag in kamervragen:
                kamervraag_durations.append(kamervraag.duration)
            party_durations.append(kamervraag_durations)

        plot, created = Plot.objects.get_or_create(type=Plot.KAMERVRAAG_REPLY_TIME_PER_PARTY)
        plot.html = kamervragen_reply_time_per_party(party_slugs, party_durations)
        plot.save()
