from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import EnergyConsumption, EnergyPurchased
from .forms import EnergyConsumptionForm, EnergyPurchasedForm
from django.core.paginator import Paginator


def energy_consumption_list(request):
    """Wyświetla listę rekordów zużycia energii z możliwością filtrowania."""
    records = EnergyConsumption.objects.all().order_by('-year', 'company')
    company = request.GET.get('company', '').strip()
    year_str = request.GET.get('year', '').strip()

    if company:
        records = records.filter(company__icontains=company)

    if year_str:
        try:
            year = int(year_str)
            records = records.filter(year=year)
        except ValueError:
            pass

    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    elided_page_range = paginator.get_elided_page_range(
        page_obj.number, on_each_side=2, on_ends=1
    )

    context = {
        'records': page_obj,
        'page_obj': page_obj,
        'page_range': elided_page_range,
        'title': 'Zużycie energii',
        'filter_company': company,
        'filter_year': year_str,
    }
    return render(request, 'emissions/energy_consumption_list.html', context)

#@login_required
def energy_consumption_add(request):
    """Formularz dodawania nowego rekordu zużycia energii."""
    if request.method == 'POST':
        form = EnergyConsumptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rekord zużycia energii został dodany.')
            return redirect('energy_consumption_list')
    else:
        form = EnergyConsumptionForm()

    return render(request, 'emissions/energy_consumption_form.html', {
        'form': form,
        'title': 'Dodaj zużycie energii'
    })


#@login_required
def energy_consumption_edit(request, pk):
    """Formularz edycji istniejącego rekordu zużycia energii."""
    record = get_object_or_404(EnergyConsumption, pk=pk)

    if request.method == 'POST':
        form = EnergyConsumptionForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rekord został zaktualizowany.')
            return redirect('energy_consumption_list')
    else:
        form = EnergyConsumptionForm(instance=record)

    return render(request, 'emissions/energy_consumption_form.html', {
        'form': form,
        'title': 'Edytuj zużycie energii'
    })


#@login_required
def energy_consumption_delete(request, pk):
    """Usuwa rekord zużycia energii po potwierdzeniu."""
    record = get_object_or_404(EnergyConsumption, pk=pk)

    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Rekord został usunięty.')
        return redirect('energy_consumption_list')

    return render(request, 'emissions/energy_consumption_confirm_delete.html', {
        'record': record,
        'title': 'Potwierdź usunięcie'
    })

def energy_purchased_list(request):
    """Wyświetla listę rekordów zakupionej energii z filtrowaniem i paginacją."""
    records = EnergyPurchased.objects.all().order_by('-year', 'company')
    company = request.GET.get('company', '').strip()
    year_str = request.GET.get('year', '').strip()

    if company:
        records = records.filter(company__icontains=company)
    if year_str:
        try:
            year = int(year_str)
            records = records.filter(year=year)
        except ValueError:
            pass

    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    elided_page_range = paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)

    context = {
        'records': page_obj,
        'page_obj': page_obj,
        'page_range': elided_page_range,
        'title': 'Zakupiona energia',
        'filter_company': company,
        'filter_year': year_str,
    }
    return render(request, 'emissions/energy_purchased_list.html', context)


#@login_required
def energy_purchased_add(request):
    if request.method == 'POST':
        form = EnergyPurchasedForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rekord zakupionej energii został dodany.')
            return redirect('energy_purchased_list')
    else:
        form = EnergyPurchasedForm()
    return render(request, 'emissions/energy_purchased_form.html', {
        'form': form,
        'title': 'Dodaj zakupioną energię'
    })


#@login_required
def energy_purchased_edit(request, pk):
    record = get_object_or_404(EnergyPurchased, pk=pk)
    if request.method == 'POST':
        form = EnergyPurchasedForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rekord został zaktualizowany.')
            return redirect('energy_purchased_list')
    else:
        form = EnergyPurchasedForm(instance=record)
    return render(request, 'emissions/energy_purchased_form.html', {
        'form': form,
        'title': 'Edytuj zakupioną energię'
    })


#@login_required
def energy_purchased_delete(request, pk):
    record = get_object_or_404(EnergyPurchased, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Rekord został usunięty.')
        return redirect('energy_purchased_list')
    return render(request, 'emissions/energy_purchased_confirm_delete.html', {
        'record': record,
        'title': 'Potwierdź usunięcie'
    })