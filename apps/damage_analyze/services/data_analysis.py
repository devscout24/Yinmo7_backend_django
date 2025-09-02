import base64
import requests
import json
from django.conf import settings
from openai import OpenAI
from rest_framework.views import APIView

class OpenAIService(APIView):
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
            # Encode image to base64
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # Prepare the prompt for car damage analysis
            prompt = """
            Analyze this car damage image and provide a detailed assessment in JSON format.
            The JSON should include:
            - total_estimated_min: minimum estimated repair cost (USD)
            - total_estimated_max: maximum estimated repair cost (USD)
            - severity: overall damage severity (low, medium, high, critical)
            - parts: array of damaged parts with:
              * part_name: name of the damaged part (e.g., Hood, Front Bumper, Headlight)
              * damage_description: detailed description of the damage
              * action_required: recommended repair action
              * estimated_cost_min: minimum estimated cost for this part (USD)
              * estimated_cost_max: maximum estimated cost for this part (USD)

            Be detailed and accurate in your assessment. Consider:
            1. The extent of damage (minor scratches, dents, major deformation)
            2. Whether parts need replacement or can be repaired
            3. Labor costs for each repair
            4. Potential hidden damage that might not be visible

            Return ONLY valid JSON, no additional text.
            """

            # Using the new responses.create method (for newer OpenAI API versions)
            response = self.client.responses.create(
                model="gpt-4.1-mini",  # Use "gpt-5" when available
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

            # Extract the response text
            analysis_text = response.output_text

            # Try to parse the JSON response
            from rest_framework.response import Response
            try:
                # Clean the response text to extract JSON
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1

                if json_start != -1 and json_end != -1:
                    json_str = analysis_text[json_start:json_end]
                    return Response(json.loads(json_str))
                else:
                    # If no JSON found, try to parse the whole response
                    return Response(json.loads(analysis_text))
            except json.JSONDecodeError:
                # Fallback: return the raw text if JSON parsing fails
                return Response({
                    "error": "Failed to parse AI response as JSON",
                    "raw_response": analysis_text
                }, status=500)

        except Exception as e:
            return self.response_error(f"OpenAI API request failed: {str(e)}", status=500)

    def response_error(self, message, status=400):
        from rest_framework.response import Response
        return Response({"error": message}, status=status)
    
    # def analyze_car_damage_alternative(self, image_path):
    #     """
    #     Alternative implementation using chat.completions for older API versions
    #     """
    #     # Encode image to base64
    #     with open(image_path, "rb") as image_file:
    #         base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
    #     prompt = """
    #     Analyze this car damage image and provide a detailed assessment in JSON format.
    #     The JSON should include:
    #     - total_estimated_min: minimum estimated repair cost (USD)
    #     - total_estimated_max: maximum estimated repair cost (USD)
    #     - severity: overall damage severity (low, medium, high, critical)
    #     - parts: array of damaged parts with:
    #       * part_name: name of the damaged part
    #       * damage_description: description of the damage
    #       * action_required: recommended repair action
    #       * estimated_cost_min: minimum estimated cost for this part
    #       * estimated_cost_max: maximum estimated cost for this part
        
    #     Return ONLY valid JSON, no additional text.
    #     """
        
    #     try:
    #         response = self.client.chat.completions.create(
    #             model="gpt-4-vision-preview",
    #             messages=[
    #                 {
    #                     "role": "user",
    #                     "content": [
    #                         {"type": "text", "text": prompt},
    #                         {
    #                             "type": "image_url",
    #                             "image_url": {
    #                                 "url": f"data:image/jpeg;base64,{base64_image}"
    #                             }
    #                         }
    #                     ]
    #                 }
    #             ],
    #             max_tokens=2000
    #         )
            
    #         analysis_text = response.choices[0].message.content
            
    #         # Try to parse the JSON response
    #         try:
    #             json_start = analysis_text.find('{')
    #             json_end = analysis_text.rfind('}') + 1
                
    #             if json_start != -1 and json_end != -1:
    #                 json_str = analysis_text[json_start:json_end]
    #                 return json.loads(json_str)
    #             else:
    #                 return json.loads(analysis_text)
    #         except json.JSONDecodeError:
    #             return {
    #                 "error": "Failed to parse AI response as JSON",
    #                 "raw_response": analysis_text
    #             }
                
    #     except Exception as e:
    #         return {"error": f"OpenAI API request failed: {str(e)}"}