from django.http import JsonResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from pollspartyapp.models import Poll,Option,ControlField,PollToken, PollUser
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

			try:
				poll = Poll.objects.create(question=data['question'],user=request.user)#Cria a poll

				for option in data['options']:#cria as opções de resposta
					Option.objects.create(answer=data['options'][option],poll=poll)
			except KeyError:
				return JsonResponse({'error':"The fields: 'question' and 'options' are required."}, status=400)


			try:
				if data['config']['protect'] == True: #Verifica se a poll vai ser protegida(ou controlada)
					poll.protect = True
					poll.save()
			except KeyError:
				pass	

			try:
				 #Verifica se a poll tem tempo para expirar, se sim instaura o tempo necessário.
				if data['config']['time'] != False:
					poll.expires_in = data['config']['time']
					poll.save()
			except KeyError:
				pass


			#Adiciona opções com todas as alternativas, ou nenhuma alternativa.
			try:
				if data['config']['all_options']:
					Option.objects.create(answer='All Options',poll=poll)
			except KeyError:
				pass
			try:

				if data['config']['no_option']:
					Option.objects.create(answer='No Option',poll=poll)

			except KeyError:	
				pass


			token = CreatePollToken()
			while PollToken.objects.filter(token=token).exists():
				token = CreatePollToken()

			PollToken.objects.create(token=token,poll=poll)


			serializer = PollSerializer(instance=poll)
			return JsonResponse(serializer.data,status=200,safe=False)

	def get(self,request,params):

		polls_query = Poll.objects.filter(user=request.user)#Procura todas as polls criadas pelo usuário	
		
		
		for poll in polls_query:
			if poll.expires_in == None:
				pass
			elif  timezone.now() - poll.token.time > timedelta(hours=poll.expires_in) and request.user == poll.user:
				HandleTokenExpired(poll)
			else:
				pass



		if params == 'all':#se o parametro "all" estiver na url, envia todas as informções de cada poll.
			serializer = serializer = PollSerializer(polls_query,many=True)
		else: #Senão, envia apenas os campos colocados na url, separados por: "-"
			url_fields = tuple(params.split('-'))
			serializer =  serializer = PollSerializer(polls_query,many=True,fields=url_fields)
			
			

		return JsonResponse(serializer.data,status=200,safe=False)

#Duas funções auxiliares para as proximas duas Views

#Retorna os paramentros de url especificos, e (caso logado) dá informações adicionais
def PollsParametersUnAuth(params,poll,request):

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

#Verifica se o token espirou e atualiza
def PollTokenVerif(info,request):
	
	if PollToken.objects.filter(token=info).exists():
		poll = Poll.objects.get(token__token=info)
		if poll.expires_in == None:
			return poll
		elif  timezone.now() - poll.token.time > timedelta(hours=poll.expires_in) and request.user == poll.user:
			new_token = HandleTokenExpired(poll)
			return JsonResponse({'error':'Token expired','new_token':new_token.token},status=400)
		elif timezone.now() - poll.token.time > timedelta(hours=poll.expires_in) and request.user != poll.user:
			HandleTokenExpired(poll)
			return JsonResponse({'error':'Token invalid or expired'},status=404)
		else:
			return poll
	else:
		return JsonResponse({'error':'Token invalid or expired'},status=404)

class PollUnAuth(APIView):


	def post(self,request,info,params):
		data = request.data

		try:
			verif_retorno = PollTokenVerif(data['token'],request)

			if type(verif_retorno) == type(JsonResponse({})):
				return verif_retorno
			else:
				pass
		except KeyError:
			return JsonResponse({'error':"The field: 'token' is required."},status=400,safe=False)

		try:
			poll = Poll.objects.get(options__pk=data['id'])
		except KeyError:
			return JsonResponse({'error':"The field: 'id' is required."},status=400,safe=False)
		except Poll.DoesNotExist:
			return JsonResponse({'error':"No option could be find with this 'id' value."},status=400,safe=False)


		if verif_retorno != poll:
			return JsonResponse({"error":"Option 'id' and Poll 'token' does not matches."})

		if poll.protect:
			option = Option.objects.get(pk=data['id'])
			try:
				control = ControlField.objects.create(control_field=data['control_field'],option=option)
			except KeyError:
				return JsonResponse({'error':"The field: 'control_field' is required on protect polls."},status=400,safe=False)
			option.votes += 1
			option.save()
			poll.total_votes +=1
			poll.save()
			return PollsParametersUnAuth(params,poll,request)
		else:
			option = Option.objects.get(pk=data['id'])
			option.votes += 1
			option.save()
			poll.total_votes +=1
			poll.save()			
			return PollsParametersUnAuth(params,poll,request)


	def get(self,request,info,params):

		verif_retorno = PollTokenVerif(info,request)

		if type(verif_retorno) == type(JsonResponse({})):
			return verif_retorno
		else:
			pass

		return PollsParametersUnAuth(params,verif_retorno,request)
				

		


class CreateUser(APIView):
	authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated,IsAdminUser]

	def post(self,request):
		data = request.data
		try:
			user = PollUser(username=data['username'],email=data['email'])
			user.set_password(data['password'])
			user.save()
			return JsonResponse({}, status=201)
		except Exception as e:
			error = str(e).split(':')[1]
			key = error.split('=')[0].split('(')[1][:-1]
			problem = error.split('=')[1].split(')')[1][:-1]

			
			return JsonResponse({'error':key + problem}, status=400)

class VerifEmail(APIView):
	"""authentication_classes = [TokenAuthentication]
	permission_classes = [IsAuthenticated,IsAdminUser]

	def post(self,request):
		email = User.objects.filter(email=request.data['email']).exists()
		username = User.objects.filter(email=request.data['username']).exists()
		data = {'email':email,'username':username}return JsonResponse(data,status=200)"""
	
		