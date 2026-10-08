"""Tache 1 et 2 : serializers et validation.

A FAIRE :
  - SalleSerializer (ModelSerializer)
  - ReservationSerializer (ModelSerializer) :
      * le champ `utilisateur` est en LECTURE SEULE (il sera renseigne par la vue)
      * validation : `fin` strictement apres `debut`
      * validation : pas de chevauchement avec une autre reservation CONFIRMEE
        de la meme salle
"""
from rest_framework import serializers

from .models import Reservation, Salle  # noqa: F401  (a utiliser)

class SalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = ["id", "nom", "capacite", "batiment"]


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["id", "salle", "utilisateur", "debut", "fin","motif", "statut", "cree_le"]
        read_only_fields = ["utilisateur", "cree_le"]

    def validate(self, data):
        debut = data.get("debut", getattr(self.instance, "debut", None))
        fin = data.get("fin", getattr(self.instance, "fin", None))
        salle = data.get("salle", getattr(self.instance, "salle", None))
        statut = data.get("statut", getattr(self.instance, "statut", Reservation.Statut.CONFIRMEE))

        if debut and fin and fin <= debut:
            raise serializers.ValidationError("La fin doit être strictement postérieure au début.")

        if statut == Reservation.Statut.CONFIRMEE and debut and fin and salle:
            conflits = Reservation.objects.filter(salle=salle,statut=Reservation.Statut.CONFIRMEE,debut__lt=fin,fin__gt=debut)
            if self.instance:
                conflits = conflits.exclude(pk=self.instance.pk)
            if conflits.exists():
                raise serializers.ValidationError("Cette salle est déjà réservée sur ce créneau.")

        return data
