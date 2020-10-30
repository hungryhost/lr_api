from django.urls import path
from django.views.generic import TemplateView
from .views import PropertyList, PropertyDetail
urlpatterns = [

	path('<int:pk>/', PropertyDetail.as_view()),
	path('', PropertyList.as_view()),

]
