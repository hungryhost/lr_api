from django.urls import path
from .views import PropertyList, PropertyDetail
urlpatterns = [

	path('<int:pk>/', PropertyDetail.as_view()),
	path('', PropertyList.as_view()),
]
