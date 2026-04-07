from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from Backend.main import Chatbox
import difflib
from django.http import JsonResponse
from .models import *
import json
chatbox=Chatbox()


def category(request):
    return render(request,'category.html')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Doctor, Department
import difflib

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Doctor, Department
from .main import Chatbox

bot = Chatbox()

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Doctor, Department
from .main import Chatbox
import difflib

bot = Chatbox()

@csrf_exempt
def process_of_chatbox(request):

    if request.method == "POST":

 
        message = request.POST.get("message", "").strip()

        if not message:
            return JsonResponse({
                "response": "⚠️ Please type something.",
                "confidence": 0.0,
                "model": "system"
            })

        try:
            user_input = message.lower()

            # ---------------- RULE BASED (DEPARTMENT) ----------------
            departments = Department.objects.all()
            doctors = Doctor.objects.all()

            dept_names = [d.name.lower() for d in departments]

            match = difflib.get_close_matches(user_input, dept_names, n=1, cutoff=0.6)

            if match:
                dept_name = match[0]

                doctor = doctors.filter(department__iexact=dept_name).first()

                if doctor:
                    return JsonResponse({
                        "response": f"👨‍⚕️ {doctor.name} is available in {dept_name.title()} department.",
                        "confidence": 1.0,
                        "model": "RULE"
                    })
                else:
                    return JsonResponse({
                        "response": f"No doctors available in {dept_name.title()} department.",
                        "confidence": 1.0,
                        "model": "RULE"
                    })

            # ---------------- AI MODEL (SLM + ML) ----------------
            result = bot.chat(message)

            return JsonResponse(result)

        except Exception as e:
            return JsonResponse({
                "response": "❌ Something went wrong.",
                "error": str(e),
                "model": "error"
            })

    return JsonResponse({
        "response": "❌ Only POST method allowed"
    })

def get_doctors(request):

    doctors = Doctor.objects.all()

    data = [{"name": doctor.name,
            "department": doctor.department}for doctor in doctors]
    return JsonResponse({
        "doctors": data
    })


def get_departments(request):
    departments = Department.objects.all()
    
    data=[{'name':dept.name} for dept in departments]

    return JsonResponse({
        "departments": data
    })


