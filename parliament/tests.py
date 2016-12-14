import datetime

from django.test import TestCase

from person.models import Person

from parliament.models import Parliament
from parliament.models import ParliamentMember
from wikidata import wikidata


class TestPoliticalParty(TestCase):

    def test_get_political_party_memberships_wikidata(self):
        mark_rutte_wikidata_id = 'Q57792'
        item = wikidata.WikidataItem(mark_rutte_wikidata_id)
        parties = item.get_political_party_memberships()
        self.assertEqual(len(parties), 1)


class TestParliamentMembers(TestCase):
    fixtures = ['person.json', 'parliament.json']

    def test_get_members_at_date(self):
        tweede_kamer = Parliament.get_or_create_tweede_kamer()
        active_members = tweede_kamer.get_members_at_date(datetime.date(year=2016, month=6, day=1))
        self.assertEqual(len(active_members), 150)
        # print(len(active_members))  # TODO: check for number if members have non null joined/left fields

    def test_get_member_for_person_at_date(self):
        person = Person.find_by_fullname('Diederik Samsom')
        members_all = ParliamentMember.objects.filter(person=person)
        self.assertEqual(members_all.count(), 4)
        members = ParliamentMember.find_at_date(person, datetime.date(year=2016, month=6, day=1))
        self.assertEqual(members[0].joined, datetime.date(year=2012, month=9, day=20))
        self.assertEqual(members.count(), 1)
        self.assertEqual(members[0].person, person)
        members = ParliamentMember.find_at_date(person, datetime.date(year=2004, month=6, day=1))
        self.assertEqual(members[0].joined, datetime.date(year=2003, month=1, day=30))
        self.assertEqual(members.count(), 1)
        self.assertEqual(members[0].person, person)

    def test_find_members(self):
        person = Person.find_by_fullname('Diederik Samsom')
        member = ParliamentMember.find('Samsom', initials='D.M.')
        self.assertEqual(member.person, person)
        member = ParliamentMember.find('Samsom', initials='D.M.', date=datetime.date(year=2004, month=6, day=1))
        self.assertEqual(member.person, person)
        self.assertEqual(member.joined, datetime.date(year=2003, month=1, day=30))
        member = ParliamentMember.find('Samsom', initials='D.M.', date=datetime.date(year=2016, month=6, day=1))
        self.assertEqual(member.person, person)
        self.assertEqual(member.joined, datetime.date(year=2012, month=9, day=20))
