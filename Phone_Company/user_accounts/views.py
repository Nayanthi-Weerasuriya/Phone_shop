from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import SignUpForm, UserForm, UserProfileForm
from .models import UserProfile


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Welcome back!")
            return redirect("store")

        messages.error(request, "Username or password is incorrect.")

    return render(request, "user_accounts/user_login.html", {"title": "Sign in"})


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


def register_user(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        UserProfile.objects.get_or_create(user=user)
        login(request, user)
        messages.success(request, "Your account has been created. Welcome!")
        return redirect("home")

    return render(request, "user_accounts/register_user.html", {"form": form, "title": "Create account"})


@login_required
def edit_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_form = UserForm(request.POST or None, instance=request.user)
    profile_form = UserProfileForm(request.POST or None, request.FILES or None, instance=profile)

    if request.method == "POST" and user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("user_accounts:edit_profile")

    return render(request, "user_accounts/edit_profile.html", {
        "title": "Edit User Profile",
        "user_form": user_form,
        "profile_form": profile_form,
        "profile": profile,
    })
