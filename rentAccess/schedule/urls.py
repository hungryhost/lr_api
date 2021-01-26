from django.urls import path
from .views import AccessList, AccessDetail, AccessNow


urlpatterns = [
    path('<int:pk>/', AccessDetail.as_view()),
    path('now/', AccessNow.as_view()),
    path('<int:year_s>-<int:month_s>-<int:day_s>T<int:hour_s>:<int:min_s>&<int:year_e>-<int:month_e>-<int:day_e>T<int'
         ':hour_e>:<int:min_e>/', AccessList.as_view()),
]

