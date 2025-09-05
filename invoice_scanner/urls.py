from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('invoice_home/', views.invoice_input, name='invoice_input'),
    path('invoice_process/', views.invoice_process, name = 'invoice_process'),
    path('compliance/', views.compliance, name = 'compliance'),
    path('documents/', views.documents, name = 'documents'),
    path('compliance/complete/<uuid:id>/', views.mark_complete, name='mark_complete'),
    path('bank_statement_analyzer/', views.bank_statement_analyzer, name = 'bank_statement_analyzer'),
    path('bank_statement_analyzer_process/', views.bank_statement_analyzer_process, name='bank_statement_analyzer_process'),
    path('profile/', views.profile, name='profile'),
    path('ask_ca_ai/', views.ask_ca_ai, name='ask_ca_ai'),
    path('front-page', views.front_page, name='front_page'),  
    path('front-page-2/', views.front_page2, name='front_page2'),  
    path('clients/', views.clients, name='clients'),
    path('tds/', views.tds, name = 'tds')

]



