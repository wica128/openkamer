
from document.models import Voting
from document.models import Vote
from document.models import VoteIndividual
from document.models import VoteParty

from government.models import Government
from parliament.models import PoliticalParty
from parliament.models import PartyMember
from parliament.models import ParliamentMember


def get_party_votes_for_government(government, vote_party_qs=None):
    if vote_party_qs is not None:
        votes_party = vote_party_qs.filter(voting__date__gte=government.date_formed)
    else:
        votes_party = VoteParty.objects.filter(voting__date__gte=government.date_formed)
    if government.date_dissolved:
        votes_party = votes_party.filter(voting__date__lt=government.date_dissolved)
    return votes_party


def get_voting_stats_per_party(vote_party_qs):
    parties = PoliticalParty.objects.all()
    parties = PoliticalParty.sort_by_current_seats(parties)
    governments = Government.objects.all()
    stats = []
    for party in parties:
        periods = []
        for gov in governments:
            party_votes = get_party_votes_for_government(gov, vote_party_qs=vote_party_qs)
            votes_for = party_votes.filter(party=party, decision=Vote.FOR)
            votes_against = party_votes.filter(party=party, decision=Vote.AGAINST)
            votes_none = party_votes.filter(party=party, decision=Vote.NONE)
            n_votes = party_votes.filter(party=party).count()
            if n_votes == 0:
                for_percent = 0
                against_percent = 0
                none_percent = 0
            else:
                for_percent = votes_for.count()/n_votes*100.0
                against_percent = votes_against.count()/n_votes*100.0
                none_percent = votes_none.count()/n_votes*100.0
            period = {
                'government': gov,
                'n_votes': n_votes,
                'for': votes_for,
                'against': votes_against,
                'none': votes_none,
                'for_percent': for_percent,
                'against_percent': against_percent,
                'none_percent': none_percent,
            }
            periods.append(period)
        stats.append({
            'party': party,
            'periods': periods,
        })
    return stats
