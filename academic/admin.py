from django.contrib import admin
from .models import subject,exam,notice,result,club,Class

# Register your models here.

#subject's is here
@admin.register(subject)    
class subjectAdmin(admin.ModelAdmin):
    list_display=('subject_id','subject_name','subject_code','teacher_id')

#exam's is here
@admin.register(exam) 
class examAdmin(admin.ModelAdmin):
    list_display = ('exam_id', 'exam_name', 'exam_date', 'subject_id')

#notice's is here
@admin.register(notice)  
class noticeAdmin(admin.ModelAdmin):
    list_display = ('notice_id', 'user_id', 'notice_title', 'notice_description', 'notice_date', 'subject_id')

#result's is here
@admin.register(result)
class resultAdmin(admin.ModelAdmin):
    list_display = ('result_id', 'user_id', 'subject_id', 'exam_id', 'marks', 'grade')  

#club's is here
@admin.register(club)
class clubAdmin(admin.ModelAdmin):
    list_display = ('club_id', 'club_name', 'club_description', 'user_id')

#Class's is here
@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('class_id', 'class_name', 'semester','academic_year', 'class_teacher')

