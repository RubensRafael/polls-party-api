import random
from pollspartyapp.models import PollToken

def CreatePollToken():
	population = '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	sort = random.choices(population,k=6)
	token = ''.join(sort)
	return token


def HandleTokenExpired(poll):
	PollToken.objects.get(poll=poll).delete()
	token = CreatePollToken()
	while PollToken.objects.filter(token=token).exists():
		token = CreatePollToken()

	new_token = PollToken.objects.create(token=token,poll=poll)
	return new_token