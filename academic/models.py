from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

#subject's model created here
class subject(models.Model):
    subject_id=models.AutoField(primary_key=True)
    subject_name=models.CharField(max_length=64)
    subject_code=models.CharField(max_length=15)
    teacher_id=models.ForeignKey(get_user_model(),on_delete=models.CASCADE)


#exam's model created here
class exam(models.Model):
    exam_id=models.AutoField(primary_key=True)
    exam_name=models.CharField(max_length=64)
    exam_date=models.DateField()
    subject_id=models.ForeignKey(subject,on_delete=models.CASCADE)


#notice model created here
class notice(models.Model):
    notice_id=models.AutoField(primary_key=True)
    user_id=models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    notice_title=models.CharField(max_length=64)
    notice_description=models.TextField()
    notice_date=models.DateField(auto_now=True)
    subject_id=models.ForeignKey(subject,on_delete=models.CASCADE)

   
#result's model created here
class result(models.Model):
    result_id=models.AutoField(primary_key=True)
    user_id=models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    subject_id=models.ForeignKey(subject,on_delete=models.CASCADE)
    exam_id=models.ForeignKey(exam,on_delete=models.CASCADE)
    marks=models.IntegerField()
    grade=models.CharField(max_length=2)


#club's model created here
class club(models.Model):
    club_id=models.AutoField(primary_key=True)
    club_name=models.CharField(max_length=64)
    club_description=models.TextField()
    user_id=models.ForeignKey(get_user_model(),on_delete=models.CASCADE)

  
#class's model created here
class Class(models.Model):
    class_id=models.AutoField(primary_key=True)
    class_name=models.CharField(max_length=64)
    semester=models.IntegerField()
    session=models.IntegerField()
    academic_year = models.CharField(max_length=10)
    class_teacher=models.ForeignKey(get_user_model(),on_delete=models.CASCADE)

   
