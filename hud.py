import pygame

def format_time(t):
    minutes = int(t // 60)
    seconds = int(t % 60)
    millis  = int((t - int(t)) * 1000)
    return f"{minutes:02}:{seconds:02}.{millis:03}"

class HUD:
    def __init__(self):
        self.font_big = pygame.font.SysFont("Arial", 42, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.previos = []
        self.last_sector_shown = None

    def draw(self, surface, car, track):
        screen_w, screen_h = surface.get_size()
        hud_x = 30
        hud_y = screen_h - 140

        # ---- TIMER ----
        current_time = format_time(car.lap_time)
        timer_text = self.font_big.render(current_time, True, (255,255,0))
        surface.blit(timer_text, (20, 20))

        # ---- LAST LAPS ----
        y_offset = 70

        for i, lap in enumerate(car.last_laps):
            color = (0,255,0) if lap == car.best_lap else (255,255,255)
            lap_text = self.font_small.render(f"{i+1}. {format_time(lap)}", True, color)
            surface.blit(lap_text, (20, y_offset))
            y_offset += 20

        # ---- BEST LAP ----
        if car.best_lap:
            best_text = self.font_small.render(f"Best: {format_time(car.best_lap)}", True, (255,215,0)) 
            surface.blit(best_text, (20, y_offset+10))

        if track.record_lap is not None:
            record_text = self.font_small.render(f"Record: {format_time(track.record_lap)}", True, (255,100,0)) 
            surface.blit(record_text, (20, y_offset+30))

        # ---- SECTOR INFO ----
        if car.last_sector_time is not None:

            sector_number = car.current_sector if car.current_sector != 0 else 4
            sector_label = f"S{sector_number}"

            partial_str = format_time(car.last_sector_time)

            # acumulado = último split guardado
            if car.current_splits:
                accumulated = car.current_splits[-1]
                accumulated_str = format_time(accumulated)
            else:
                # accumulated_str = "--:--.---"
                accumulated_str = format_time(car.last_laps[0]) 

            # GAP
            if car.last_sector_gap is not None:
                gap_val = car.last_sector_gap
                if gap_val >= 0:
                    gap_str = f"+{gap_val:.3f}"
                    gap_color = (255,0,0)
                else:
                    gap_str = f"{gap_val:.3f}"
                    gap_color = (0,255,0)
            else:
                gap_str = "--"
                gap_color = (255,255,255)

            text = f"{sector_label}  {partial_str} | {accumulated_str} | {gap_str}"

            if car.current_sector != self.last_sector_shown:
                self.previos.insert(0, (text, gap_color))
                self.previos = self.previos[:3]
                self.last_sector_shown = car.current_sector
            for i, (linea, color) in enumerate(self.previos):
                text_surface = self.font_small.render(linea, True, color)
                surface.blit(text_surface, (300, 25 + i * 20))

        # Tablero
        speed = car.speed_kmh()
        speed_text = self.font_big.render(f"{speed:6.1f} km/h", True, (255,255,255))
        surface.blit(speed_text, (hud_x - 40, hud_y - 10))

        bar_width = 25
        bar_height = 80

        # THR
        pygame.draw.rect(surface, (50,50,50), (hud_x, hud_y+60, bar_width, bar_height))
        pygame.draw.rect(surface, (0,200,0),
            (hud_x, hud_y+60 + (bar_height - bar_height*car.throttle_input),
             bar_width, bar_height*car.throttle_input))
        surface.blit(self.font_small.render("THR", True, (255,255,255)), (hud_x, hud_y + 40))

        # BRK
        pygame.draw.rect(surface, (50,50,50), (hud_x+35, hud_y+60, bar_width, bar_height))
        pygame.draw.rect(surface, (200,0,0),
            (hud_x+35, hud_y+60 + (bar_height - bar_height*car.brake_input),
             bar_width, bar_height*car.brake_input))
        surface.blit(self.font_small.render("BRK", True, (255,255,255)), (hud_x + 35, hud_y + 40))

        # REV
        if car.reverse_input:
            surface.blit(self.font_big.render("R", True, (255,0,0)), (hud_x + 70, hud_y + 50))

    def draw_minimap(self, surface, track, car):

        minimap_scale = 0.02

        minimap = pygame.transform.scale(
            track.image,
            (int(track.rect.width*minimap_scale),
             int(track.rect.height*minimap_scale))
        )

        screen_w, screen_h = surface.get_size()
        x = screen_w - minimap.get_width() - 20
        y = 20

        surface.blit(minimap, (x,y))

        mini_car_x = x + car.position.x * minimap_scale
        mini_car_y = y + car.position.y * minimap_scale

        pygame.draw.circle(surface, (255,0,0), (int(mini_car_x), int(mini_car_y)), 4)

