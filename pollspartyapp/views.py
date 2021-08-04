from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from pollspartyapp.models import Poll,Option,ControlField,PollToken
from pollspartyapp.serializers import PollSerializer, OptionSerializer
from pollspartyapp.logic import CreatePollToken, HandleTokenExpired
from datetime import timedelta

# Views que só podem ser chamadas por usuários cadastrados tem "Auth", no nome.
class PollAuth(APIView):
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated]
	
	def post(self,request,params):
			#recebe json com parametros que vão servir para criação da poll.

			data = request.data #Pega os dados

			poll = Poll.objects.create(question=data['question'],user=request.user)#Cria a poll

			if data['config']['protect'] == True: #Verifica se a poll vai ser protegida(ou controlada)
				poll.protect = True
				poll.save()

			if data['config']['time'] != False: #Verifica se a poll tem tempo para expirar, se sim instaura o tempo necessário.
				token = CreatePollToken()
				while PollToken.objects.filter(token=token).exists():
					token = CreatePollToken()


				PollToken.objects.create(token=token,poll=poll)
				poll.expires_in = data['config']['time']
				poll.save()
			else:
				token = CreatePollToken()
				PollToken.objects.create(token=token,poll=poll)

							
			for option in data['options']:#cria as opções de resposta
				Option.objects.create(answer=data['options'][option],poll=poll)
									
			if data['config']['all_options']:#Adiciona opções com todas as alternativas, ou nenhuma alternativa.
				Option.objects.create(answer='All Options',poll=poll)
			elif data['config']['any_options']:
				Option.objects.create(answer='Any Option',poll=poll)

			serializer = PollSerializer(instance=poll)
			return JsonResponse(serializer.data,status=200,safe=False)

	def get(self,request,params):

		polls_query = Poll.objects.filter(user=request.user)#Procura todas as polls criadas pelo usuário	
		

		if params == 'all':#se o parametro "all" estiver na url, envia todas as informções de cada poll.
			serializer = serializer = PollSerializer(polls_query,many=True)
		else: #Senão, envia apenas os campos colocados na url, separados por: "-"
			url_fields = tuple(params.split('-'))
			serializer =  serializer = PollSerializer(polls_query,many=True,fields=url_fields)
			
			

		return JsonResponse(serializer.data,status=200,safe=False)

class PollUnAuth(APIView):


	def post(self,request,info,params):
		data = request.data
		poll = Poll.objects.get(options__pk=data.get('id'))

		if poll.protect:
			option = Option.objects.get(pk=data.get('id'))
			control = ControlField.objects.create(control_field=data['control_field'],option=option)
			option.votes += 1
			option.save()
			poll.total_votes +=1
			poll.save()
			serializer = PollSerializer(instance=poll)
			return JsonResponse(serializer.data,status=200,safe=False)
		else:
			option = Option.objects.get(pk=data.get('id'))
			option.votes += 1
			option.save()
			poll.total_votes +=1
			poll.save()			
			serializer = PollSerializer(instance=poll)
			return JsonResponse(serializer.data,status=200,safe=False)	

	def get(self,request,info,params):

		if PollToken.objects.filter(token=info).exists():
			poll = Poll.objects.get(token__token=info)
			if poll.expires_in == None:
				pass
			elif  timezone.now() - poll.token.time > timedelta(hours=poll.expires_in) and request.user == poll.user:
				new_token = HandleTokenExpired(poll)
				return JsonResponse({'error':'Token expired','new_token':new_token.token},status=400)
			elif timezone.now() - poll.token.time > timedelta(hours=poll.expires_in) and request.user != poll.user:
				HandleTokenExpired(poll)
				return JsonResponse({'error':'Token invalid or expired'},status=400)
			else:
				pass
		else:
			return JsonResponse({'error':'Token invalid or expired'},status=404)


		if params == 'all':
			poll_serializer = PollSerializer(instance=poll)
		else:
			url_fields = tuple(params.split('-'))
			poll_serializer =  PollSerializer(instance=poll,fields=url_fields)

		if request.user == poll.user:
			options = Option.objects.filter(poll=poll)
			options_serializer = OptionSerializer(options,many=True,fields=('id','controllers'))
			data = {'poll':poll_serializer.data,'insights':options_serializer.data}
			return JsonResponse(data,status=200)
		else:
			return JsonResponse(poll_serializer.data,status=200)

				

		


class CreateUser(APIView):
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated,IsAdminUser]

	def post(self,request):
		data = request.data
		try:
			user = User(username=data['username'],email=data['email'])
			user.set_password(data['password'])
			user.save()
			return JsonResponse({}, status=201)
		except:
			return JsonResponse({}, status=500)

class VerifEmail(APIView):
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated,IsAdminUser]

	def post(self,request):
		email = User.objects.filter(email=request.data['email']).exists()
		username = User.objects.filter(email=request.data['username']).exists()
		data = {'email':email,'username':username}
		return JsonResponse(data,status=200)
		