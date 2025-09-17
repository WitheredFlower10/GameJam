import arcade
import textwrap
import random

# Constantes du mini-jeu de chat d'oracle du terminal
QUESTIONS = [
    "Quel est ton rêve préféré?",
    "Si tu pouvais voyager n'importe où, où irais-tu?",
    "Quel animal aimerais-tu être?",
    "Quelle est ta couleur porte-bonheur?",
    "Quel est le prénom de ton premier ami?",
    "Quel est le dernier film que tu as vu?",
    "Quel plat te rend heureux?",
    "Quelle chanson écoutes-tu en boucle?",
    "Si tu pouvais avoir un super-pouvoir, lequel choisirais-tu?",
    "Quel est le plus beau souvenir de ton enfance?"
]

# Résultats d'oracle prédéfinis
FORTUNE_RESULTS = [
    "Le vent souffle en faveur de l'adversaire aujourd'hui...",
    "L'ombre de l'ennemi semble légère, c'est le moment d'agir.",
    "Une force tranquille habite ton héros en ce jour.",
    "Un voile de fatigue effleure ton champion, la prudence est de mise.",
    "L'adversaire hésite, ses pas sont incertains.",
    "L'énergie circule librement dans les veines de ton héros.",
    "Un défi de taille se profile à l'horizon, l'ennemi n'est pas à sous-estimer.",
    "La confiance rayonne autour de ton héros, rien ne semble impossible.",
    "L'adversaire se tient droit, prêt à tout, reste vigilant.",
    "La victoire semble sourire à ton héros, mais le destin reste mystérieux."
]

# Résultat d'oracle par défaut si l'index est dépassé
DEFAULT_RESULT = "Impossible de prédire aujourd'hui, mais préparez-vous à tout!"

MAX_TERMINAL_LINES = 80


class FortuneChatGame:
    def __init__(self, window, on_finish_callback=None, main_terminal_view=None):
        self.window = window
        self.on_finish_callback = on_finish_callback
        self.main_terminal_view = main_terminal_view
        self._reset_state()

    def on_draw(self):
        term_green = (0, 255, 0)
        font_terminal = "ByteBounce"
        # Paramètres de fenêtre unifiés, identiques à RepairScreenGame
        w, h = 450, 300
        screen_width, screen_height = self.window.width, self.window.height
        x = screen_width - w - 30
        y = screen_height - h - 30

    # Fond + bordure
        arcade.draw_lrbt_rectangle_filled(x, x+w, y, y+h, (0, 0, 0, 230))
        arcade.draw_lrbt_rectangle_outline(x, x+w, y, y+h, term_green, 2)

    # Titre
        arcade.draw_text("Future Chat", x+18, y+h-38, term_green, 18, font_name=font_terminal, bold=True)

    # Zone d'historique (retour à la ligne automatique)
        option_gap = 20
        max_lines = 5
        max_width = w - 64
        font_size = 12
        char_width = 8
        max_chars_per_line = max_width // char_width
        lines = self.terminal_lines[-max_lines:]
        y_draw = y+h-70
        for who, line in lines:
            prefix = "BOT: " if who == "bot" else "YOU: "
            for subline in textwrap.wrap(prefix + line, width=max_chars_per_line):
                arcade.draw_text(subline, x+32, y_draw, term_green, font_size, font_name=font_terminal)
                y_draw -= option_gap

    # Zone de saisie
        prompt = "> "
        if self.state == "asking":
            arcade.draw_text(f"{prompt}{self.input_text}", x+32, y+32, term_green, 14, font_name=font_terminal)
        elif self.state == "finished":
            for subline in textwrap.wrap(self.result, width=max_chars_per_line):
                arcade.draw_text(subline, x+32, y+32, arcade.color.GREEN, 14, font_name=font_terminal)

    def on_text(self, text: str):
        if self.state == "asking":
            if text.isprintable():
                self.input_text += text

    def on_key_press(self, key, modifiers):
        if self.state == "asking":
            if key == arcade.key.BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif key in (arcade.key.ENTER, arcade.key.RETURN):
                self._commit_answer()
        elif self.state == "finished":
            if key in (arcade.key.ENTER, arcade.key.RETURN):
                # Callback après la fin, afficher le terminal
                if self.on_finish_callback:
                    self.on_finish_callback(success=True)

    def _commit_answer(self):
        answer = self.input_text.strip()
        if not answer:
            return
        self.terminal_lines.append(("user", answer))
    # Calculer le nombre de mots
        index = len(answer) % len(FORTUNE_RESULTS)
    # Choisir le résultat de l'oracle
        result = FORTUNE_RESULTS[index]
        self.terminal_lines.append(("bot", result))
        self.result = result
        self.state = "finished"
        self.input_text = ""

    def _reset_state(self):
        self.terminal_lines = []
        self.input_text = ""
        self.state = "asking"
        self.result = ""
        self.current_question = random.choice(QUESTIONS)
        self.terminal_lines.append(("bot", "Bienvenue sur FUTUREBOT. Je vais vous poser une question sur la force de l'ennemi ou de votre héros..."))
        self.terminal_lines.append(("bot", self.current_question))
