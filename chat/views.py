import os
import google.generativeai as genai
from dotenv import load_dotenv
from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import WellnessGoalForm
from .models import WellnessGoal
from django.contrib.auth.decorators import login_required

from .models import Goal, GoalProgress
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import JsonResponse

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")

def neurobuddy_chat(request):
    if request.method == "POST":
        user_input = request.POST.get("user_input", "")
        try:
            response = model.generate_content(user_input)
            reply = response.text
        except Exception as e:
            reply = f"⚠️ Gemini Error: {str(e)}"
        return render(request, "chat/chat.html", {"response": reply})
    return render(request, "chat/chat.html")


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")

def smart_todo_view(request):
    tips = ""
    if request.method == "POST":
        mood = request.POST.get("mood", "")
        prompt = f"""
        A user is feeling '{mood}'. 
        Suggest 3 smart to-do tips that are practical, supportive, and mental-health friendly. 
        Example: take a walk, journal, break tasks into small steps, etc.
        """
        try:
            response = model.generate_content(prompt)
            tips = response.text
        except Exception as e:
            tips = f"⚠️ Gemini Error: {str(e)}"

    return render(request, "chat/chat.html", {"tips": tips})




def neurogoals_view(request):
    if request.method == 'POST':
        form = WellnessGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('neurogoals')
    else:
        form = WellnessGoalForm()

    goals = WellnessGoal.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'chat/neurogoals.html', {'form': form, 'goals': goals})

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")

@login_required
def suggest_goals(request):
    today = timezone.now().date()
    user = request.user

    if request.method == 'POST':
        mood_input = request.POST.get('mood_input', '')
        prompt = f"Suggest 3 daily mental wellness goals for someone feeling: {mood_input}."
        response = model.generate_content(prompt)
        goals_text = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
        
        # Save new goals to DB
        for goal_text in goals_text:
            goal = Goal.objects.create(user=user, text=goal_text)
            GoalProgress.objects.create(goal=goal, completed=False)

    # Load today's goals
    todays_goals = Goal.objects.filter(user=user, created_at=today).prefetch_related('progress')

    return render(request, 'chat/suggest_goals.html', {'todays_goals': todays_goals})



@require_POST
@login_required
def toggle_goal_completion(request, progress_id):
    progress = GoalProgress.objects.get(id=progress_id, goal__user=request.user)
    progress.completed = not progress.completed
    progress.save()
    return JsonResponse({'status': 'ok', 'completed': progress.completed})
