from django.conf import settings
from django.db import models


class Salle(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    capacite = models.PositiveIntegerField()
    batiment = models.CharField(max_length=100)

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return f"{self.nom} ({self.batiment})"


class Reservation(models.Model):
    class Statut(models.TextChoices):
        CONFIRMEE = "CONFIRMEE", "Confirmée"
        ANNULEE = "ANNULEE", "Annulée"

    salle = models.ForeignKey(
        Salle, on_delete=models.CASCADE, related_name="reservations"
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    debut = models.DateTimeField()
    fin = models.DateTimeField()
    motif = models.CharField(max_length=200)
    statut = models.CharField(
        max_length=10, choices=Statut.choices, default=Statut.CONFIRMEE
    )
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["debut"]

    def __str__(self):
        return f"{self.salle.nom} : {self.debut:%d/%m/%Y %H:%M} - {self.fin:%H:%M} ({self.utilisateur})"
