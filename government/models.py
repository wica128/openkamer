import logging

from django.db import models

from person.models import Person

logger = logging.getLogger(__name__)


class Government(models.Model):
    name = models.CharField(max_length=200)
    date_formed = models.DateField()
    date_dissolved = models.DateField(blank=True, null=True)
    wikidata_id = models.CharField(max_length=200, blank=True)

    def prime_minister(self):
        return GovernmentPosition.objects.filter(
            position=GovernmentPosition.PRIME_MINISTER,
            government=self
        )[0].member_current()

    def deputy_prime_minister(self):
        return GovernmentPosition.objects.filter(
            position=GovernmentPosition.DEPUTY_PRIME_MINISTER,
            government=self
        )[0].member_current()

    def members_current(self):
        members = []
        positions = GovernmentPosition.objects.filter(government=self)
        for position in positions:
            members.append(position.member_current())
        return members

    def members(self):
        members = []
        positions = GovernmentPosition.objects.filter(government=self)
        for position in positions:
            for mem in position.members():
                members.append(mem)
        return members

    def ministries(self):
        return Ministry.objects.filter(government=self)

    def __str__(self):
        return str(self.name)


class Ministry(models.Model):
    name = models.CharField(max_length=200)
    government = models.ForeignKey(Government)

    def positions(self):
        return GovernmentPosition.objects.filter(ministry=self)

    def __str__(self):
        return str(self.name)


class GovernmentPosition(models.Model):
    MINISTER = 'MIN'
    SECRETARY_OF_STATE = 'SOS'
    PRIME_MINISTER = 'PMI'
    DEPUTY_PRIME_MINISTER = 'DPM'
    GOVERNMENT_POSITIONS = (
        (MINISTER, 'Minister'),
        (SECRETARY_OF_STATE, 'Secretary of State'),
        (PRIME_MINISTER, 'Prime Minister'),
        (DEPUTY_PRIME_MINISTER, 'Deputy Prime Minister'),
    )
    position = models.CharField(max_length=3, choices=GOVERNMENT_POSITIONS)
    ministry = models.ForeignKey(Ministry, blank=True, null=True)
    government = models.ForeignKey(Government, blank=True, null=True)

    def __str__(self):
        return self.get_position_display()

    def member_current(self):
        members = self.members()
        for member in members:
            if member.is_active():
                return member
        return None

    def members_inactive(self):
        members = self.members()
        members_inactive = []
        for member in members:
            if not member.is_active():
                members_inactive.append(member)
        return members_inactive

    def members(self):
        return GovernmentMember.objects.filter(position=self)

    @staticmethod
    def find_position_type(position_str):
        logger.info(position_str)
        position_str = position_str.lower()
        if 'viceminister-president' in position_str:
            return GovernmentPosition.DEPUTY_PRIME_MINISTER
        elif 'minister-president' in position_str:
            return GovernmentPosition.PRIME_MINISTER
        elif 'minister' in position_str:
            return GovernmentPosition.MINISTER
        elif 'staatssecretaris' in position_str:
            return GovernmentPosition.SECRETARY_OF_STATE
        return ''


class GovernmentMember(models.Model):
    person = models.ForeignKey(Person)
    position = models.ForeignKey(GovernmentPosition)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(self.person) + ' as ' + str(self.position)

    def is_active(self):
        return self.end_date is None
