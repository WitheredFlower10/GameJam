import arcade
import string

TARGET_PHRASE = "LIBERTE EGALITE FRATERNITE"
MAX_ATTEMPTS = 15
MAX_FINAL_TRIES = 3
MAX_TERMINAL_LINES = 80

class RepairScreenGame(arcade.View):
    def __init__(self, on_finish_callback=None):
        super().__init__()
        self.on_finish_callback = on_finish_callback
        self._reset_state()

    # ---------- Cycle de vie ----------
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
    # Enregistrer la police pixel personnalisée
        arcade.load_font("./assets/ARCADECLASSIC.TTF")

    def on_draw(self):
        self.clear()
        term_green = (0, 255, 0)

    # Haut : mot de passe à déchiffrer (masqué)
        font_terminal = "ArcadeClassic"
        arcade.draw_text("MOT DE PASSE ENCRYPTE :", 60, 710, term_green, 20, width=900, font_name=font_terminal)
        masked = self.get_masked_phrase()
        arcade.draw_text(masked, 60, 670, term_green, 20, width=900, font_name=font_terminal)

    # Bordure du terminal
        term_x, term_y = 40, 80
        term_w, term_h = 900, 560
        arcade.draw_lrbt_rectangle_outline(term_x, term_x + term_w, term_y, term_y + term_h, term_green, 3)

    # Pas de barre d'état, passer directement à l'historique
        y = term_y + term_h - 40

        # Historique du terminal (gestion du saut de ligne automatique)
        import textwrap
        max_width = term_w - 40
        font_size = 20
        char_width = 12  # Approximation pour la police ArcadeClassic
        max_chars_per_line = max_width // char_width
        lines = self.terminal_lines[-15:]
        wrapped_lines = []
        for line in lines:
            wrapped = textwrap.wrap(line, width=max_chars_per_line)
            wrapped_lines.extend(wrapped if wrapped else [""])
        y_draw = y
        for line in wrapped_lines:
            arcade.draw_text(line, term_x + 20, y_draw, term_green, font_size, width=max_width, font_name=font_terminal)
            y_draw -= font_size + 4

    # Ligne de saisie actuelle
        prompt = ">   "
        prompt_font_size = 15
        if self.state == "guessing":
            arcade.draw_text(f"{prompt}{self.input_letter}", term_x + 20, term_y + 20, term_green, prompt_font_size, width=term_w-40, font_name=font_terminal, multiline=True)
        elif self.state == "final":
            arcade.draw_text(f"{prompt}{self.input_final}", term_x + 20, term_y + 20, term_green, prompt_font_size, width=term_w-40, font_name=font_terminal, multiline=True)
        elif self.state == "finished":
            arcade.draw_text(self.message, term_x + 20, term_y + 20, arcade.color.GREEN, 20, font_name=font_terminal)
        elif self.state == "failed":
            arcade.draw_text(self.message, term_x + 20, term_y + 20, arcade.color.RED, 20, font_name=font_terminal)

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
                if self.on_finish_callback:
                    self.on_finish_callback(success=(self.state == "finished"))



    # ---------- Logique ----------
    def _commit_letter_guess(self):
        if not self.input_letter:
            return
        letter = self.input_letter
        self.input_letter = ""

        if letter in self.guessed_letters:
            self._log("Veuillez   entrer   une   lettre   differente !")
            return

        self.guessed_letters.add(letter)

        if letter in TARGET_PHRASE:
            self.attemps += 1
            self._log(f"Lettre   correcte :   {letter} (restants {MAX_ATTEMPTS - self.attemps})")
            
        else:
            self.attemps += 1
            self._log(f"Lettre   incorrecte :   {letter} (restants {MAX_ATTEMPTS - self.attemps})")

    # Toutes les lettres révélées → succès immédiat
        if self._all_revealed():
            self._log("Toutes les lettres sont revelees. Reparation reussie !")
            self.state = "finished"
            self.message = "Connexion   reussie.   Appuyez   sur   Entree   pour   quitter."
            return


    # Nombre d'essais épuisé → échec immédiat
        if self.attemps >= MAX_ATTEMPTS:
            self._log("Échec : trop de tentatives.")
            self.state = "failed"
            self.message = "Échec   de   la   connexion.   Appuyez   sur   Entree   pour   quitter."
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
            "Connexion   distante   chiffree.  Vous   devez   dechiffrer   le   mot   de   passe.  Entrez   une   lettre   et   appuyez   sur   Entree   pour   commencer   a   deviner   le   mot   de   passe."
        ]
