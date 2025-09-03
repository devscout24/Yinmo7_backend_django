from django.shortcuts import render
from rest_framework.views import APIView
from apps.damage_analyze.serializer import AppointmentRequestSerializer
from apps.user.permission import IsCarOwner,IsRepairShop,IsShopOwner
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.repair_shop.models import AppointmentRequest

# Create your views here.
class AppointmentList(APIView):
    permission_classes = [IsAuthenticated, IsRepairShop]

    def get(self, request):
        bookings = AppointmentRequest.objects.filter(repair_shop=request.user)
        serializer = AppointmentRequestSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AcceptAppointment(APIView):
    permission_classes = [IsAuthenticated, IsRepairShop, IsShopOwner]

    def post(self, request, appointment_id):
        try:
            appointment = AppointmentRequest.objects.get(id=appointment_id)
        except AppointmentRequest.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        appointment.status = "accepted"
        appointment.save()

        return Response({"message": "Appointment accepted successfully."}, status=status.HTTP_200_OK)
    

class RejectAppointment(APIView):
    permission_classes = [IsAuthenticated, IsRepairShop, IsShopOwner]

    def post(self, request, appointment_id):
        try:
            appointment = AppointmentRequest.objects.get(id=appointment_id)
        except AppointmentRequest.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        appointment.status = "declined"
        appointment.save()

        return Response({"message": "Appointment rejected successfully."}, status=status.HTTP_200_OK)

    
class CompleteAppointment(APIView):
    permission_classes = [IsAuthenticated, IsRepairShop, IsShopOwner]

    def post(self, request, appointment_id):
        try:
            appointment = AppointmentRequest.objects.get(id=appointment_id)
        except AppointmentRequest.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        appointment.status = "completed"
        appointment.save()

        return Response({"message": "Appointment completed successfully."}, status=status.HTTP_200_OK)