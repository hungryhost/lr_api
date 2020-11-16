from django.urls import path
from django.views.generic import TemplateView
from .views import PropertyList, PropertyDetail, PropertyCreate, PropertyUpdate, PropertyDelete

# TODO: separate delete route

urlpatterns = [

	path('<int:pk>/', PropertyDetail.as_view()),
	path('list/', PropertyList.as_view()),
	path('create/', PropertyCreate.as_view()),
	path('update/<int:pk>/', PropertyUpdate.as_view()),
	path('delete/<int:pk>/', PropertyDelete.as_view()),
]
