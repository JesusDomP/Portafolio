from django.db import models


class Airplane(models.Model):
    airplane_id = models.AutoField(primary_key=True, db_comment='Identificador de la tabla')
    name = models.CharField(max_length=255, db_comment='Nombre del avi¾n')

    class Meta:
        managed = False
        db_table = 'airplane'


class BoardingPass(models.Model):
    boarding_pass_id = models.AutoField(primary_key=True, db_comment='Identificador de la tabla')
    purchase = models.ForeignKey('Purchase', models.DO_NOTHING, db_column="purchase_id", db_comment='Id de la compra')
    passenger = models.ForeignKey('Passenger', models.DO_NOTHING, db_column="passenger_id", db_comment='Id del pasajero')
    seat_type = models.ForeignKey('SeatType', models.DO_NOTHING, db_column="seat_type_id", db_comment='Id del tipo de asiento')
    seat = models.ForeignKey('Seat', models.DO_NOTHING, blank=True, null=True, db_column="seat_id", db_comment='Id del asiento')
    flight = models.ForeignKey('Flight', models.DO_NOTHING, db_column="flight_id", db_comment='Id del vuelo')

    class Meta:
        managed = False
        db_table = 'boarding_pass'


class Flight(models.Model):
    flight_id = models.AutoField(primary_key=True, db_comment='Identificador de la tabla')
    takeoff_date_time = models.IntegerField(db_comment='Fecha y hora del despegue')
    takeoff_airport = models.CharField(max_length=255, db_comment='Aeropuerto de despegue')
    landing_date_time = models.IntegerField(db_comment='Fecha y hora de aterrizaje')
    landing_airport = models.CharField(max_length=255, db_comment='Aeropuerto de aterrizaje')
    airplane = models.ForeignKey(Airplane, models.DO_NOTHING, db_column="airplane_id", db_comment='Id del avi¾n')

    class Meta:
        managed = False
        db_table = 'flight'


class Passenger(models.Model):
    passenger_id = models.AutoField(primary_key=True, db_comment='Identificador de la tabla')
    dni = models.CharField(max_length=255, db_comment='N·mero de identificaci¾n del pasajero')
    name = models.CharField(max_length=255, db_comment='Nombre completo del pasajero')
    age = models.IntegerField(db_comment='Edad del pasajero')
    country = models.CharField(max_length=255, db_comment='PaÝs del pasajero')

    class Meta:
        managed = False
        db_table = 'passenger'


class Purchase(models.Model):
    purchase_id = models.AutoField(primary_key=True, db_comment='Identificador de la tabla')
    purchase_date = models.IntegerField(db_comment='Fecha de la compra')

    class Meta:
        managed = False
        db_table = 'purchase'


class ScriptTable(models.Model):
    script_content = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'script_table'


class Seat(models.Model):
    seat_id = models.AutoField(primary_key=True, db_comment='Identificador de la tabla')
    seat_column = models.CharField(max_length=2, db_comment='Columna del asiento')
    seat_row = models.IntegerField(db_comment='Fila del asiento')
    seat_type = models.ForeignKey('SeatType', models.DO_NOTHING, db_column="seat_type_id", db_comment='Id del tipo de asiento {FK}')
    airplane = models.ForeignKey(Airplane, models.DO_NOTHING, db_column="airplane_id", db_comment='Id del avión al que pertenece el asiento')

    class Meta:
        managed = False
        db_table = 'seat'


class SeatType(models.Model):
    seat_type_id = models.AutoField(primary_key=True, db_comment='Identificador de la tabla')
    name = models.CharField(max_length=255, db_comment='Nombre del tipo de asiento')

    class Meta:
        managed = False
        db_table = 'seat_type'
