from django.contrib import admin
from .models import subject,exam,notice,result,club

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_id', 'subject_name', 'subject_code', 'teacher_id')

admin.site.register(subject, SubjectAdmin)
admin.site.register(exam)
admin.site.register(notice)
admin.site.register(result)
admin.site.register(club)

