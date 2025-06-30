from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
import os

# Configure with your actual API key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyASKsQM1XwBhgzJQehhk9__Rs2O5VAmC9Y') 
genai.configure(api_key=GEMINI_API_KEY)

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
            chat = model.start_chat(history=[])
            response = chat.send_message(user_message)
            return JsonResponse({
                'response': response.text,
                'status': 'success'
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'status': 'error'
            }, status=500)
    
    return render(request, 'chatbot/chatbot.html')