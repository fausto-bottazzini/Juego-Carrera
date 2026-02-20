import pygame
from settings import TRACK_SCALE

class Track:
    def __init__(self, track_image, mask_image):

        original = pygame.image.load(track_image).convert()
        w = int(original.get_width() * TRACK_SCALE)
        h = int(original.get_height() * TRACK_SCALE)

        self.image = pygame.transform.scale(original, (w, h))
        self.rect = self.image.get_rect()

        mask_surface = pygame.image.load(mask_image).convert()
        mask_surface = pygame.transform.scale(mask_surface, (w, h))
        self.mask = pygame.mask.from_threshold(mask_surface, (255,255,255), (1,1,1))

        self.start = pygame.Vector2(495,512)  
        # parrilla de largada 
        # [4953.19, 5116.33] 
        # [5022.06, 4983.77]
        # [5175.32, 5113.93]

        # ---- META Y sectorS EN COORDENADAS BASE ----
        self.finish_base = pygame.Rect(480, 487, 5, 35)

        self.sectors_base = [
            ((212, 109), (193, 132)),   # 1940, 1304 // 2125.24, 1087.68 ([2160.04, 1311][1916.88, 1732.97])
            ((201, 396), (201, 368)),   # 2007.73, 3956.82 // 1998.4, 3679.26 ([1986.73, 3797.29] [2379.7, 3992.34])
            ((443, 129), (470, 140))    # 4691.36, 1388.06 // 4429.46, 1289.12 ([4404.73, 1607.21])
        ]

        self.record_lap = None

        self._scale_special_zones()

    def _scale_special_zones(self):
        s = TRACK_SCALE

        # Meta
        self.finish_line = (
            pygame.Vector2(self.finish_base.x * s, self.finish_base.y * s),
            pygame.Vector2((self.finish_base.x + self.finish_base.width) * s - 50 , (self.finish_base.y + self.finish_base.height) * s))

        # sectors
        self.sectors = []
        for p1, p2 in self.sectors_base:
            a = pygame.Vector2(p1[0] * s, p1[1] * s)
            b = pygame.Vector2(p2[0] * s, p2[1] * s)
            self.sectors.append((a, b))

        self.start = pygame.Vector2(self.start.x, self.start.y) * s

    def is_on_track(self, position):
        x, y = int(position.x), int(position.y)
        if 0 <= x < self.rect.width and 0 <= y < self.rect.height:
            return self.mask.get_at((x,y))
        return False

    def draw_overlay(self, surface, offset):
            # --- META (Línea Continua) ---
            # Usamos self.finish_line que ya contiene los Vector2 escalados
            p1_meta, p2_meta = self.finish_line
            pygame.draw.line(surface, (255, 255, 255), p1_meta - offset, p2_meta - offset, 8)

            # --- SECTORES (Líneas Rayadas) ---
            for a, b in self.sectors:
                # Calculamos la dirección y el largo del sector
                direction = b - a
                dist = direction.length()
                if dist == 0: continue
                
                unit_dir = direction.normalize()
                
                # Configuración del rayado
                dash_length = 15  # Largo de cada rayita blanca
                gap_length = 10   # Espacio entre rayitas
                step = dash_length + gap_length
                
                # Dibujamos segmentos a lo largo de la línea del sector
                for i in range(0, int(dist), step):
                    start_segment = a + unit_dir * i
                    # Evitamos que la última rayita se pase del punto final
                    end_dist = min(i + dash_length, dist)
                    end_segment = a + unit_dir * end_dist
                    
                    pygame.draw.line(surface, (255, 255, 255), 
                                    start_segment - offset, 
                                    end_segment - offset, 4)


    def crossed_line(self, p1, p2, line):
        a, b = line
        return self.segment_intersect(p1, p2, a, b)

    def segment_intersect(self, p1, p2, q1, q2):
        def ccw(A, B, C):
            return (C.y-A.y)*(B.x-A.x) > (B.y-A.y)*(C.x-A.x)

        return (ccw(p1,q1,q2) != ccw(p2,q1,q2) and
                ccw(p1,p2,q1) != ccw(p1,p2,q2))
