from django.db import models
from datetime import datetime
from django.utils.functional import cached_property
import uuid

from django.db.models.signals import post_delete
from django.dispatch import receiver
# models.py
from django.contrib.auth.models import User
from django.db import models

def get_default_user():
    # return User.objects.get(username='os').id  # or any default username
    return 1

class Clients(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ca_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=20)
    address = models.TextField()
    business_type = models.CharField(max_length=100)
    business_name = models.CharField(max_length=100)
    gst_number = models.CharField(max_length=20)
    pan_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
 



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    firm_name = models.CharField(max_length=255, blank=True)
    ca_registration_number = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class DocumentsModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    doc_type = models.CharField(max_length=100, default='others') # IT WOULD BE DONE AS A PROPERTY

    @property
    def name(self):
        return str(self.file).replace('uploads/', '')

@receiver(post_delete, sender=DocumentsModel)
def delete_file_on_model_delete(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(False)
        
class DocumentSync(models.Model):
    name = models.CharField(max_length=100, unique=True)
    d = models.JSONField(default={})
    embedding_dim = models.IntegerField(default=384)

# Create your models here.
# class UploadedFile(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     file = models.FileField(upload_to='uploads/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     doc_type = models.CharField(max_length=100, null=True)

class Compliances_Model(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length = 2000, null = True)
    
    date = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()

    completed = models.BooleanField(default=False)

    # completed = models.
    @property
    def type(self):
        txt = self.description
        if 'GST' in txt.upper():
            return 'GST'
        elif 'TDS' in txt.upper():
            return 'TDS'
        elif 'TCS' in txt.upper():
            return 'TCS'
        elif 'income tax' in txt.lower():
            return 'Income Tax'
        return 'Others'

    @property
    def heading(self):
        txt = self.description
        return txt.split('.')[0][:80].strip()
    
    @property
    def tag(self):
        """
        Returns 'high' if the compliance date is within 3 days from today,
        'moderate' if within 10 days, else 'other'.
        """
        try:
            compliance_date = datetime(self.year, self.month, self.date)
            today = datetime.now()
            delta = (compliance_date - today).days
            if delta <= 3 and delta >= 0:
                return 'high'
            elif delta <= 10 and delta > 3:
                return 'moderate'
            else:
                return 'low'
        except Exception:
            return 'low'        



class SyncStatus(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., 'compliance_fetch'
    last_fetched = models.DateTimeField(null=True)    # updated automatically
    completed_number = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.last_fetched}"
    

    # tag = models.CharField(max_length = 200, null = True, default=fill_tag)
    # heading = models.CharField(max_length = 200, null = True, default=fill_heading)
    # type = models.CharField(max_length = 200, null = True, default=fill_type)

    # def is_good_compliance_date_check(self):
    #     curr_date = datetime.now()
    #     if self.year == curr_date.year :
    #         if self.month == curr_date.month:
    #             # we need to check the date now
    #             if self.date >= curr_date.day:
    #                 return True

    #         elif self.month > curr_date.month:
    #             return True
        # 
        # return False