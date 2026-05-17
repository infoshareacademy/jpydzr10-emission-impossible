from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import EnergyConsumption
from .forms import EnergyConsumptionForm


def energy_consumption_list(request):
    """Wyświetla listę wszystkich rekordów zużycia energii."""
    records = EnergyConsumption.objects.all().order_by('year', 'company')
    return render(request, 'emissions/energy_consumption_list.html', {
        'records': records,
        'title': 'Zużycie energii'
    })


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