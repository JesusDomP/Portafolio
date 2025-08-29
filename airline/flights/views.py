from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import OperationalError
from . import models
from collections import defaultdict


def to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


def dict_keys_to_camel(d: dict) -> dict:
    return {to_camel(k): v for k, v in d.items()}


def assign_seats_v2(flight, bps):
    """
    Asignación de asientos con reglas:
    - Mantener asientos ya asignados
    - Agrupar pasajeros por purchase_id
    - Menores (<18) deben quedar junto a un adulto de su grupo
    """
    # 1) Obtener asientos del avión
    seats = list(
        models.Seat.objects.filter(airplane_id=flight.airplane_id)
        .order_by("seat_row", "seat_column")
        .values("seat_id", "seat_row", "seat_column")
    )

    # 2) Ocupados (ya asignados)
    occupied = {bp["seat_id"] for bp in bps if bp["seat_id"]}
    seat_map = {s["seat_id"]: s for s in seats}

    # 3) Agrupar boarding passes por purchase_id
    groups = defaultdict(list)
    for bp in bps:
        groups[bp["purchase_id"]].append(bp)

    # 4) Funciones auxiliares
    def find_next_free():
        for s in seats:
            if s["seat_id"] not in occupied:
                yield s["seat_id"]

    free_seats_iter = find_next_free()

    def assign_to_seat(bp, seat_id):
        bp["seat_id"] = seat_id
        occupied.add(seat_id)

    def are_adjacent(seat_a, seat_b):
        """Verifica si dos asientos son contiguos (misma fila y col +1 o -1)."""
        if not seat_a or not seat_b:
            return False
        return (
            seat_map[seat_a]["seat_row"] == seat_map[seat_b]["seat_row"]
            and abs(
                ord(seat_map[seat_a]["seat_column"][0])
                - ord(seat_map[seat_b]["seat_column"][0])
            )
            == 1
        )

    # 5) Recorrer grupos
    for purchase_id, group in groups.items():
        adults = [bp for bp in group if bp["age"] >= 18]
        minors = [bp for bp in group if bp["age"] < 18]

        # A) Si no hay menores → asignar normalmente
        if not minors:
            for bp in group:
                if not bp["seat_id"]:
                    assign_to_seat(bp, next(free_seats_iter, None))
            continue

        # B) Hay menores → primero asignar adultos
        for bp in adults:
            if not bp["seat_id"]:
                assign_to_seat(bp, next(free_seats_iter, None))

        # C) Colocar menores junto a un adulto
        for bp in minors:
            if bp["seat_id"]:
                continue  # ya tenía asiento asignado
            placed = False
            for adult in adults:
                if adult["seat_id"]:
                    # buscar asiento contiguo libre
                    for s in seats:
                        if (
                            s["seat_id"] not in occupied
                            and are_adjacent(adult["seat_id"], s["seat_id"])
                        ):
                            assign_to_seat(bp, s["seat_id"])
                            placed = True
                            break
                if placed:
                    break
            # Si no encontró al lado de adulto → asignar al siguiente libre
            if not placed:
                assign_to_seat(bp, next(free_seats_iter, None))

    return bps


class FlightPassengersView(APIView):
    def get(self, request, flight_id: int):
        try:
            # 1) Buscar el vuelo
            try:
                flight = models.Flight.objects.select_related("airplane").get(
                    flight_id=flight_id
                )
            except models.Flight.DoesNotExist:
                return Response(
                    {"code": 404, "data": {}},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # 2) Traer boarding passes + pasajeros
            raw_bps = list(
                models.BoardingPass.objects.select_related("passenger")
                .filter(flight_id=flight_id)
                .values(
                    "boarding_pass_id",
                    "seat_id",
                    "seat_type_id",
                    "purchase_id",
                    "passenger_id",
                    "passenger__dni",
                    "passenger__name",
                    "passenger__age",
                    "passenger__country",
                )
            )

            
            bps = []
            for bp in raw_bps:
                bps.append({
                    "boarding_pass_id": bp["boarding_pass_id"],
                    "seat_id": bp["seat_id"],
                    "seat_type_id": bp["seat_type_id"],
                    "purchase_id": bp["purchase_id"],
                    "passenger_id": bp["passenger_id"],
                    "dni": bp["passenger__dni"],
                    "name": bp["passenger__name"],
                    "age": bp["passenger__age"],
                    "country": bp["passenger__country"],
                })

            # Asignar asientos según reglas 
            bps = assign_seats_v2(flight, bps)

            # 5) Construir la respuesta
            data = {
                "flight_id": flight.flight_id,
                "takeoff_date_time": flight.takeoff_date_time,
                "takeoff_airport": flight.takeoff_airport,
                "landing_date_time": flight.landing_date_time,
                "landing_airport": flight.landing_airport,
                "airplane_id": flight.airplane_id,
                "passengers": [],
            }

            for bp in bps:
                data["passengers"].append(dict_keys_to_camel(bp))

            return Response(
                {"code": 200, "data": dict_keys_to_camel(data)},
                status=status.HTTP_200_OK,
            )

        except OperationalError:
            return Response(
                {"code": 400, "errors": "could not connect to db"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except models.Flight.DoesNotExist:
            return Response(
                {"code": 404, "data": {}},
                status=status.HTTP_404_NOT_FOUND,
            )