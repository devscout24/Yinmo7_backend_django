from django.urls import path
from apps.repair_shop.views import AcceptAppointment, AppointmentList, CompleteAppointment, RejectAppointment

urlpatterns = [
    path('appointments-list/', AppointmentList.as_view(), name='appointment-list'),
    path('accept-appointments/<int:appointment_id>/', AcceptAppointment.as_view(), name='appointment-detail'),
    path('reject-appointments/<int:appointment_id>/', RejectAppointment.as_view(), name='reject-appointment'),
    path('complete-appointments/<int:appointment_id>/', CompleteAppointment.as_view(), name='complete-appointment'),
    
]