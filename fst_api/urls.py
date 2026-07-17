"""
URL configuration for fst_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.urls import re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from fst_api.api import AnalysisList

# router = routers.DefaultRouter()

schema_view = get_schema_view(
    openapi.Info(
        title="Altlab FST API",
        default_version="v1",
        description="Provides access to an FST as a REST endpoint",
        public=True,
    )
)

urlpatterns = [
    re_path("$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    re_path("^analyse/(?P<wordform>.+)$", AnalysisList.as_view()),
]
