from __future__ import annotations

from functools import wraps

from django import forms
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.db import models
from django.forms import modelform_factory
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse


ADMIN_SESSION_KEY = "admin_panel_authenticated"


def _admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        if not request.session.get(ADMIN_SESSION_KEY):
            return redirect("admin_panel_login")
        return view_func(request, *args, **kwargs)

    return _wrapped


def _admin_models():
    app_config = apps.get_app_config("hotelapp")
    models_list = []
    for model in app_config.get_models():
        # Keep the panel limited to concrete models that have DB tables.
        if model._meta.abstract:
            continue
        models_list.append(
            {
                "name": model._meta.model_name,  # e.g. "booking_room"
                "label": model._meta.verbose_name_plural.title(),
            }
        )
    return sorted(models_list, key=lambda x: x["label"].lower())


def _get_model_or_404(model_name: str):
    try:
        return apps.get_model("hotelapp", model_name=model_name)
    except LookupError as exc:
        raise Http404("Model not found") from exc


def admin_login(request: HttpRequest) -> HttpResponse:
    if request.session.get(ADMIN_SESSION_KEY):
        return redirect("admin_panel_dashboard")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        if (
            username == getattr(settings, "ADMIN_PANEL_USERNAME", "admin")
            and password == getattr(settings, "ADMIN_PANEL_PASSWORD", "admin123")
        ):
            request.session[ADMIN_SESSION_KEY] = True
            request.session["admin_panel_username"] = username
            messages.success(request, "Logged in as admin.")
            return redirect("admin_panel_dashboard")

        messages.error(request, "Invalid admin credentials.")

    return render(
        request,
        "adminpanel/login.html",
        {
            "page_title": "Admin Login",
        },
    )


@_admin_required
def admin_logout(request: HttpRequest) -> HttpResponse:
    request.session.pop(ADMIN_SESSION_KEY, None)
    request.session.pop("admin_panel_username", None)
    messages.success(request, "Logged out.")
    return redirect("admin_panel_login")


@_admin_required
def admin_dashboard(request: HttpRequest) -> HttpResponse:
    Register = apps.get_model("hotelapp", "Register")
    Room = apps.get_model("hotelapp", "Room")
    BookingRoom = apps.get_model("hotelapp", "Booking_room")

    stats = {
        "users": Register.objects.count(),
        "rooms": Room.objects.count(),
        "bookings": BookingRoom.objects.count(),
        "bookings_success": BookingRoom.objects.filter(payment_status="SUCCESS").count(),
        "bookings_pending": BookingRoom.objects.filter(payment_status="PENDING").count(),
    }

    latest_bookings = BookingRoom.objects.select_related("user", "room").order_by("-created_at")[:10]

    return render(
        request,
        "adminpanel/dashboard.html",
        {
            "page_title": "Admin Dashboard",
            "admin_models": _admin_models(),
            "stats": stats,
            "latest_bookings": latest_bookings,
        },
    )


def _model_field_infos(model):
    infos = []
    for field in model._meta.fields:
        # Skip internal auto-created one-to-one pointers, etc.
        if getattr(field, "auto_created", False) and not field.concrete:
            continue
        infos.append(
            {
                "name": field.name,
                "label": field.verbose_name.title(),
                "is_image": isinstance(field, models.ImageField),
            }
        )
    return infos


@_admin_required
def admin_model_list(request: HttpRequest, model_name: str) -> HttpResponse:
    model = _get_model_or_404(model_name)
    objects = model.objects.all().order_by("-pk")[:500]
    field_infos = _model_field_infos(model)

    return render(
        request,
        "adminpanel/model_list.html",
        {
            "page_title": model._meta.verbose_name_plural.title(),
            "admin_models": _admin_models(),
            "model_name": model._meta.model_name,
            "model_label": model._meta.verbose_name_plural.title(),
            "objects": objects,
            "field_infos": field_infos,
        },
    )


def _build_modelform(model):
    class _BootstrapFormMixin(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                    continue
                existing = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = (existing + " form-control").strip()

    return modelform_factory(model, fields="__all__", form=_BootstrapFormMixin)


@_admin_required
def admin_model_add(request: HttpRequest, model_name: str) -> HttpResponse:
    model = _get_model_or_404(model_name)
    FormClass = _build_modelform(model)

    if request.method == "POST":
        form = FormClass(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"{model._meta.verbose_name.title()} created.")
            return redirect("admin_panel_model_list", model_name=model._meta.model_name)
    else:
        form = FormClass()

    return render(
        request,
        "adminpanel/model_form.html",
        {
            "page_title": f"Add {model._meta.verbose_name.title()}",
            "admin_models": _admin_models(),
            "model_name": model._meta.model_name,
            "model_label": model._meta.verbose_name_plural.title(),
            "form": form,
            "is_edit": False,
        },
    )


@_admin_required
def admin_model_edit(request: HttpRequest, model_name: str, pk: int) -> HttpResponse:
    model = _get_model_or_404(model_name)
    instance = model.objects.filter(pk=pk).first()
    if instance is None:
        raise Http404("Object not found")

    FormClass = _build_modelform(model)

    if request.method == "POST":
        form = FormClass(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, f"{model._meta.verbose_name.title()} updated.")
            return redirect("admin_panel_model_list", model_name=model._meta.model_name)
    else:
        form = FormClass(instance=instance)

    return render(
        request,
        "adminpanel/model_form.html",
        {
            "page_title": f"Edit {model._meta.verbose_name.title()}",
            "admin_models": _admin_models(),
            "model_name": model._meta.model_name,
            "model_label": model._meta.verbose_name_plural.title(),
            "form": form,
            "is_edit": True,
            "object": instance,
        },
    )


@_admin_required
def admin_model_delete(request: HttpRequest, model_name: str, pk: int) -> HttpResponse:
    model = _get_model_or_404(model_name)
    instance = model.objects.filter(pk=pk).first()
    if instance is None:
        raise Http404("Object not found")

    if request.method == "POST":
        instance.delete()
        messages.success(request, f"{model._meta.verbose_name.title()} deleted.")
        return redirect("admin_panel_model_list", model_name=model._meta.model_name)

    return render(
        request,
        "adminpanel/model_confirm_delete.html",
        {
            "page_title": f"Delete {model._meta.verbose_name.title()}",
            "admin_models": _admin_models(),
            "model_name": model._meta.model_name,
            "model_label": model._meta.verbose_name_plural.title(),
            "object": instance,
            "cancel_url": reverse("admin_panel_model_list", kwargs={"model_name": model._meta.model_name}),
        },
    )

