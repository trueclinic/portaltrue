"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
app_name = 'ticket'

urlpatterns = [
    path('tickets/', views.lista_tickets, name='lista'),
    path('tickets/novo/', views.criar_ticket, name='criar'),
    path('tickets/<int:ticket_id>/', views.detalhe_ticket, name='detalhe'),
    path('tickets/export/csv/', views.exportar_tickets_csv, name='export_csv'),
    path('tickets/export/xlsx/', views.exportar_tickets_xlsx, name='export_xlsx'),
]