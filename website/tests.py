import logging

from django.contrib.auth.models import User
from django.test import Client
from django.test import TestCase
from django.urls import reverse

import scraper.documents

from person.models import Person

from government.models import Government

from parliament.models import ParliamentMember
from parliament.models import PartyMember
from parliament.models import PoliticalParty

from document.models import Agenda
from document.models import BesluitenLijst
from document.models import CategoryDossier
from document.models import CategoryDocument
from document.models import Dossier
from document.models import Document
from document.models import Kamerstuk
from document.models import Voting

import website.create

logger = logging.getLogger(__name__)


class TestExample(TestCase):

    def test_example(self):
        logger.info('BEGIN')
        logger.info('END')


class TestCreateParliament(TestCase):

    def test_create_parliament(self):
        website.create.create_parties()
        website.create.create_parliament_members()

    def test_create_parliament_from_wikidata(self):
        website.create.create_parliament_members_from_wikidata(max_results=20)


class TestCreateGovernment(TestCase):
    fixtures = ['person.json', 'parliament.json']

    @classmethod
    def setUpTestData(cls):
        rutte_2_wikidata_id = 'Q1638648'
        government = website.create.create_government(rutte_2_wikidata_id, max_members=4)

    def test_government_data(self):
        government = Government.objects.all()[0]
        self.assertEqual(government.name, 'Kabinet-Rutte II')
        members = government.members
        persons = []
        for member in members:
            persons.append(member.person)
        party_members = PartyMember.objects.filter(person__in=persons)
        self.assertTrue(len(party_members) >= len(persons))

    def test_governements_view(self):
        response = self.client.get(reverse('governments'))
        self.assertEqual(response.status_code, 200)

    def test_governement_view(self):
        governments = Government.objects.all()
        for government in governments:
            response = self.client.get(reverse('government', args=(government.slug,)))
            self.assertEqual(response.status_code, 200)

    def test_governement_current_view(self):
        governments = Government.objects.all()
        response = self.client.get(reverse('government-current'))
        self.assertEqual(response.status_code, 200)

    def test_api_governement(self):
        response = self.client.get('/api/government/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/ministry/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/government_member/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/government_position/')
        self.assertEqual(response.status_code, 200)


class TestCreateBesluitenLijst(TestCase):
    urls = [
        'https://www.tweedekamer.nl/downloads/document?id=4f728174-02ac-4822-a13f-66e0454a61c5&title=Besluitenlijst%20Financi%C3%ABn%20-%2026%20oktober%202016.pdf',
        'https://www.tweedekamer.nl/downloads/document?id=a1473f2c-79b1-47dd-b82c-7d7cd628e395&title=Besluitenlijst%20procedurevergadering%20Rijksuitgaven%20-%205%20juni%202014.pdf',
        'https://www.tweedekamer.nl/downloads/document?id=57fad866-5252-492f-9974-0ef396ba9080&title=Procedurevergadering%20RU%20-%2011%20oktober%202012%20VINDT%20GEEN%20DOORGANG.pdf',
        'https://www.tweedekamer.nl/downloads/document?id=a1342689-a7e4-4b17-a058-439005b22991&title=Herziene%20besluitenlijst%20e-mailprocedure%20BIZA%20-%2030%20mei%202016%20.pdf',
        'https://www.tweedekamer.nl/downloads/document?id=39d1fda2-24ce-4b11-b979-ce9b3b0ae7cf&title=Besluitenlijst%20procedurevergadering%20Buza%2017%20mrt.pdf',
        'https://www.tweedekamer.nl/downloads/document?id=8f30f5b6-eadc-4d9f-8ef4-59feed7d62f5&title=Besluitenlijst%20extra%20procedurevergadering%208%2F3%2F2011%20Buza%2FDef%20.pdf',
        # 'https://www.tweedekamer.nl/downloads/document?id=61a2686e-ec4a-4881-892b-04e215462ecd&title=Besluitenlijst%20extra%20procedurevergadering%20IM%20d.d.%207%20juni%202011.pdf',  # gives a TypeError, may be corrupt pdf or pdfminer bug
    ]

    def test_create_besluitenlijst_from_url(self):
        for url in self.urls:
            besluitenlijst = website.create.create_besluitenlijst(url)
            self.assertFalse(besluitenlijst.title == '')
            items = besluitenlijst.items()
            for item in items:
                self.assertFalse('Zaak:' in item.title)
                self.assertFalse('Besluit:' in item.title)
                self.assertFalse('Document:' in item.title)
                self.assertFalse('Noot:' in item.title)
                for case in item.cases():
                    self.assertFalse('Besluit:' in case.title)
                    self.assertFalse('Noot:' in case.title)
            dossier_ids = besluitenlijst.related_dossier_ids

    def test_create_besluitenlijst_to_commissions(self):
        url = 'https://www.tweedekamer.nl/downloads/document?id=a458091b-5963-4b5d-becb-664a10f55b8f&title=Besluitenlijst%20extra%20procedurevergadering%20werkbezoek%20Auschwitz.pdf'
        besluitenlijst = website.create.create_besluitenlijst(url)
        self.assertEqual(besluitenlijst.commission, 'vaste commissie voor Volksgezondheid, Welzijn en Sport')


class TestFindParliamentMembers(TestCase):
    fixtures = ['person.json', 'parliament.json']

    def test_find_member(self):
        surname = 'Zijlstra'
        forename = 'Halbe'
        initials = 'H.'
        member = ParliamentMember.find(surname=surname, initials=initials)
        self.assertEqual(member.person.forename, forename)

    def test_find_member_surname_prefix(self):
        surname = 'Weyenberg van'
        forename = 'Steven'
        initials = 'S.P.R.A.'
        member = ParliamentMember.find(surname=surname, initials=initials)
        self.assertEqual(member.person.forename, forename)
        surname = 'van Weyenberg'
        member = ParliamentMember.find(surname=surname, initials=initials)
        self.assertEqual(member.person.forename, forename)

    def test_find_member_non_ascii(self):
        surname = 'Koser Kaya'
        forename = 'Fatma'
        initials = 'F.'
        member = ParliamentMember.find(surname=surname, initials=initials)
        self.assertEqual(member.person.forename, forename)
        surname = 'Koşer Kaya'
        member = ParliamentMember.find(surname=surname, initials=initials)
        self.assertEqual(member.person.forename, forename)


class TestFindOriginalKamerstukId(TestCase):
    dossier_id = 33885

    def test_find_original_motie(self):
        expected_result = '33885-18'
        title = 'Gewijzigde motie van het lid Segers c.s. (t.v.v. 33885, nr.18) over de bevoegdheden van de Koninklijke Marechaussee'
        original_id = website.create.find_original_kamerstuk_id(self.dossier_id, title)
        self.assertEqual(original_id, expected_result)

    def test_find_original_amendement(self):
        title = 'Gewijzigd amendement van het lid Oskam ter vervanging van nr. 9 waarmee een verbod op illegaal pooierschap in het wetboek van strafrecht wordt geintroduceerd'
        expected_result = '33885-9'
        original_id = website.create.find_original_kamerstuk_id(self.dossier_id, title)
        self.assertEqual(original_id, expected_result)

    def test_find_original_voorstel_van_wet(self):
        title = 'Wijziging van de Wet regulering prostitutie en bestrijding misstanden seksbranche; Gewijzigd voorstel van wet '
        expected_result = '33885-voorstel_van_wet'
        original_id = website.create.find_original_kamerstuk_id(self.dossier_id, title)
        self.assertEqual(original_id, expected_result)

    def test_find_original_none(self):
        title = 'Motie van de leden Volp en Kooiman over monitoring van het nulbeleid'
        expected_result = ''
        original_id = website.create.find_original_kamerstuk_id(self.dossier_id, title)
        self.assertEqual(original_id, expected_result)


class TestPersonView(TestCase):
    fixtures = ['person.json']

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

    def test_persons_overview(self):
        response = self.client.get(reverse('persons'))
        self.assertEqual(response.status_code, 200)

    def test_person_overview(self):
        persons = Person.objects.all()[:10]
        for person in persons:
            response = self.client.get(reverse('person', args=(person.slug,)))
            self.assertEqual(response.status_code, 200)

    def test_person_check_view(self):
        response = self.client.get(reverse('persons-check'))
        self.assertEqual(response.status_code, 200)


class TestCreatePerson(TestCase):
    wikidata_id_ss = 'Q516335'
    name_ss = 'Sjoerd Sjoerdsma'

    def test_create_person_from_wikidata_id(self):
        person = website.create.create_person(self.wikidata_id_ss, add_initials=True)
        self.check_sjoerd(person)

    def test_create_person_from_wikidata_id_and_fullname(self):
        person = website.create.create_person(self.wikidata_id_ss, self.name_ss, add_initials=True)
        self.check_sjoerd(person)

    def check_sjoerd(self, person):
        self.assertTrue('Sjoerdsma' in person.surname)
        self.assertEqual(person.forename, 'Sjoerd')
        self.assertEqual(person.surname, 'Sjoerdsma')
        self.assertEqual(person.initials, 'Sj.W.')

    def test_jeroen_wikidata(self):
        wikidata_id = 'Q17428405'
        person = website.create.create_person(wikidata_id)
        self.assertEqual(person.forename, 'Jeroen')
        self.assertEqual(person.surname_prefix, 'van')
        self.assertEqual(person.surname, 'Wijngaarden')
        self.assertEqual(person.fullname(), 'Jeroen van Wijngaarden')

    def test_jan_kees_wikidata(self):
        wikidata_id = 'Q1666631'
        person = website.create.create_person(wikidata_id)
        self.assertEqual(person.forename, 'Jan Kees')
        self.assertEqual(person.surname_prefix, 'de')
        self.assertEqual(person.surname, 'Jager')
        self.assertEqual(person.fullname(), 'Jan Kees de Jager')

    def test_eelke_wikidata(self):
        wikidata_id = 'Q2710877'
        person = website.create.create_person(wikidata_id)
        self.assertEqual(person.forename, 'Eeke')
        self.assertEqual(person.surname_prefix, 'van der')
        self.assertEqual(person.surname, 'Veen')
        self.assertEqual(person.fullname(), 'Eeke van der Veen')

    def test_koser_kaya_wikidata(self):
        wikidata_id = 'Q467610'
        person = website.create.create_person(wikidata_id)
        self.assertEqual(person.forename, 'Fatma')
        self.assertEqual(person.surname_prefix, '')
        self.assertEqual(person.surname, 'Koşer Kaya')
        self.assertEqual(person.fullname(), 'Fatma Koşer Kaya')


class TestWebsite(TestCase):
    fixtures = ['person.json', 'parliament.json', 'government.json']

    @classmethod
    def setUpTestData(cls):
        website.create.create_dossier_retry_on_error(33885)
        website.create.create_dossier_retry_on_error(33506)
        website.create.create_besluitenlijsten(max_commissions=3, max_results_per_commission=5)
        cls.client = Client()

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_persons_overview(self):
        response = self.client.get(reverse('persons'))
        self.assertEqual(response.status_code, 200)

    def test_person_overview(self):
        persons = Person.objects.all()[:10]
        for person in persons:
            response = self.client.get(reverse('person', args=(person.slug,)))
            self.assertEqual(response.status_code, 200)

    def test_person_autocomplete_view(self):
        response = self.client.get(reverse('person-autocomplete') + '?q=samsom')
        self.assertEqual(response.status_code, 200)

    def test_dossiers_overview(self):
        response = self.client.get(reverse('wetsvoorstellen'))
        self.assertEqual(response.status_code, 200)

    def test_dossiers_filter_view(self):
        ivo = Person.objects.filter(forename='Ivo', surname='Opstelten')[0]
        response = self.client.get(reverse('wetsvoorstellen') + '?title=wet&submitter=' + str(ivo.id) + '&voting_result=AAN')
        self.assertEqual(response.status_code, 200)

    def test_dossier_views(self):
        dossiers = Dossier.objects.all()
        for dossier in dossiers:
            response = self.client.get(reverse('dossier-tiles', args=(dossier.dossier_id,)))
            self.assertEqual(response.status_code, 200)

    def test_timeline_views(self):
        dossiers = Dossier.objects.all()
        for dossier in dossiers:
            response = self.client.get(reverse('dossier-timeline', args=(dossier.dossier_id,)))
            self.assertEqual(response.status_code, 200)

    def test_timeline_horizontal_views(self):
        dossiers = Dossier.objects.all()
        for dossier in dossiers:
            response = self.client.get(reverse('dossier-timeline-horizontal', args=(dossier.dossier_id,)))
            self.assertEqual(response.status_code, 200)
            response = self.client.get('/dossier/timeline/horizontal/json/?dossier_pk=' + str(dossier.id))
            self.assertEqual(response.status_code, 200)

    def test_document_view(self):
        documents = Document.objects.all()
        for document in documents:
            response = self.client.get(reverse('document', args=(document.document_id,)))
            self.assertEqual(response.status_code, 200)

    def test_kamerstuk_view(self):
        kamerstukken = Kamerstuk.objects.all()
        for kamerstuk in kamerstukken:
            response = self.client.get(reverse('kamerstuk', args=(kamerstuk.id_main, kamerstuk.id_sub,)))
            self.assertEqual(response.status_code, 200)

    def test_kamerstuk_modifications(self):
        kamerstuk_08 = Kamerstuk.objects.get(id_main='33885', id_sub='8')
        kamerstuk_11 = Kamerstuk.objects.get(id_main='33885', id_sub='11')
        kamerstuk_29 = Kamerstuk.objects.get(id_main='33885', id_sub='29')
        kamerstuk_original = Kamerstuk.objects.get(id_main='33885', id_sub='2')
        self.assertEqual(kamerstuk_08.original, kamerstuk_original)
        self.assertEqual(kamerstuk_11.original, kamerstuk_original)
        self.assertEqual(kamerstuk_29.original, kamerstuk_original)
        modifications = [kamerstuk_08, kamerstuk_11, kamerstuk_29]
        for modification in kamerstuk_original.modifications:
            self.assertTrue(modification in modifications)

    def test_agendas_view(self):
        response = self.client.get('/agendas/')
        self.assertEqual(response.status_code, 200)

    def test_agenda_view(self):
        agendas = Agenda.objects.all()
        for agenda in agendas:
            response = self.client.get('/agenda/' + str(agenda.id) + '/')
            self.assertEqual(response.status_code, 200)

    def test_votings_overview(self):
        response = self.client.get(reverse('votings'))
        self.assertEqual(response.status_code, 200)

    def test_voting_view(self):
        votings = Voting.objects.all()
        for voting in votings:
            if voting.is_dossier_voting:
                response = self.client.get(reverse('voting-dossier', args=(voting.dossier.dossier_id,)))
            else:
                response = self.client.get(reverse('voting-kamerstuk', args=(voting.kamerstuk.id_main, voting.kamerstuk.id_sub,)))
            self.assertEqual(response.status_code, 200)

    def test_parties_overview(self):
        response = self.client.get(reverse('parties'))
        self.assertEqual(response.status_code, 200)

    def test_party_view(self):
        parties = PoliticalParty.objects.all()
        for party in parties:
            response = self.client.get(reverse('party', args=(party.slug,)))
            self.assertEqual(response.status_code, 200)

    def test_besluitenlijsten_view(self):
        response = self.client.get(reverse('besluitenlijsten'))
        self.assertEqual(response.status_code, 200)

    def test_besluitenlijst_view(self):
        lijsten = BesluitenLijst.objects.all()
        for lijst in lijsten:
            response = self.client.get(reverse('besluitenlijst', args=(lijst.activity_id,)))
            self.assertEqual(response.status_code, 200)

    def test_parliament_members_overview(self):
        response = self.client.get(reverse('parliament-members'))
        self.assertEqual(response.status_code, 200)

    def test_parliament_members_check(self):
        password = 'adminpassword'
        my_admin = User.objects.create_superuser('adminuser', 'admin@admin.com', password)
        self.client.login(username=my_admin.username, password=password)
        response = self.client.get(reverse('parliament-members-check'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_database_dumps_view(self):
        response = self.client.get(reverse('database-dumps'))
        self.assertEqual(response.status_code, 200)

    def test_stats_view(self):
        response = self.client.get(reverse('stats'))
        self.assertEqual(response.status_code, 200)

    def test_data_stats_view(self):
        response = self.client.get(reverse('stats-data'))
        self.assertEqual(response.status_code, 200)

    def test_plot_example_view(self):
        response = self.client.get('/stats/exampleplots/')
        self.assertEqual(response.status_code, 200)

    def test_api_homepage(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)

    def test_api_person(self):
        response = self.client.get('/api/person/')
        self.assertEqual(response.status_code, 200)

    def test_api_parliament(self):
        response = self.client.get('/api/parliament/')
        self.assertEqual(response.status_code, 200)

    def test_api_parliament_member(self):
        response = self.client.get('/api/parliament_member/')
        self.assertEqual(response.status_code, 200)

    def test_api_party(self):
        response = self.client.get('/api/party/')
        self.assertEqual(response.status_code, 200)

    def test_api_party_member(self):
        response = self.client.get('/api/party_member/')
        self.assertEqual(response.status_code, 200)

    def test_api_document(self):
        response = self.client.get('/api/document/')
        self.assertEqual(response.status_code, 200)

    def test_api_kamerstuk(self):
        response = self.client.get('/api/kamerstuk/')
        self.assertEqual(response.status_code, 200)

    def test_api_submitter(self):
        response = self.client.get('/api/submitter/')
        self.assertEqual(response.status_code, 200)

    def test_api_dossier(self):
        response = self.client.get('/api/dossier/')
        self.assertEqual(response.status_code, 200)

    def test_api_voting(self):
        response = self.client.get('/api/voting/')
        self.assertEqual(response.status_code, 200)

    def test_api_voteparty(self):
        response = self.client.get('/api/vote_party/')
        self.assertEqual(response.status_code, 200)

    def test_api_voteindividual(self):
        response = self.client.get('/api/vote_individual/')
        self.assertEqual(response.status_code, 200)

    def test_api_category_dossier(self):
        response = self.client.get('/api/category_dossier/')
        self.assertEqual(response.status_code, 200)

    def test_api_category_document(self):
        response = self.client.get('/api/category_document/')
        self.assertEqual(response.status_code, 200)


class TestCategory(TestCase):

    def test_create_dossier_category_from_string(self):
        self.create_category_from_string(CategoryDossier)

    def test_create_document_category_from_string(self):
        self.create_category_from_string(CategoryDocument)

    def create_category_from_string(self, category_class):
        text = 'Zorg en gezondheid | Ziekten en behandelingen'
        expected_names = [
            'zorg en gezondheid',
            'ziekten en behandelingen',
        ]
        categories = website.create.get_categories(text, category_class)
        self.assertEqual(len(categories), 2)
        for index, category in enumerate(categories):
            self.assertEqual(expected_names[index], category.name)
        text = '  Zorg en Gezondheid|  Ziekten en Behandelingen'
        expected_names = [
            'zorg en gezondheid',
            'ziekten en behandelingen',
        ]
        categories = website.create.get_categories(text, category_class)
        self.assertEqual(len(categories), 2)
        for index, category in enumerate(categories):
            self.assertEqual(expected_names[index], category.name)


class TestDocumentLinks(TestCase):

    @classmethod
    def setUpTestData(cls):
        dosser_id = '33569'
        dossier = Dossier.objects.create(dossier_id=dosser_id)
        document = Document.objects.create(dossier=dossier)
        Kamerstuk.objects.create(document=document, id_main=dosser_id, id_sub='1')
        Kamerstuk.objects.create(document=document, id_main=dosser_id, id_sub='2')
        Kamerstuk.objects.create(document=document, id_main=dosser_id, id_sub='3')

    def test_update_document_html_links(self):
        url = 'https://zoek.officielebekendmakingen.nl/kst-33771-8.html'
        document_id, content_html, title = scraper.documents.get_document_id_and_content(url)
        website.create.update_document_html_links(content_html)

    def test_create_new_url(self):
        url = 'kst-33569-1.html'
        url_expected = '/kamerstuk/33569/1/'
        self.check_url(url, url_expected)
        url = 'kst-33569-A.html'
        url_expected = 'https://zoek.officielebekendmakingen.nl/kst-33569-A.html'
        self.check_url(url, url_expected)
        url = 'http://www.google.com'
        url_expected = 'http://www.google.com'
        self.check_url(url, url_expected)
        url = '#anchor-1'
        url_expected = '#anchor-1'
        self.check_url(url, url_expected)

    def check_url(self, url, url_expected):
        new_url = website.create.create_new_url(url)
        self.assertEqual(new_url, url_expected)
        url = new_url
        new_url = website.create.create_new_url(url)
        self.assertEqual(new_url, url)