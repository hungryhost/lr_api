from django.urls import path
from django.views.generic import TemplateView
from .views import PropertyList, PropertyDetail, PropertyCreate, PropertyUpdate, PropertyDelete

urlpatterns = [

	path('<int:pk>/', PropertyDetail.as_view()),
	path('list/', PropertyList.as_view()),
	path('create/', PropertyCreate.as_view()),
	path('update/<int:pk>/', PropertyUpdate.as_view()),
	path('delete/<int:pk>/', PropertyDelete.as_view()),
	# TODO: uncomment the paths below after adding the views
	# path('upload_main_image/<int:pk>/', PropertyMainImageUpload.as_view()),
	# path('upload_additional_images/<int:pk>/', PropertyAdditionalImagesUpload.as_view()),
	# path('delete_main_image/<int:pk>/', PropertyDeleteMainImage.as_view()),
	# TODO: find a way to either specify the image for delete request ot separate them
	# path('delete_additional_images/<int:pk/', PropertyDeleteAdditionalImages.as_view()),
]
