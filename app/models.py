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
class Cast(models.Model):
    name=models.CharField('定投名称', max_length=100)
    minute=models.CharField('分', max_length=10,)
    hour = models.CharField('时', max_length=10)
    day = models.CharField('天', max_length=10)
    exid =models.IntegerField('交易所ID')
    symbol=models.CharField('交易对', max_length=20)
    amount=models.DecimalField('金额',max_digits=40, decimal_places=20)
    sellpercent=models.DecimalField('卖出比率', max_digits=5, decimal_places=2)
    cost=models.DecimalField('成本，max_length=50', max_digits=40, decimal_places=20,default=0)
    ttime=models.DateTimeField('任务时间',auto_now=True)
    def getrun(self):
        status='停止'
        jobs = DjangoJob.objects.filter(name=str(self.id))
        if jobs.exists():
            status='运行'
        return status
    def getnextruntime(self):
        nextruntime='无'
        jobs=DjangoJob.objects.filter(name=str(self.id))
        if jobs.exists():
            nextruntime=str(jobs[0].next_run_time)
        return nextruntime
class Castlog(models.Model):
    cast=models.ForeignKey('Cast',on_delete=models.CASCADE)
    tltime=models.DateTimeField('日志时间',auto_now_add=True)
    content=models.TextField('日志内容',max_length=2000)
