import base64,json
from django.conf import settings
from openai import OpenAI
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializer import AppointmentRequestSerializer,RepairShopProfileSerializer,DamageAnalyzeSerializer
from apps.user.models import RepairShopProfile
from .models import DamageAnalyze, Damage
from rest_framework import status
from apps.user.permission import IsCarOwner,IsRepairShop

class DamageAnalysisView(APIView):
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)

    def post(self, request):
        image_file = request.FILES.get("image")
        """
        Analyze car damage using OpenAI GPT-4 with vision.
        Input: multipart/form-data with 'image' + car details.
        """
        if not image_file:
            return self.response_error("Image file is required in form-data with key 'image'.", status=400)

        try:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            prompt = """
            Analyze this car damage image and return ONLY valid JSON.
            JSON must include:
            {
            "description": "Overall damage description",
            "total_estimated_min": number,
            "total_estimated_max": number,
            "severity": "low | medium | high | critical",
            "parts": [
                {
                "part_name": "string",
                "damage_description": "string",
                "action_required": "string",
                "estimated_cost_min": number,
                "estimated_cost_max": number
                }
            ]
            }
            """

            response = self.client.responses.create(
                model="gpt-4.1-mini",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": prompt,
                            },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        ]
                    }
                ]
            )

            analysis_text = response.output_text

            car_brand = request.data.get("car_brand")
            car_model = request.data.get("car_model")
            year = request.data.get("year")
            user_obj = request.user if hasattr(request, "user") and request.user.is_authenticated else None

            try:
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1

                if json_start != -1 and json_end != -1:
                    json_str = analysis_text[json_start:json_end]
                    analysis_data = json.loads(json_str)
                else:
                    analysis_data = json.loads(analysis_text)
            except json.JSONDecodeError:
                return Response({
                    "error": "Failed to parse AI response as JSON",
                    "raw_response": analysis_text
                }, status=500)

            damage_analyze = DamageAnalyze.objects.create(
                car_owner=user_obj,
                car_brand=car_brand,
                car_model=car_model,
                year=year,
                total_estimated_min=analysis_data.get("total_estimated_min"),
                total_estimated_max=analysis_data.get("total_estimated_max"),
                severity=analysis_data.get("severity"),
            )

            for part in analysis_data.get("parts", []):
                Damage.objects.create(
                    analyze=damage_analyze,
                    part_name=part.get("part_name"),
                    damage_type=part.get("damage_description"),
                    damage=part.get("damage_description"),
                    action=part.get("action_required"),
                    estimated_cost_min=part.get("estimated_cost_min"),
                    estimated_cost_max=part.get("estimated_cost_max"),
                )

            return Response(analysis_data)

        except Exception as e:
            return self.response_error(f"OpenAI API request failed: {str(e)}", status=500)

    def response_error(self, message, status=400):
        from rest_framework.response import Response
        return Response({"error": message}, status=status)
    

class ShowEstimateList(APIView):
    permission_classes = [IsAuthenticated, IsCarOwner]

    def get(self, request, *args, **kwargs):
        user = request.user
        estimates = DamageAnalyze.objects.filter(car_owner=user)
        serializer = DamageAnalyzeSerializer(estimates, many=True)
        return Response(serializer.data)


class DeleteItemsFromEstimateList(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        item_ids = request.data.get("item_ids", [])

        if not item_ids:
            return Response({"error": "No item_ids provided"}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = Damage.objects.filter(
            id__in=item_ids,
            analyze__car_owner=request.user
        ).delete()

        if deleted_count == 0:
            return Response(
                {"message": "No items deleted. They may not exist or don’t belong to you."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"message": f"{deleted_count} item(s) deleted successfully"},
            status=status.HTTP_200_OK
        )         
    


class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated, IsCarOwner]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['car_owner'] = request.user.id
        shop_id = request.data.get('shop_id')
        if shop_id:
            data['repair_shop'] = shop_id
        serializer = AppointmentRequestSerializer(data=data)
        if serializer.is_valid():
            booking = serializer.save()
            return Response(AppointmentRequestSerializer(booking).data, status=201)
        return Response(serializer.errors, status=400)
    



#============================================== Need To Test ===============================================
class CreateReviewView(APIView):
    permission_classes = [IsAuthenticated, IsCarOwner]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['car_owner'] = request.user.id
        shop_id = request.data.get('shop_id')
        if shop_id:
            data['repair_shop'] = shop_id
        serializer = AppointmentRequestSerializer(data=data)
        if serializer.is_valid():
            booking = serializer.save()
            return Response(AppointmentRequestSerializer(booking).data, status=201)
        return Response(serializer.errors, status=400)

class ListOfRepairShop(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        repair_shops = RepairShopProfile.objects.all()
        serializer = RepairShopProfileSerializer(repair_shops, many=True)
        return Response(serializer.data)
    
