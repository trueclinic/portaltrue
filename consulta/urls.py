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

app_name = 'consulta'

urlpatterns = [
    path('exames/', views.lista_exames, name='lista'),
    path('exames/novo/', views.criar_exame, name='criar'),
    path('exames/<int:exame_id>/', views.detalhe_exame, name='detalhe'),
    path('exames/export/csv/', views.exportar_exames_csv, name='export_csv'),
    path('exames/export/xlsx/', views.exportar_exames_xlsx, name='export_xlsx'),
]