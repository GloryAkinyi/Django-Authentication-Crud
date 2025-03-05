from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from .models import *


# Create your views here.
def index(request):
    return render(request, 'index.html')


def inner(request):
    return render(request, 'inner-page.html')



def Appoint(request):
    if request.method == 'POST':
        myappointments = Appointment(
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            date=request.POST['date'],
            department=request.POST['department'],
            doctor=request.POST['doctor'],
            message=request.POST['message'],
            image=request.FILES.get('image')  # Handle image upload
        )
        myappointments.save()
        return redirect('/show')

    else:
        return render(request, 'appointment.html')


def show(request):
    all = Appointment.objects.all()
    return render(request,'show.html',{'all':all})



def edit_appointment(request, id):
    appointment = get_object_or_404(Appointment, id=id)

    if request.method == "POST":
        appointment.name = request.POST.get("name")
        appointment.email = request.POST.get("email")
        appointment.phone = request.POST.get("phone")
        appointment.date = request.POST.get("date")
        appointment.department = request.POST.get("department")
        appointment.doctor = request.POST.get("doctor")
        appointment.message = request.POST.get("message")

        if 'image' in request.FILES:
            appointment.image = request.FILES['image']


        appointment.save()
        return redirect('show')  # Redirect to the page that lists all appointments

    return render(request, "edit.html", {"appointment": appointment})

def delete(request, id):
    myappointment = get_object_or_404(Appointment, id=id)

    if myappointment.image:
        myappointment.image.delete()  # Delete image file from storage

    myappointment.delete()
    return redirect('/show')



def register(request):
    """ Show the registration form """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Check the password
        if password == confirm_password:
            try:
                user = User.objects.create_user(username=username, password=password)
                user.save()

                # Display a message
                messages.success(request, "Account created successfully")
                return redirect('/login')
            except:
                # Display a message if the above fails
                messages.error(request, "Username already exist")
        else:
            # Display a message saying passwords don't match
            messages.error(request, "Passwords do not match")

    return render(request, 'register.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        # Check if the user exists
        if user is not None:
            # login(request, user)
            login(request,user)
            messages.success(request, "You are now logged in!")
            return redirect('/home')
        else:
            messages.error(request, "Invalid login credentials")

    return render(request, 'login.html')

