from django.contrib import admin
from .models import DocumentsModel, SyncStatus, Compliances_Model, DocumentSync, Profile, Clients

# Register your models here.
admin.site.register(DocumentsModel)
admin.site.register(SyncStatus)
admin.site.register(Compliances_Model)
admin.site.register(DocumentSync)
admin.site.register(Profile)
admin.site.register(Clients)