from django.db import models

# Create your models here.
class Exchange(models.Model):
    code=models.CharField('代号',max_length=30)
    name=models.CharField('名称',max_length=50)
    status=models.BooleanField('启用',default=False)
    apikey=models.CharField('API_KEY',max_length=100)
    secretkey=models.CharField('SECRET_KEY',max_length=100)
    symbols=models.CharField('对名称列表', max_length=10000,null=True)
class Symbol(models.Model):
    ecode=models.CharField('代号',max_length=30)
    snames=models.CharField('对名称列表', max_length=10000)