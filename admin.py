from django.contrib import admin

from .models import Reservation, Salle


@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ("nom", "batiment", "capacite")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("salle", "utilisateur", "debut", "fin", "statut")
    list_filter = ("statut", "salle")
