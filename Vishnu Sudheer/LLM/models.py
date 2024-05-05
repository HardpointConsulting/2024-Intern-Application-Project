from django.db import models

# Create your models here.
class Output(models.Model):
    id=models.IntegerField(primary_key=True)
    title=models.CharField(max_length=255,null=True)
    year=models.IntegerField(null=True)
    journal=models.CharField(max_length=255,null=True)
    authors=models.TextField(null=True)
    description=models.TextField(null=True)
    constructs=models.TextField(null=True)
    context=models.TextField(null=True)
    study=models.TextField(null=True)
    level=models.TextField(null=True)
    findings=models.TextField(null=True)
    summary=models.TextField(null=True)