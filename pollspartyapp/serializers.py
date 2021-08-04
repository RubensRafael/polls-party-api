from rest_framework import serializers
from pollspartyapp.models import Poll, Option, ControlField,PollToken

class ControlSerializer(serializers.ModelSerializer):
	class Meta:
		model = ControlField
		fields = ['control_field']

class TokenSerializer(serializers.ModelSerializer):
	class Meta:
		model = PollToken
		fields = ['token']

class OptionSerializer(serializers.ModelSerializer):
	

	def __init__(self, *args, **kwargs):
		fields = kwargs.pop('fields', None)
		super(OptionSerializer, self).__init__(*args, **kwargs)

		if fields is not None:
			allowed = set(fields)
			existing = set(self.fields)
			for field_name in existing - allowed:
				self.fields.pop(field_name)

	controllers = ControlSerializer(many=True, read_only=True)
	class Meta:
		model = Option
		fields = ['answer', 'votes','id','controllers']

class PollSerializer(serializers.ModelSerializer):

	def __init__(self, *args, **kwargs):
		fields = kwargs.pop('fields', None)
		super(PollSerializer, self).__init__(*args, **kwargs)

		if fields is not None:
			allowed = set(fields)
			existing = set(self.fields)
			for field_name in existing - allowed:
				self.fields.pop(field_name)

	

	options = OptionSerializer(many=True, read_only=True,fields=('id','answer','votes'))
	token = TokenSerializer(read_only=True)
	class Meta:
		model = Poll
		fields = ['id','question', 'total_votes', 'options','expires_in','token']