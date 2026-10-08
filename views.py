"""Taches 3, 4, 5 (et bonus) : vues de l'API.

A FAIRE :
  - SalleViewSet (ModelViewSet), avec l'action `occupation` (tache 5)
  - ReservationViewSet (ModelViewSet), avec perform_create (tache 3)
"""
from rest_framework import viewsets,serializers,permissions  # noqa: F401  (a utiliser)

from .models import Reservation, Salle  # noqa: F401  (a utiliser)

from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .permissions import IsOwnerOrReadOnly
from .serializers import ReservationSerializer, SalleSerializer


class ReservationPagination(PageNumberPagination):
    page_size = 10  


class SalleViewSet(viewsets.ModelViewSet):
    queryset = Salle.objects.all()
    serializer_class = SalleSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve", "occupation"):
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @staticmethod
    def _lire_date(valeur):
        if not valeur:
            raise serializers.ValidationError("Les paramètres debut et fin sont requis.")
        try:
            dt = parse_datetime(valeur)
        except ValueError:
            dt = None
        if dt is None:
            raise serializers.ValidationError(f"Date invalide : {valeur}")
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
        return dt

    @action(detail=True, methods=["get"])
    def occupation(self, request, pk=None):
        salle = self.get_object()  

        debut = self._lire_date(request.query_params.get("debut"))
        fin = self._lire_date(request.query_params.get("fin"))
        if fin <= debut:
            raise serializers.ValidationError("fin doit être postérieure à debut.")

        reservations = salle.reservations.filter(statut=Reservation.Statut.CONFIRMEE,debut__lt=fin,fin__gt=debut)
        reserve = sum((min(r.fin, fin) - max(r.debut, debut)).total_seconds() for r in reservations)
        total = (fin - debut).total_seconds()

        return Response({"salle": salle.id,"debut": debut,"fin": fin,"heures_reservees": reserve / 3600,"taux_occupation": reserve / total})


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related("salle", "utilisateur")
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = ReservationPagination

    def get_queryset(self):
        qs = super().get_queryset()
        salle = self.request.query_params.get("salle")
        date = self.request.query_params.get("date")
        if salle:
            qs = qs.filter(salle_id=salle)
        if date:
            jour = parse_date(date)
            if jour is None:
                raise serializers.ValidationError({"date": "Format attendu : AAAA-MM-JJ."})
            qs = qs.filter(debut__date=jour)
        return qs

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)
