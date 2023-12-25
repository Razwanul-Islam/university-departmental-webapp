from django.contrib import admin
from .models import subject,exam,notice,result,club,Class

# Register your models here.

admin.site.register(subject)    
admin.site.register(exam)
admin.site.register(notice)
admin.site.register(result)
admin.site.register(club)
admin.site.register(Class)

