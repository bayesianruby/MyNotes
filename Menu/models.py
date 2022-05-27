from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
# from django.contrib.auth.models import AbstractUser


class Subject(models.Model):
    name = models.CharField(max_length=128)
    def __str__(self):
        return self.name


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    subjects = models.ManyToManyField(Subject)
    university = models.CharField(max_length=128,default='')
    year = models.SmallIntegerField(default=-1)
    def __str__(self):
        return(self.user.username)

class Image(models.Model):
    image = models.ImageField(upload_to='images/')




class Text(models.Model):
    richtext = RichTextField(default="",blank=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, null=True,on_delete=models.CASCADE)
    # customer = models.ForeignKey(
    #     Customer, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    title = models.CharField(max_length=128,default='') 
    pdf = models.FileField(upload_to= 'pdf/',blank=True)
    is_a_pdf = models.BooleanField(default=False)
    teacher = models.CharField(max_length=128,default='')
    is_private = models.BooleanField(default=False)
    #year = models.BooleanField(default=False)
    class Meta:
        # sort by "the date" in descending order unless
        # overridden in the query with order_by()
        ordering = ['-date_created']
    def __str__(self):
        if self.title== '':
            return self.richtext[:20]
        else : 
            return self.title[:20]

def get_or_none(classmodel, **kwargs):
        try:
            return classmodel.objects.get(**kwargs)
        except classmodel.DoesNotExist:
            return None
