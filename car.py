import pygame
from settings import *

class Car:
    def __init__(self, x, y, car_image):

        self.position = pygame.Vector2(x,y)
        self.velocity = pygame.Vector2()

        self.prev_position = self.position.copy()

        self.angle = 180
        self.rotation_speed = 120

        self.max_speed = (MAX_SPEED_KMH / 3.6) / PIXEL_TO_METER
        self.min_speed = (MAX_REVERSE_KMH / 3.6) / PIXEL_TO_METER
        self.acceleration = ACCELERATION_MPS2 / PIXEL_TO_METER
        self.reverse_acceleration = REVERSE_ACCELERATION_MPS2 / PIXEL_TO_METER

        self.image_original = pygame.image.load(car_image).convert_alpha()
        w = int(self.image_original.get_width() * CAR_SCALE)
        h = int(self.image_original.get_height() * CAR_SCALE)
        self.image_original = pygame.transform.scale(self.image_original, (w,h))

        self.throttle_input = 0
        self.brake_input = 0
        self.reverse_input = 0

        # logica de vueltas y sectors
        self.race_started = False

        self.lap_time = 0
        self.current_sector = 0
        self.sector_start_time = 0

        self.last_sector_time = None
        self.last_sector_gap = None
        self.current_splits = []

        self.best_lap = None
        self.best_lap_splits = [None, None, None, None]

        self.last_laps = []
        
        self.on_finish_last_frame = False
    
        # Telemetria 
        self.current_telemetry = []
        self.best_telemetry = []
        self.telemetry_interval = 0.1  # Grabar 1 vez cada 0.1 segundos (10 Hz)
        self.last_telemetry_time = 0

    def update(self, dt, keys):
        if self.race_started:
            self.lap_time += dt

        # Guardar frame de telemetría
        if self.lap_time - self.last_telemetry_time >= self.telemetry_interval:
            self.current_telemetry.append({
                "t": round(self.lap_time, 3),
                "x": round(self.position.x, 2),
                "y": round(self.position.y, 2),
                "thr": self.throttle_input,
                "brk": self.brake_input,
                "rev": self.reverse_input})
            self.last_telemetry_time = self.lap_time

        forward = pygame.Vector2(1,0).rotate(-self.angle)
        speed_forward = self.velocity.dot(forward)

        # Rotación
        if keys[pygame.K_a] and self.velocity.length() > 2:
            self.angle += self.rotation_speed * dt
        if keys[pygame.K_d] and self.velocity.length() > 2:
            self.angle -= self.rotation_speed * dt

        # Inputs
        self.throttle_input = 1 if keys[pygame.K_w] else 0
        self.reverse_input  = 1 if keys[pygame.K_s] else 0
        self.brake_input    = 1 if keys[pygame.K_SPACE] else 0

        # Aceleración
        if self.throttle_input:
            self.velocity += forward * self.acceleration * dt

        if self.reverse_input:
            self.velocity -= forward * self.reverse_acceleration * dt
            if speed_forward < -self.min_speed:
                self.velocity -= forward * (speed_forward + self.min_speed)

        if self.brake_input and self.velocity.length() > 0:
            brake_accel = BRAKE_FORCE / PIXEL_TO_METER
            decel = brake_accel * dt

            if self.velocity.length() > decel:
                self.velocity -= self.velocity.normalize() * decel
            else:
                self.velocity = pygame.Vector2()

        #-- Fricción --

        # Drag aerodinámico suave (siempre activo)
        self.velocity -= self.velocity * DRAG * dt

        # Rolling resistance (solo cuando no acelera)
        if not self.throttle_input and not self.reverse_input:
            rolling = 2.0 / PIXEL_TO_METER
            decel = rolling * dt

            if self.velocity.length() > decel:
                self.velocity -= self.velocity.normalize() * decel
            else:
                self.velocity = pygame.Vector2()

        # Límite
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)

        self.prev_position = self.position.copy()
        self.position += self.velocity * dt

    def speed_kmh(self):
        return self.velocity.length() * PIXEL_TO_METER * 3.6 

    def draw(self, surface, offset):
        rotated = pygame.transform.rotate(self.image_original, self.angle)
        rect = rotated.get_rect(center=self.position - offset)
        surface.blit(rotated, rect)
