import base64
import requests
import json
from django.conf import settings
from rest_framework.views import APIView

class OpenAIService(APIView):
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    def post(self, request):
        """
        Analyze car damage using OpenAI's GPT-4 with vision capabilities
        Accepts image upload via form-data (key: 'image').
        """
        image_file = request.FILES.get('image')
        if not image_file:
            return self.response_error("No image file uploaded.")
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        prompt = """
        Analyze this car damage image and provide a detailed assessment in JSON format.
        The JSON should include:
        - Description of the damage.
        - total_estimated_min: minimum estimated repair cost
        - total_estimated_max: maximum estimated repair cost
        - severity: overall damage severity (low, medium, high, critical)
        - parts: array of damaged parts with:
          * part_name: name of the damaged part
          * damage_description: description of the damage
          * action_required: recommended repair action
          * estimated_cost_min: minimum estimated cost for this part
          * estimated_cost_max: maximum estimated cost for this part
        
        Be detailed and accurate in your assessment. Consider the extent of damage,
        potential part replacements vs repairs, and labor costs.
        """
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            analysis_text = result['choices'][0]['message']['content']
            try:
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_str = analysis_text[json_start:json_end]
                    return self.response_json(json.loads(json_str))
                else:
                    return self.response_json(json.loads(analysis_text))
            except json.JSONDecodeError:
                return self.response_json({
                    "error": "Failed to parse AI response",
                    "raw_response": analysis_text
                })
        except requests.exceptions.RequestException as e:
            return self.response_error(f"OpenAI API request failed: {str(e)}")
        except Exception as e:
            return self.response_error(f"Unexpected error: {str(e)}")

    def response_json(self, data, status=200):
        from rest_framework.response import Response
        return Response(data, status=status)

    def response_error(self, message, status=400):
        from rest_framework.response import Response
        return Response({"error": message}, status=status)
        