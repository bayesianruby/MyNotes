from django.contrib import admin
from .models import Image
from .models import Text
from .models import Subject
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import UserProfile

# from .models import Customer

# Register your models here.
admin.site.register(Image)
admin.site.register(Text)
admin.site.register(Subject)
admin.site.register(UserProfile)
# admin.site.register(Customer)