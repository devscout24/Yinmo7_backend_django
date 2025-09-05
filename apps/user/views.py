from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import CarModel, RepairShopImage
from apps.user.models import User, RepairShopProfile
from apps.user.serializers import UserProfileSerializer



class CarOwnerProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()
        # Ensure car_owner is a dict
        car_owner_data = data.get('car_owner', {})
        if isinstance(car_owner_data, str):
            import json
            car_owner_data = json.loads(car_owner_data)
        # Handle image upload for car_owner profile
        if 'image' in request.FILES:
            car_owner_data['image'] = request.FILES['image']
        data['car_owner'] = car_owner_data
        serializer = UserProfileSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Profile updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    


class RepairShopOProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = user.repair_shop
        except RepairShopProfile.DoesNotExist:
            return Response({
                "status": "error",
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": "Repair shop profile not found."
            }, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        if 'logo' in request.FILES:
            data['logo'] = request.FILES['logo']

        business_hours_data = data.pop('business_hours', [])
        profile.business_hours.all().delete()
        from .models import RepairshopBesinessHour
        for bh in business_hours_data:
            RepairshopBesinessHour.objects.create(shop=profile, **bh)

        for attr in ['shop_name', 'contact_person_name', 'phone', 'location', 'charge_range']:
            if attr in data:
                setattr(profile, attr, data[attr])
        if 'logo' in data:
            profile.logo = data['logo']
        profile.save()

        cover_images = request.FILES.getlist('cover_images')
        for img in cover_images:
            RepairShopImage.objects.create(shop=profile, image=img)

        cover_image_urls = [img.image.url for img in profile.images.all()]
        business_hours = list(profile.business_hours.values())
        return Response({
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "Repair shop profile updated successfully.",
            "data": {
                "shop_name": profile.shop_name,
                "charge_range": profile.charge_range,
                "contact_person_name": profile.contact_person_name,
                "phone": profile.phone,
                "location": profile.location,
                "logo": profile.logo.url if profile.logo else None,
                "cover_images": cover_image_urls,
                "business_hours": business_hours,
            }
        }, status=status.HTTP_200_OK)