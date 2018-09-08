from django.db import models
from django_apscheduler.models import DjangoJob
# Create your models here.
class Exchange(models.Model):
    code=models.CharField('代号',max_length=30)
    name=models.CharField('名称',max_length=50)
    status=models.BooleanField('启用',default=False)
    apikey=models.CharField('API_KEY',max_length=100,null=True)
    secretkey=models.CharField('SECRET_KEY',max_length=100,null=True)
    symbols=models.CharField('对名称列表', max_length=10000,null=True)
class Symbol(models.Model):
    exchange=models.ForeignKey('Exchange',on_delete=models.CASCADE,null=True)
    name=models.CharField('对名称', max_length=30,default='')
class Task(models.Model):
    name=models.CharField('任务名称', max_length=100,unique=True)
    minute=models.CharField('分', max_length=10,)
    hour = models.CharField('时', max_length=10)
    day = models.CharField('天', max_length=10)
    exid =models.IntegerField('交易所ID')
    symbol=models.CharField('交易对', max_length=20)
    amount=models.DecimalField('金额',max_length=20)
    sellpercent=models.DecimalField('卖出比率',max_length=10)
    cost=models.DecimalField('成本，max_length=50')
    ttime=models.TimeField('任务时间',auto_now=True)
class Tasklog(models.Model):
    task=models.ForeignKey('Task',on_delete=models.CASCADE)
    tltime=models.TimeField('日志时间',auto_now_add=True)
    content=models.TextField('日志内容',max_length=2000)
