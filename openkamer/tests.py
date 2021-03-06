import datetime

from django.urls import reverse
from django.test import TestCase

from person.models import Person

from government.models import Government

from parliament.models import Parliament
from parliament.models import ParliamentMember
from parliament.models import PartyMember
from parliament.models import PoliticalParty

from document.models import Document
from document.models import Dossier
from document.models import Kamervraag
from document.models import Voting

import openkamer.besluitenlijst
import openkamer.document
import openkamer.dossier
import openkamer.kamerstuk
import openkamer.kamervraag
import openkamer.parliament
import openkamer.voting


class TestCreatePerson(TestCase):
    wikidata_id_ss = 'Q516335'
    name_ss = 'Sjoerd Sjoerdsma'

    def test_create_person_from_wikidata_id(self):
        person = openkamer.parliament.get_or_create_person(self.wikidata_id_ss, add_initials=True)
        self.check_sjoerd(person)

    def test_create_person_from_wikidata_id_and_fullname(self):
        person = openkamer.parliament.get_or_create_person(self.wikidata_id_ss, self.name_ss, add_initials=True)
        self.check_sjoerd(person)

    def check_sjoerd(self, person):
        self.assertTrue('Sjoerdsma' in person.surname)
        self.assertEqual(person.forename, 'Sjoerd')
        self.assertEqual(person.surname, 'Sjoerdsma')
        self.assertEqual(person.initials, 'S.W.')

    def test_jeroen_wikidata(self):
        wikidata_id = 'Q17428405'
        person = openkamer.parliament.get_or_create_person(wikidata_id)
        self.assertEqual(person.forename, 'Jeroen')
        self.assertEqual(person.surname_prefix, 'van')
        self.assertEqual(person.surname, 'Wijngaarden')
        self.assertEqual(person.fullname(), 'Jeroen van Wijngaarden')

    def test_jan_kees_wikidata(self):
        wikidata_id = 'Q1666631'
        person = openkamer.parliament.get_or_create_person(wikidata_id)
        self.assertEqual(person.forename, 'Jan Kees')
        self.assertEqual(person.surname_prefix, 'de')
        self.assertEqual(person.surname, 'Jager')
        self.assertEqual(person.fullname(), 'Jan Kees de Jager')

    def test_eelke_wikidata(self):
        wikidata_id = 'Q2710877'
        person = openkamer.parliament.get_or_create_person(wikidata_id)
        self.assertEqual(person.forename, 'Eeke')
        self.assertEqual(person.surname_prefix, 'van der')
        self.assertEqual(person.surname, 'Veen')
        self.assertEqual(person.fullname(), 'Eeke van der Veen')

    def test_koser_kaya_wikidata(self):
        wikidata_id = 'Q467610'
        person = openkamer.parliament.get_or_create_person(wikidata_id)
        self.assertEqual(person.forename, 'Fatma')
        self.assertEqual(person.surname_prefix, '')
        self.assertEqual(person.surname, 'Koşer Kaya')
        self.assertEqual(person.fullname(), 'Fatma Koşer Kaya')

    def test_submitter(self):
        date = datetime.date(day=30, month=1, year=2010)
        p1 = Person.objects.create(forename='Jeroen', surname='Dijsselbloem', initials='J.R.V.A.')
        parliament = Parliament.get_or_create_tweede_kamer()
        ParliamentMember.objects.create(person=p1, parliament=parliament, joined=datetime.date(2010, 1, 1), left=datetime.date(2010, 2, 1))
        document = Document.objects.create(date_published=datetime.date.today())
        submitter = openkamer.document.create_submitter(document, 'L. van Tongeren', date)
        self.assertEqual(submitter.person.initials, 'L.')
        submitter = openkamer.document.create_submitter(document, 'Tongeren C.S.', date)
        self.assertEqual(submitter.person.initials, '')
        submitter = openkamer.document.create_submitter(document, 'DIJSSELBLOEM', date)
        self.assertEqual(submitter.person, p1)
        p5 = Person.objects.create(forename='', surname='Dijsselbloem', initials='')
        submitter = openkamer.document.create_submitter(document, 'DIJSSELBLOEM', date)
        self.assertEqual(submitter.person, p1)
        p2 = Person.objects.create(forename='Pieter', surname='Dijsselbloem', initials='P.')
        ParliamentMember.objects.create(person=p2, parliament=parliament, joined=datetime.date(2010, 1, 1), left=datetime.date(2010, 2, 1))
        submitter = openkamer.document.create_submitter(document, 'DIJSSELBLOEM', date)
        self.assertNotEqual(submitter.person, p1)
        self.assertNotEqual(submitter.person, p2)
        p3 = Person.objects.create(forename='Jan Jacob', surname_prefix='van', surname='Dijk', initials='J.J.')
        p4 = Person.objects.create(forename='Jasper', surname_prefix='van', surname='Dijk', initials='J.J.')
        submitter = openkamer.document.create_submitter(document, 'JAN JACOB VAN DIJK', date)
        self.assertEqual(submitter.person, p3)
        submitter = openkamer.document.create_submitter(document, 'JASPER VAN DIJK', date)
        self.assertEqual(submitter.person, p4)

    def test_submitter_empty(self):
        p1 = Person.objects.create(forename='', surname='', initials='')
        document = Document.objects.create(date_published=datetime.date.today())
        submitter = openkamer.document.create_submitter(document, '', datetime.date.today())
        self.assertEqual(submitter.person, p1)

    def test_submitter_surname_only(self):
        p1 = Person.objects.create(forename='', surname='van Raak', initials='')
        document = Document.objects.create(date_published=datetime.date.today())
        submitter = openkamer.document.create_submitter(document, 'VAN RAAK', datetime.date.today())
        self.assertEqual(submitter.person, p1)
        p2 = Person.objects.create(forename='', surname_prefix='van der', surname='Ham', initials='')
        submitter = openkamer.document.create_submitter(document, 'Ham, van der', datetime.date.today())  # example: https://zoek.officielebekendmakingen.nl/kst-30830-13
        self.assertEqual(submitter.person, p2)


class TestFindOriginalKamerstukId(TestCase):
    dossier_id = 33885

    def test_find_original_motie(self):
        expected_result = '33885-18'
        title = 'Gewijzigde motie van het lid Segers c.s. (t.v.v. 33885, nr.18) over de bevoegdheden van de Koninklijke Marechaussee'
        original_id = openkamer.kamerstuk.find_original_kamerstuk_id(self.dossier_id, title)
        self.assertEqual(original_id, expected_result)

    def test_find_original_amendement(self):
        title = 'Gewijzigd amendement van het lid Oskam ter vervanging van nr. 9 waarmee een verbod op illegaal pooierschap in het wetboek van strafrecht wordt geintroduceerd'
        expected_result = '33885-9'
        original_id = openkamer.kamerstuk.find_original_kamerstuk_id(self.dossier_id, title)
        self.assertEqual(original_id, expected_result)

    def test_find_original_voorstel_van_wet(self):
        title = 'Wijziging van de Wet regulering prostitutie en bestrijding misstanden seksbranche; Gewijzigd voorstel van wet '
        expected_result = '33885-voorstel_van_wet'
        original_id = openkamer.kamerstuk.find_original_kamerstuk_id(self.dossier_id, title)
        self.assertEqual(original_id, expected_result)

    def test_find_original_none(self):
        title = 'Motie van de leden Volp en Kooiman over monitoring van het nulbeleid'
        expected_result = ''
        original_id = openkamer.kamerstuk.find_original_kamerstuk_id(self.dossier_id, title)
        self.assertEqual(original_id, expected_result)


class TestCreateParliament(TestCase):

    @classmethod
    def setUpTestData(cls):
        openkamer.parliament.create_parties()

    def test_create_parliament_from_wikidata(self):
        openkamer.parliament.create_parliament_members(max_results=20)


class TestCreateParliamentMember(TestCase):

    def test_create_parliament_member_from_wikidata_martin(self):
        person_wikidata_id = 'Q2801440'  # Martin van Rooijen
        parliament = Parliament.get_or_create_tweede_kamer()
        members = openkamer.parliament.create_parliament_member_from_wikidata_id(parliament, person_wikidata_id)
        self.assertEqual(len(members), 1)
        party_expected = PoliticalParty.find_party('50plus')
        self.assertEqual(members[0].party, party_expected)

    def test_create_parliament_member_from_wikidata_kuzu(self):
        person_wikidata_id = 'Q616635'  # Tunahan Kuzu
        parliament = Parliament.get_or_create_tweede_kamer()
        members = openkamer.parliament.create_parliament_member_from_wikidata_id(parliament, person_wikidata_id)
        self.assertEqual(len(members), 3)
        party_expected_0 = PoliticalParty.find_party('PvdA')
        party_expected_1 = PoliticalParty.find_party('GrKÖ')
        party_expected_2 = PoliticalParty.find_party('DENK')
        self.assertEqual(members[0].party, party_expected_0)
        self.assertEqual(members[1].party, party_expected_1)
        self.assertEqual(members[2].party, party_expected_2)


class TestCreatePoliticalParty(TestCase):

    def test_create_socialist_party(self):
        party = openkamer.parliament.create_party('Socialistische Partij', 'SP')
        self.assertEqual(party.wikidata_id, 'Q849580')

    def test_create_party_wikidata_id(self):
        wikidata_id = 'Q849580'  # SP
        party = openkamer.parliament.create_party_wikidata(wikidata_id)
        self.assertEqual(party.name, 'Socialistische Partij')
        self.assertEqual(party.name_short, 'SP')
        self.assertEqual(party.founded, datetime.date(year=1971, month=10, day=22))
        self.assertEqual(party.slug, 'sp')


class TestCreateGovernment(TestCase):
    fixtures = ['person.json', 'parliament.json']

    @classmethod
    def setUpTestData(cls):
        rutte_2_wikidata_id = 'Q1638648'
        government = openkamer.parliament.create_government(rutte_2_wikidata_id, max_members=4)

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
            besluitenlijst = openkamer.besluitenlijst.create_besluitenlijst(url)
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
        besluitenlijst = openkamer.besluitenlijst.create_besluitenlijst(url)
        self.assertEqual(besluitenlijst.commission, 'vaste commissie voor Volksgezondheid, Welzijn en Sport')


class TestKamervraag(TestCase):

    def test_create_kamervraag(self):
        infos = Kamervraag.get_kamervragen_info(2016)
        document, vraagnummer, related_document_ids = openkamer.kamervraag.create_kamervraag_document(infos[0]['overheidnl_document_id'])
        # print(metadata)

    def test_get_receiver_from_title(self):
        receiver_expected = 'Staatssecretaris van Infrastructuur en Milieu'
        title = "Vragen van het lid Monasch (PvdA) aan de Staatssecretaris van Infrastructuur en Milieu over het artikel «Schiphol kan verder met uitbreiding» (ingezonden 23 november 2015)."
        receiver = openkamer.kamervraag.get_receiver_from_title(title)
        self.assertEqual(receiver, receiver_expected)

    def test_parse_footnotes(self):
        footnote_html = """
        <div id="noten">
            <hr />
            <div class="voet noot snp-mouseoffset snb-pinned notedefault" id="supernote-note-ID-2016Z00047-d37e61">
               <h5 class="note-close"><a class="note-close" href="#close-ID-2016Z00047-d37e61">X</a> Noot
               </h5><sup><span class="nootnum"><a id="ID-2016Z00047-d37e61" name="ID-2016Z00047-d37e61"></a>1</span></sup><p><a href="http://nos.nl/l/2077649" title="link naar http://nos.nl/l/2077649" class="externe_link">http://nos.nl/l/2077649</a></p>
            </div>
            <div class="voet noot snp-mouseoffset snb-pinned notedefault" id="supernote-note-ID-2016Z00047-d37e69">
               <h5 class="note-close"><a class="note-close" href="#close-ID-2016Z00047-d37e69">X</a> Noot
               </h5><sup><span class="nootnum"><a id="ID-2016Z00047-d37e69" name="ID-2016Z00047-d37e69"></a>2</span></sup><p>VOG: verklaring omtrent gedrag</p>
            </div>
        </div>
        """
        footnotes = openkamer.kamervraag.create_footnotes(footnote_html)

    def test_find_question_in_html(self):
        document = Document.objects.create(content_html="""<div class="vraag">
            <h2 class="stuktitel no-toc"><a id="d16e43" name="d16e43"></a>Vraag 1
            </h2>
            <p>Wat is uw reactie op het bericht «Veel beginnende ggz-krachten krijgen alleen onkostenvergoeding»?<a class="nootnum supernote-click-ID-2016Z00020-d37e57" href="#ID-2016Z00020-d37e57">1</a> <a class="nootnum supernote-click-n2" href="#n2">2</a></p>
         </div>
         <div class="vraag">
            <h2 class="stuktitel no-toc"><a id="d16e55" name="d16e55"></a>Vraag 2
            </h2>
            <p>Bent u van mening dat hier sprake is van een arbeidsrelatie waarbij loon verschuldigd
               is? Zo ja, wat gaat u hieraan doen? Zo nee, waarom niet?
            </p>
         </div>
         <div class="vraag">
            <h2 class="stuktitel no-toc"><a id="d16e62" name="d16e62"></a>Vraag 3
            </h2>
            <p>Bent u van mening dat, indien er geen sprake is van een boventallige functie waarbij
               een leerdoel centraal staat, er met terugwerkende kracht voldaan moet worden aan het
               wettelijk minimumloon dan wel de van toepassing zijnde cao? Zo ja, wat gaat u hieraan
               doen? Zo nee, waarom niet?
            </p>
         </div>
         <div class="vraag">
            <h2 class="stuktitel no-toc"><a id="d16e69" name="d16e69"></a>Vraag 4
            </h2>
            <p>Bent u bereid de Inspectie SZW per direct onderzoek te laten doen naar deze situatie?
               Zo ja, op welke termijn kunt u de Kamer over de resultaten informeren? Zo nee, waarom
               niet?
            </p>
         </div>""")
        kamervraag = Kamervraag.objects.create(document=document, vraagnummer='dummy')
        openkamer.kamervraag.create_vragen_from_kamervraag_html(kamervraag)

    def test_create_kamervragen(self):
        n_create = 4
        kamervragen, kamerantwoorden = openkamer.kamervraag.create_kamervragen('2016', max_n=n_create, skip_if_exists=False)
        for kamervraag in kamervragen:
            self.assertTrue(kamervraag.kamerantwoord)
        self.assertEqual(len(kamervragen), n_create)
        self.assertEqual(len(kamerantwoorden), n_create)

    def test_postponed_answer(self):
        overheid_id = 'kv-tk-2017Z07318'
        kamervraag, related_document_ids = openkamer.kamervraag.create_kamervraag(overheid_id)
        self.assertEqual(len(related_document_ids), 2)
        kamerantwoord, mededelingen = openkamer.kamervraag.create_related_kamervraag_documents(kamervraag, related_document_ids)
        self.assertTrue(kamerantwoord)
        self.assertEqual(len(mededelingen), 1)
        self.assertTrue(mededelingen[0].text)

    def test_update_or_create(self):
        overheid_doc_id = 'kv-tk-2017Z07318'
        kamervraag, related_document_ids = openkamer.kamervraag.create_kamervraag(overheid_doc_id)
        documents = Document.objects.all()
        self.assertEqual(documents.count(), 1)
        kamervraag, related_document_ids = openkamer.kamervraag.create_kamervraag(overheid_doc_id)
        documents = Document.objects.all()
        self.assertEqual(documents.count(), 1)


class TestKamerantwoord(TestCase):

    def test_combined_answers(self):
        overheidnl_document_id = 'ah-tk-20152016-1580'
        kamerantwoord, mededeling = openkamer.kamervraag.create_kamerantwoord(overheidnl_document_id)
        self.assertEqual(kamerantwoord.antwoord_set.count(), 4)
        antwoorden = kamerantwoord.antwoord_set.all()
        self.assertEqual(antwoorden[0].see_answer_nr, None)
        self.assertEqual(antwoorden[1].see_answer_nr, None)
        self.assertEqual(antwoorden[2].see_answer_nr, 2)
        self.assertEqual(antwoorden[3].see_answer_nr, None)


class TestVoting(TestCase):

    def test_dossier_voting_controversieel(self):
        dossier_id = '29282'
        dossier = Dossier.objects.create(dossier_id=dossier_id)
        openkamer.voting.create_votings(dossier_id)
        votings = Voting.objects.all()
        self.assertEqual(votings.count(), 66)
        for voting in votings:
            self.assertEqual(dossier.id, voting.dossier.id)
            self.assertNotEqual(voting.source_url, '')
        dossier.delete()
        votings = Voting.objects.all()
        self.assertEqual(votings.count(), 0)
