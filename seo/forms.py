'''seo forms'''
from django import forms
from seo.models import Metadata


class AddSeoForm(forms.ModelForm):
	"""
	Form for saving seo
	"""
	class Meta:
		model = Metadata
		fields = '__all__'
		#fields = ['keywords', 'title', 'description', 'lastname', 'ext']