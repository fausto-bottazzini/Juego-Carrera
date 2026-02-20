import numpy as np
import pygame
from settings import *
from car import Car
from track import Track
from hud import HUD
from Telemetry import plot_telemetry
import json
import os, sys
import threading
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def resource_path(relative_path):
    """ Obtiene la ruta absoluta para recursos, funciona en dev y en PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

track_img = resource_path("assets/images/tracks/track_1.png")
mask_img = resource_path("assets/images/tracks/track_1-mask.png")
track = Track(track_img, mask_img)
car_image = resource_path("assets/images/cars/car_1.png")
car = Car(track.start.x, track.start.y, car_image)

hud = HUD()

# Cargar récord global si existe
if os.path.exists("best_lap_record.json"):
    with open("best_lap_record.json", "r") as f:
        data = json.load(f)
        track.record_lap = data["lap_time"]
        car.best_telemetry = data["telemetry"]
        print(f"Récord cargado: {track.record_lap:.3f}s")

def show_session_telemetry():
    if not os.path.exists("best_lap_record.json"):
        return
    if car.best_telemetry:
        plot_telemetry("best_lap_record.json", track_img)
    plt.show()

running = True
while running:
    dt = clock.tick(FPS)/1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False

    # if keys[pygame.K_k]:
    #     print(f"Posición: {car.position}")

    car.update(dt, keys)

    # Laps
    # ---- SECTORES ----
    if car.race_started:
        if car.current_sector < len(track.sectors):
            sector_line = track.sectors[car.current_sector]

            if track.crossed_line(car.prev_position, car.position, sector_line):
            
                # Tiempo sector
                sector_time = car.lap_time - car.sector_start_time
                split_time = car.lap_time
            
                # Guardar split actual
                car.current_splits.append(split_time)
            
                # Calcular gap contra mejor vuelta
                best_split = car.best_lap_splits[car.current_sector]
                if best_split is not None:
                    car.last_sector_gap = split_time - best_split
                else:
                    car.last_sector_gap = None
                car.last_sector_time = sector_time
            
                # Guardar mejor split si corresponde
                if best_split is None or split_time < best_split:
                    car.best_lap_splits[car.current_sector] = split_time

                car.sector_start_time = car.lap_time
                car.current_sector += 1

    # ---- META ----
    on_finish = track.crossed_line(car.prev_position, car.position, track.finish_line)
    if on_finish and not car.on_finish_last_frame:
        # Primera vez → iniciar carrera
        if not car.race_started:
            car.race_started = True
            car.lap_time = 0
            car.sector_start_time = 0
            car.current_sector = 0
            car.current_splits = []
            car.current_telemetry = []
            car.last_telemetry_time = 0
        else:
            if car.current_sector == len(track.sectors):
                lap_time = car.lap_time

                # Guardar vuelta
                car.last_laps.insert(0, lap_time)
                car.last_laps = car.last_laps[:5]

                car.last_sector_time = lap_time - car.sector_start_time
                car.current_splits.append(lap_time)
                # Calcular gap contra la meta de la mejor vuelta
                best_split_meta = car.best_lap_splits[3] 
                if best_split_meta is not None:
                    car.last_sector_gap = lap_time - best_split_meta
                else:
                    car.last_sector_gap = None

                # Mejor vuelta
                if car.best_lap is None or lap_time < car.best_lap:
                    car.best_lap = lap_time
                    car.best_lap_splits = list(car.current_splits)
                    if track.record_lap is None or lap_time < track.record_lap:
                        track.record_lap = lap_time
                        car.best_telemetry = list(car.current_telemetry)
                        
                        # Guardar en archivo JSON para persistencia
                        telemetry_data = {
                            "lap_time": car.best_lap,
                            "splits": car.best_lap_splits,
                            "telemetry": car.best_telemetry
                        }
                        def save_telemetry_async(data):   # Función que corre en paralelo
                            with open("best_lap_record.json", "w") as f:
                                json.dump(data, f)  # Sacamos el indent=4 para que escriba más rápido
                            print("¡Telemetría guardada en background!")
                        # Disparar el hilo para evitar el lag
                        threading.Thread(target=save_telemetry_async, args=(telemetry_data,)).start()

            # Reset vuelta
            car.lap_time = 0
            car.sector_start_time = 0
            car.current_sector = 0
            car.current_splits = []
            car.current_telemetry = []
            car.last_telemetry_time = 0

    car.on_finish_last_frame = on_finish


    # Limites de pista
    if not track.is_on_track(car.position):
        car.velocity -= car.velocity * OFFTRACK_DRAG * dt
        # print("Fuera de pista!")

    # Cámara
    cam_x = car.position.x - SCREEN_WIDTH//2
    cam_y = car.position.y - SCREEN_HEIGHT//2
    cam_x = max(0, min(cam_x, track.rect.width - SCREEN_WIDTH))
    cam_y = max(0, min(cam_y, track.rect.height - SCREEN_HEIGHT))
    offset = pygame.Vector2(cam_x, cam_y)

    # Limite mapa
    if car.position.x < 0:
        car.position.x = 0
        car.velocity.x = 0
    elif car.position.x > track.rect.width:
        car.position.x = track.rect.width
        car.velocity.x = 0
    if car.position.y < 0:
        car.position.y = 0
        car.velocity.y = 0
    elif car.position.y > track.rect.height:
        car.position.y = track.rect.height
        car.velocity.y = 0
    
    # Dibujar
    screen.fill((0,0,0))
    screen.blit(track.image, (-offset.x, -offset.y))
    track.draw_overlay(screen, offset)
    car.draw(screen, offset)

    hud.draw(screen, car, track)
    hud.draw_minimap(screen, track, car)

    pygame.display.flip()

pygame.quit()

show_session_telemetry()
