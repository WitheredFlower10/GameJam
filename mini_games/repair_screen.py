import arcade
import textwrap

#à ajouter dans constatnts.py
TARGET_PHRASE = "LIBERTE EGALITE FRATERNITE"
MAX_ATTEMPTS = 15
MAX_FINAL_TRIES = 3
MAX_TERMINAL_LINES = 80

class RepairScreenGame:
    def __init__(self, window, on_finish_callback=None, main_terminal_view=None):
        self.window = window
        self.on_finish_callback = on_finish_callback
        self.main_terminal_view = main_terminal_view
        self._reset_state()


    def on_draw(self):
        term_green = (0, 255, 0)
        font_terminal = "ByteBounce"
        w, h = 450, 300
        screen_width, screen_height = self.window.width, self.window.height
        x = screen_width - w - 30
        y = screen_height - h - 30

        # arrière-plan + bordure
        arcade.draw_lrbt_rectangle_filled(x, x+w, y, y+h, (0, 0, 0, 230))
        arcade.draw_lrbt_rectangle_outline(x, x+w, y, y+h, term_green, 2)

        # titre
        arcade.draw_text("Connexion a l'ecran", x+18, y+h-38, term_green, 18, font_name=font_terminal, bold=True)

        # afficher la phrase chiffrée
        arcade.draw_text("MOT DE PASSE :", x+18, y+h-68, term_green, 16, font_name=font_terminal)
        masked = self.get_masked_phrase()
        arcade.draw_text(masked, x+32, y+h-90, term_green, 13, font_name=font_terminal)

        # historique (auto-wrap)
        option_gap = 20
        max_lines = 3 
        max_width = w - 64
        font_size = 15
        char_width = 8  # estimation de la largeur d'un caractère
        max_chars_per_line = max_width // char_width
        lines = self.terminal_lines[-max_lines:]
        y_draw = y+h-120
        for line in lines:
            wrapped = textwrap.wrap(line, width=max_chars_per_line)
            for subline in wrapped:
                arcade.draw_text(subline, x+32, y_draw, term_green, font_size, font_name=font_terminal)
                y_draw -= option_gap

        # ligne de saisie
        prompt = "> "
        if self.state == "guessing":
            arcade.draw_text(f"{prompt}{self.input_letter}", x+32, y+32, term_green, 14, font_name=font_terminal)
        elif self.state == "final":
            arcade.draw_text(f"{prompt}{self.input_final}", x+32, y+32, term_green, 14, font_name=font_terminal)
        elif self.state == "finished":
            # message alignement
            msg_lines = textwrap.wrap(self.message, width=48)
            y_msg = y+32
            for line in msg_lines:
                arcade.draw_text(line, x+32, y_msg, arcade.color.GREEN, 14, font_name=font_terminal)
                y_msg -= 18
        elif self.state == "failed":
            msg_lines = textwrap.wrap(self.message, width=48)
            y_msg = y+32
            for line in msg_lines:
                arcade.draw_text(line, x+32, y_msg, arcade.color.RED, 14, font_name=font_terminal)
                y_msg -= 18

    def on_text(self, text: str):
    # Saisie texte : une lettre à la fois pour le devin, A–Z et espace pour la phase finale
        if self.state == "guessing":
            if len(text) == 1 and text.isalpha():
                self.input_letter = text.upper()


    def on_key_press(self, key, modifiers):
        if self.state == "guessing":
            if key == arcade.key.BACKSPACE:
                self.input_letter = ""
            elif key in (arcade.key.ENTER, arcade.key.RETURN):
                self._commit_letter_guess()
            elif arcade.key.A <= key <= arcade.key.Z:
                self.input_letter = chr(key).upper()
        elif self.state in ("finished", "failed"):
            if key in (arcade.key.ENTER, arcade.key.RETURN):
                if self.state == "finished" and self.main_terminal_view is not None:
                    self.main_terminal_view.screen_connected = True
                if self.on_finish_callback:
                    self.on_finish_callback(success=(self.state == "finished"))



    # ---------- Logique ----------
    def _commit_letter_guess(self):
        if not self.input_letter:
            return
        letter = self.input_letter
        self.input_letter = ""

        if letter in self.guessed_letters:
            self._log("Veuillez entrer une lettre differente !")
            return

        self.guessed_letters.add(letter)

        if letter in TARGET_PHRASE:
            self.attemps += 1
            self._log(f"Lettre correcte : {letter} (restants {MAX_ATTEMPTS - self.attemps})")
            
        else:
            self.attemps += 1
            self._log(f"Lettre incorrecte : {letter} (restants {MAX_ATTEMPTS - self.attemps})")

    # Toutes les lettres révélées → succès immédiat
        if self._all_revealed():
            self._log("Toutes les lettres sont revelees. Reparation reussie !")
            self.state = "finished"
            self.message = "Connexion reussie. Appuyez sur Entree pour revenir au terminal."
            return


    # Nombre d'essais épuisé → échec immédiat
        if self.attemps >= MAX_ATTEMPTS:
            self._log("Échec : trop de tentatives.")
            self.state = "failed"
            self.message = "Échec de la connexion. Appuyez sur Entree pour quitter."
            return

    def get_masked_phrase(self):
        return ' '.join([c if c == ' ' or c in self.guessed_letters else '_' for c in TARGET_PHRASE])

    def _all_revealed(self):
    # Toutes les lettres sauf espace sont dans guessed_letters
        return all((c == ' ') or (c in self.guessed_letters) for c in TARGET_PHRASE)

    def _log(self, text):
        self.terminal_lines.append(text)
        if len(self.terminal_lines) > MAX_TERMINAL_LINES:
            self.terminal_lines = self.terminal_lines[-MAX_TERMINAL_LINES:]

    def _reset_state(self):
        self.guessed_letters = set()
        self.attemps = 0
        self.input_letter = ""
        self.input_final = ""
        self.state = "guessing"   # guessing, final, finished, failed
        self.message = ""
        self.final_attempts = 0
        self.terminal_lines = [
            "Connexion distante chiffree. Vous devez dechiffrer le mot de passe. Entrez une lettre et appuyez sur Entree pour commencer a deviner. une lettre du mot de passe, vous avez 15 tentatives pour deviner tous les lettres."
        ]
