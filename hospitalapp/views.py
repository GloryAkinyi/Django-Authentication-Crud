import json

import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponse
from requests.auth import HTTPBasicAuth

from hospitalapp.credentials import MpesaAccessToken, LipanaMpesaPpassword

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
        image = request.FILES.get('image')

        if image:  # Log file upload
            print(f"Uploaded File Name: {image.name}")
            print(f"File Size: {image.size} bytes")

            # Optional: Save to disk manually (debugging)
            path = default_storage.save(f"appointments/{image.name}", ContentFile(image.read()))
            print(f"File saved at: {path}")

        myappointments = Appointment1(
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            date=request.POST['date'],
            department=request.POST['department'],
            doctor=request.POST['doctor'],
            message=request.POST['message'],
            image=image  # Assign image
        )
        myappointments.save()
        return redirect('/show')

    return render(request, 'appointment.html')


def show(request):
    all = Appointment1.objects.all()
    return render(request,'show.html',{'all':all})


def edit_appointment(request, id):
    appointment = get_object_or_404(Appointment1, id=id)

    if request.method == "POST":
        appointment.name = request.POST.get("name")
        appointment.email = request.POST.get("email")
        appointment.phone = request.POST.get("phone")
        appointment.date = request.POST.get("date")
        appointment.department = request.POST.get("department")
        appointment.doctor = request.POST.get("doctor")
        appointment.message = request.POST.get("message")

        # Handle image update
        if 'image' in request.FILES:
            if appointment.image:  # Delete old image
                appointment.image.delete()
            appointment.image = request.FILES['image']

        appointment.save()
        messages.success(request, "Appointment updated successfully!")
        return redirect('/show')  # Redirect to list of appointments

    return render(request, "edit.html", {"appointment": appointment})




def delete(request, id):
    myappointment = get_object_or_404(Appointment1, id=id)

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


def admin_login_view(request):
    # Admin credentials
    admin_username = "glory"
    admin_email = "akinyiglory2@gmail.com"
    admin_password = "Gloryokoth@1999"

    # Ensure admin user exists
    if not User.objects.filter(username=admin_username).exists():
        User.objects.create_superuser(username=admin_username, email=admin_email, password=admin_password)
        print("Superuser created successfully!")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.username == admin_username:
            login(request, user)
            messages.success(request, "Welcome Admin!")
            return redirect('/transactions')  # Redirect to transactions page
        else:
            messages.error(request, "Invalid credentials! Only admin can log in.")
            return redirect('/adminlogin')  # Redirect back to login page

    return render(request, 'adminlogin.html')





def token(request):
    consumer_key = '77bgGpmlOxlgJu6oEXhEgUgnu0j2WYxA'
    consumer_secret = 'viM8ejHgtEmtPTHd'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'token.html', {"token":validated_mpesa_access_token})

def pay(request):
   return render(request, 'pay.html')


def stk(request):
    if request.method == "POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        request_data = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/callback",
            "AccountReference": "Medilab",
            "TransactionDesc": "Appointment"
        }
        response = requests.post(api_url, json=request_data, headers=headers)

        response_data = response.json()
        transaction_id = response_data.get("CheckoutRequestID", "N/A")
        result_code = response_data.get("ResponseCode", "1")  # 0 is success, 1 is failure

        if result_code == "0":
            # Only save transaction if it was successful
            transaction = Transaction(
                phone_number=phone,
                amount=amount,
                transaction_id=transaction_id,
                status="Success"
            )
            transaction.save()

            return HttpResponse(f"Transaction ID: {transaction_id}, Status: Success")
        else:
            return HttpResponse(f"Transaction Failed. Error Code: {result_code}")




def transactions_list(request):
    transactions = Transaction.objects.all().order_by('-date')
    return render(request, 'transactions.html', {'transactions': transactions})

