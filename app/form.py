from django import forms
from django.contrib.auth.models import User
from captcha.fields import CaptchaField

from .models import *

class LoginForm(forms.Form):
    username=forms.CharField(label='用户名',max_length=100,error_messages={'required': "用户名不能为空"})
    password=forms.CharField(label='密码',widget=forms.PasswordInput(),error_messages={'required': "密码不能为空"})
    captcha = CaptchaField(label='验证码')


    def clean_username(self):
        value = self.cleaned_data.get('username')
        user=User.objects.filter(username=value)
        if len(user) == 0:
            raise forms.ValidationError('用户%s不存在' % value)
        return value
class ExchangeForm(forms.ModelForm):
    class Meta:
        model=Exchange
        fields=['code','name','status','apikey','secretkey']
    def clean_status(self):
        statusvalue= self.cleaned_data.get('status')
        apikeyvalue = self.cleaned_data.get('apikey')
        secretkeyvalue = self.cleaned_data.get('secretkey')
        if apikeyvalue is None or secretkeyvalue is None and statusvalue is True:
            raise forms.ValidationError('API_KEY或SECRET_KEY未设置，无法启用此交易所')
        return statusvalue

