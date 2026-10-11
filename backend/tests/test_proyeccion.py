from app.proyeccion import proyectar_horas, semaforo, tasa_desgaste_por_100h

def test_proyeccion_lineal():
    m = [(0, 40.0), (100, 38.0), (200, 36.0)]  # 2 mm por 100 h
    assert round(proyectar_horas(m, 30.0)) == 300  # cruza en h=500, hoy 200

def test_sin_desgaste():
    assert proyectar_horas([(0, 40.0), (100, 40.0)], 30.0) is None

def test_tasa():
    assert tasa_desgaste_por_100h([(0, 40.0), (200, 36.0)]) == 2.0

def test_semaforo():
    assert (semaforo(100), semaforo(450), semaforo(900)) == ("rojo", "amarillo", "verde")
