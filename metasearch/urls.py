from django.urls import path

from .views import HomePageView, search_results


urlpatterns = [
    path('search/', search_results, name='search_results'),
    path('', HomePageView.as_view(), name='home_page'),
]