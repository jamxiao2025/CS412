from django.db import models
from datetime import datetime

class Voter(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    street_number = models.CharField(max_length=20)
    street_name = models.CharField(max_length=200)
    apartment_number = models.CharField(max_length=20, blank=True, null=True)
    zip_code = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    date_of_registration = models.DateField()
    party_affiliation = models.CharField(max_length=50)
    precinct_number = models.CharField(max_length=20)  # Updated to CharField to accommodate non-integer values
    v20state = models.BooleanField()
    v21town = models.BooleanField()
    v21primary = models.BooleanField()
    v22general = models.BooleanField()
    v23town = models.BooleanField()
    voter_score = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - Precinct {self.precinct_number}"

def load_data():
    Voter.objects.all().delete()

    filename = '/Users/jamesxiao/Downloads/newton_voters.csv'
    with open(filename, 'r', encoding='utf-8') as f:
        next(f)  # Skip header
        for line in f:
            try:
                fields = line.strip().split(',')
                
                # Convert fields to appropriate types
                date_of_birth = datetime.strptime(fields[7], '%Y-%m-%d').date()
                date_of_registration = datetime.strptime(fields[8], '%Y-%m-%d').date()
                v20state = fields[11].strip().upper() == 'TRUE'
                v21town = fields[12].strip().upper() == 'TRUE'
                v21primary = fields[13].strip().upper() == 'TRUE'
                v22general = fields[14].strip().upper() == 'TRUE'
                v23town = fields[15].strip().upper() == 'TRUE'
                voter_score = int(fields[16].strip())

                voter = Voter(
                    last_name=fields[1],
                    first_name=fields[2],
                    street_number=fields[3],
                    street_name=fields[4],
                    apartment_number=fields[5] or None,
                    zip_code=fields[6],
                    date_of_birth=date_of_birth,
                    date_of_registration=date_of_registration,
                    party_affiliation=fields[9],
                    precinct_number=fields[10],
                    v20state=v20state,
                    v21town=v21town,
                    v21primary=v21primary,
                    v22general=v22general,
                    v23town=v23town,
                    voter_score=voter_score
                )
                voter.save()
                print(f'Created voter: {voter}')
            except Exception as e:
                print(f"Exception on row: {fields}, Error: {e}")
