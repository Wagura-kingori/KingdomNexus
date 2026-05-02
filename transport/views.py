from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Route, Vehicle, StudentTransportAssignment, TransportPayment
from .forms import RouteForm, VehicleForm, TransportAssignmentForm, TransportPaymentForm
from students.models import Student, ClassGrade
from django.db.models import Sum

# ---------- Routes ----------
def routes_list(request):
    routes = Route.objects.all()
    return render(request, "transport/routes_list.html", {"routes": routes})


def route_create(request):
    form = RouteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Route saved.")
        return redirect('transport:routes')
    return render(request, "transport/route_form.html", {"form": form, "title": "Add Route"})


def route_edit(request, pk):
    inst = get_object_or_404(Route, pk=pk)
    form = RouteForm(request.POST or None, instance=inst)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Route updated.")
        return redirect('transport:routes')
    return render(request, "transport/route_form.html", {"form": form, "title": "Edit Route"})


# ---------- Vehicles ----------
def vehicles_list(request):
    vehicles = Vehicle.objects.select_related('route', 'driver').all()
    return render(request, "transport/vehicles_list.html", {"vehicles": vehicles})


def vehicle_create(request):
    form = VehicleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Vehicle added.")
        return redirect('transport:vehicles')
    return render(request, "transport/vehicle_form.html", {"form": form, "title": "Add Vehicle"})


def vehicle_edit(request, pk):
    inst = get_object_or_404(Vehicle, pk=pk)
    form = VehicleForm(request.POST or None, instance=inst)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Vehicle updated.")
        return redirect('transport:vehicles')
    return render(request, "transport/vehicle_form.html", {"form": form, "title": "Edit Vehicle"})


# ---------- Assignments ----------
def assignments_view(request):
    classes = ClassGrade.objects.all()
    selected_class = request.GET.get('classroom')
    students = None
    routes = Route.objects.all()
    selected_class_obj = None

    if selected_class:
        selected_class_obj = get_object_or_404(ClassGrade, pk=selected_class)
        students = Student.objects.filter(current_class=selected_class_obj).select_related('user')

    # Handle POST: save assignments per student
    if request.method == "POST":
        
        for student in Student.objects.filter(current_class=selected_class_obj):
            route_val = request.POST.get(f"route_{student.id}")
            vehicle_val = request.POST.get(f"vehicle_{student.id}")
            if route_val:
                route = Route.objects.filter(pk=route_val).first()
            else:
                route = None
            if vehicle_val:
                vehicle = Vehicle.objects.filter(pk=vehicle_val).first()
            else:
                vehicle = None

            if route is None and vehicle is None:
                # delete existing assignment if any
                StudentTransportAssignment.objects.filter(student=student).delete()
            else:
                assign, _ = StudentTransportAssignment.objects.get_or_create(student=student)
                assign.route = route
                assign.vehicle = vehicle
                assign.save()
        messages.success(request, "Assignments updated.")
        return redirect('transport:assignments')

    return render(request, "transport/transport_assignments.html", {
        "classes": classes,
        "students": students,
        "routes": routes,
        "selected_class": int(selected_class) if selected_class else None
    })


# ---------- Transport Fees / Payments ----------
def transport_fees_view(request):
    # Build a list of students with assignment info + payments summary
    assignments = StudentTransportAssignment.objects.select_related('student', 'route').all()
    data = []
    for a in assignments:
        total_paid = a.payments.aggregate(total=Sum('amount'))['total'] or 0
        fee = a.route.fee if a.route else 0
        balance = fee - total_paid
        data.append({
            "student": a.student,
            "route": a.route,
            "amount_paid": total_paid,
            "balance": balance,
        })
    return render(request, "transport/transport_fees.html", {"students": data})


def payments_list(request):
    payments = TransportPayment.objects.select_related('assignment__student').all()
    return render(request, "transport/payments_list.html", {"payments": payments})


def payment_create(request):
    form = TransportPaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Payment recorded.")
        return redirect('transport:payments')
    return render(request, "transport/payment_form.html", {"form": form, "title": "Record Payment"})
