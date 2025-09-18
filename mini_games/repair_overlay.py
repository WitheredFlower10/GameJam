import arcade
import time


class RepairMinigameOverlay:
    """Mini-jeu simple de calibration pour réparer un module du vaisseau.

    Contexte: L'écran de surveillance grésille à cause d'un désalignement de phase.
    Il faut calibrer le régulateur en appuyant sur ESPACE quand l'aiguille
    passe dans la zone verte. 2 validations suffisent.
    """

    def __init__(self, window, on_exit_callback=None, mission_system=None, completion_attr: str = "repair_completed", title: str = "CALIBRATION DU RÉGULATEUR"):
        self.window = window
        self.on_exit_callback = on_exit_callback
        self.mission_system = mission_system
        self.completion_attr = completion_attr
        self.title = title

        # Overlay dimensions (en pixels écran)
        self.panel_w = int(self.window.width * 0.4)
        self.panel_h = int(self.window.height * 0.25)

        # Animation de l'aiguille (0..1)
        self.pos = 0.0
        self.speed = 0.9  # unités par seconde
        self.direction = 1.0

        # Zone verte (cible)
        self.zone_left = 0.47
        self.zone_right = 0.53

        # Succès requis
        self.required_hits = 2
        self.hits = 0

        # Anti-spam
        self._last_key_time = 0.0
        self._debounce = 0.25

        self.active = True
        self._last_time = time.time()

    def _update_anim(self):
        now = time.time()
        dt = now - self._last_time
        self._last_time = now

        # Avancer l'aiguille
        self.pos += self.direction * self.speed * dt
        if self.pos > 1.0:
            self.pos = 1.0
            self.direction = -1.0
        elif self.pos < 0.0:
            self.pos = 0.0
            self.direction = 1.0

    def _success(self):
        self.hits += 1
        if self.hits >= self.required_hits:
            # Succès: marquer comme réparé et fermer
            if self.mission_system is not None:
                try:
                    if isinstance(self.completion_attr, str) and self.completion_attr:
                        setattr(self.mission_system, self.completion_attr, True)
                    else:
                        # Fallback
                        self.mission_system.repair_completed = True
                except Exception:
                    pass
            self.close()

    def close(self):
        self.active = False
        if callable(self.on_exit_callback):
            try:
                self.on_exit_callback()
            except Exception:
                pass

    def on_key_press(self, key, modifiers):
        now = time.time()
        if (now - self._last_key_time) < self._debounce:
            return
        self._last_key_time = now

        if key == arcade.key.ESCAPE:
            # Annuler sans réussir
            self.close()
            return

        if key == arcade.key.SPACE:
            # Vérifier si dans la zone
            if self.zone_left <= self.pos <= self.zone_right:
                self._success()
            return

    def on_draw(self):
        # Mettre à jour l'animation indépendamment d'on_update
        self._update_anim()

        # Fond assombri
        arcade.draw_lrbt_rectangle_filled(0, self.window.width, 0, self.window.height, (0, 0, 0, 140))

        # Panneau en bas à droite
        right = self.window.width - 30
        left = right - self.panel_w
        bottom = 30
        top = bottom + self.panel_h
        cx = (left + right) // 2
        cy = (bottom + top) // 2

        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.DARK_SLATE_GRAY)
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.LIGHT_GRAY, 3)

        # Titre et instructions
        arcade.draw_text(self.title, cx, top - 30, arcade.color.GOLD, 16, anchor_x="center")
        arcade.draw_text("ESPACE: Valider | ESC: Fermer", cx, bottom + 20, arcade.color.LIGHT_GRAY, 12, anchor_x="center")

        # Barre de calibration
        bar_left = left + 30
        bar_right = right - 30
        bar_y = cy
        arcade.draw_line(bar_left, bar_y, bar_right, bar_y, arcade.color.WHITE, 2)

        # Zone verte
        zl = bar_left + (bar_right - bar_left) * self.zone_left
        zr = bar_left + (bar_right - bar_left) * self.zone_right
        arcade.draw_lrbt_rectangle_filled(zl, zr, bar_y - 8, bar_y + 8, arcade.color.DARK_SPRING_GREEN)

        # Aiguille
        px = bar_left + (bar_right - bar_left) * self.pos
        arcade.draw_line(px, bar_y - 18, px, bar_y + 18, arcade.color.ORANGE, 3)

        # Progression
        progress_text = f"Validations: {self.hits}/{self.required_hits}"
        arcade.draw_text(progress_text, cx, bar_y + 30, arcade.color.WHITE, 12, anchor_x="center")


