import random
import arcade

MENU_OPTIONS = [
    "Connecter a l'ecran",
    "Chat du futur ($20 chaque fois)",
    "Achat des infos($200)",
    "Exit Terminal"
    
]

class MainTerminal:
    def __init__(self, window, on_select_callback=None, on_exit_callback=None, screen_connected=False):
        self.window = window
        self.selected_index = 0
        self.on_select_callback = on_select_callback
        self.on_exit_callback = on_exit_callback
        self.font_terminal = "ByteBounce"
        self.screen_connected = screen_connected
    # Sous-état : None (menu principal), 'fortune', 'repair', 'info'
        self.sub_view = None
    # État pour l'affichage des informations achetées
        self.info_state = {
            'lines': [],
            'state': 'showing',
        }
    # État du chat du futur
        self.fortune_state = {
            'lines': [], 'input_text': '', 'result': '', 'state': 'asking', 'current_question': '', 'question_list': [
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
            ],
            'fortune_results': [
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
        }
    # État de l'écran de réparation
        self.repair_state = {
            'guessed_letters': set(),
            'attemps': 0,
            'input_letter': '',
            'state': 'guessing',
            'message': '',
            'terminal_lines': [
                "Connexion distante chiffree. Vous devez dechiffrer le mot de passe. Entrez une lettre et appuyez sur Entree pour commencer a deviner. une lettre du mot de passe, vous avez 15 tentatives pour deviner tous les lettres."
            ],
            'target_phrase': "LIBERTE EGALITE FRATERNITE"
        }

    @property
    def menu_options(self):
        if self.screen_connected:
            return ["Ecran deja connecte"] + MENU_OPTIONS[1:]
        else:
            return MENU_OPTIONS



    def on_draw(self):
        w, h = 450, 300
        screen_width, screen_height = self.window.width, self.window.height
        x = screen_width - w - 30
        y = screen_height - h - 30
        term_green = (0, 255, 0)
        font_terminal = self.font_terminal

    # Gestion des sous-vues
        if self.sub_view == 'fortune':
            self._draw_fortune(x, y, w, h, term_green, font_terminal)
            return
        elif self.sub_view == 'repair':
            self._draw_repair(x, y, w, h, term_green, font_terminal)
            return

    # Affichage des informations achetées
        if self.sub_view == 'info':
            self._draw_info(x, y, w, h, term_green, font_terminal)
            return

    # Menu principal
        arcade.draw_lrbt_rectangle_filled(x, x+w, y, y+h, (0, 0, 0, 230))
        arcade.draw_lrbt_rectangle_outline(x, x+w, y, y+h, term_green, 2)
        arcade.draw_text("Terminal", x+18, y+h-38, term_green, 18, font_name=font_terminal, bold=True)
        option_gap = 32
        for i, option in enumerate(self.menu_options):
            oy = y + h - 70 - i * option_gap
            if i == self.selected_index and not (self.screen_connected and i == 0):
                arcade.draw_lrbt_rectangle_outline(x+18, x+w-18, oy-6, oy+24, term_green, 2)
                bold = True
            else:
                bold = False
            arcade.draw_text(option, x+32, oy, term_green, 20, font_name=font_terminal, bold=bold)

    def on_key_press(self, key, modifiers):
    # Délégation selon le sous-état
        if self.sub_view == 'fortune':
            if key == arcade.key.ESCAPE:
                self.sub_view = None
            else:
                self._fortune_on_key_press(key, modifiers)
            return
        elif self.sub_view == 'repair':
            if key == arcade.key.ESCAPE:
                self.sub_view = None
            else:
                self._repair_on_key_press(key, modifiers)
            return

        elif self.sub_view == 'info':
            # Retour au menu principal avec Entrée ou Échap
            if key in (arcade.key.ENTER, arcade.key.RETURN, arcade.key.ESCAPE):
                self.sub_view = None
            return

        max_index = len(self.menu_options) - 1
        if key == arcade.key.UP:
            prev = self.selected_index
            while True:
                self.selected_index = (self.selected_index - 1) % (max_index + 1)
                if not (self.screen_connected and self.selected_index == 0):
                    break
                if self.selected_index == prev:
                    break
        elif key == arcade.key.DOWN:
            prev = self.selected_index
            while True:
                self.selected_index = (self.selected_index + 1) % (max_index + 1)
                if not (self.screen_connected and self.selected_index == 0):
                    break
                if self.selected_index == prev:
                    break
        elif key in (arcade.key.ENTER, arcade.key.RETURN):
            # Si le dernier élément (Exit Terminal) est sélectionné, fermer le terminal
            if self.selected_index == max_index:
                if self.on_exit_callback:
                    self.on_exit_callback()
                # Si pas de callback, marquer la fermeture (détectable de l'extérieur)
                if hasattr(self.window, 'parent_view') and hasattr(self.window.parent_view, 'terminal'):
                    self.window.parent_view.terminal = None
                return
            if not (self.screen_connected and self.selected_index == 0):
                # Ouvrir le chat du futur
                if self.menu_options[self.selected_index].startswith("Chat du futur"):
                    self._reset_fortune()
                    self.sub_view = 'fortune'
                # Ouvrir l'écran de réparation
                elif self.menu_options[self.selected_index].startswith("Connecter a l'ecran"):
                    self._reset_repair()
                    self.sub_view = 'repair'
                # Ouvrir l'affichage des informations achetées
                elif self.menu_options[self.selected_index].startswith("Achat des infos"):
                    self._reset_info()
                    self.sub_view = 'info'
                elif self.on_select_callback:
                    self.on_select_callback(self.selected_index)
    
    # -------- Vue d'informations achetées --------
    def _draw_info(self, x, y, w, h, term_green, font_terminal):
        import textwrap
        state = self.info_state
    # Générer le contenu une seule fois
        if not state['lines']:
            # Texte en français, sans accents, mais toujours en français
            info_text = (
                "Analyse des donnees :\n"
                "Heros :\n"
                "- Energie : 8*%\n"
                "- Etat mental : S**ide\n"
                "Ennemi :\n"
                "- Forces : Supe**eur\n"
                "- Faiblesses : De**ense faible\n"
                "(Appuyez sur Entree pour revenir au terminal)"
            )
            # Découper par ligne
            state['lines'] = info_text.split('\n')
    # Affichage
        arcade.draw_lrbt_rectangle_filled(x, x+w, y, y+h, (0, 0, 0, 230))
        arcade.draw_lrbt_rectangle_outline(x, x+w, y, y+h, term_green, 2)
        arcade.draw_text("Informations Achetees", x+18, y+h-38, term_green, 18, font_name=font_terminal, bold=True)
        option_gap = 22
        max_lines = 9
        y_draw = y+h-70
        for line in state['lines'][:max_lines]:
            for subline in textwrap.wrap(line, width=48):
                arcade.draw_text(subline, x+32, y_draw, term_green, 14, font_name=font_terminal)
                y_draw -= option_gap
    # Affichage défilant si besoin (à étendre si nécessaire)

    def _reset_info(self):
        self.info_state['lines'] = []
        self.info_state['state'] = 'showing'
    def on_text(self, text):
        if self.sub_view == 'fortune':
            self._fortune_on_text(text)
            return
        elif self.sub_view == 'repair':
            self._repair_on_text(text)
            return
    # Le menu principal n'accepte pas de saisie texte

    # -------- fortune chat 子界面 --------
    def _draw_fortune(self, x, y, w, h, term_green, font_terminal):
        import textwrap
        state = self.fortune_state
        # 初始化
        if not state['lines']:
            state['current_question'] = random.choice(state['question_list'])
            state['lines'].append(("bot", "Bienvenue sur FUTUREBOT. Je vais vous poser une question sur la force de l'ennemi ou de votre héros..."))
            state['lines'].append(("bot", state['current_question']))
        # 绘制
        arcade.draw_lrbt_rectangle_filled(x, x+w, y, y+h, (0, 0, 0, 230))
        arcade.draw_lrbt_rectangle_outline(x, x+w, y, y+h, term_green, 2)
        arcade.draw_text("Future Chat", x+18, y+h-38, term_green, 18, font_name=font_terminal, bold=True)
        option_gap = 20
        max_lines = 5
        max_width = w - 64
        font_size = 12
        char_width = 8
        max_chars_per_line = max_width // char_width
        lines = state['lines'][-max_lines:]
        y_draw = y+h-70
        for who, line in lines:
            prefix = "BOT: " if who == "bot" else "YOU: "
            for subline in textwrap.wrap(prefix + line, width=max_chars_per_line):
                arcade.draw_text(subline, x+32, y_draw, term_green, font_size, font_name=font_terminal)
                y_draw -= option_gap
        prompt = "> "
        if state['state'] == "asking":
            arcade.draw_text(f"{prompt}{state['input_text']}", x+32, y+32, term_green, 14, font_name=font_terminal)
       
    def _fortune_on_key_press(self, key, modifiers):
        state = self.fortune_state
        if state['state'] == "asking":
            if key == arcade.key.BACKSPACE:
                state['input_text'] = state['input_text'][:-1]
            elif key in (arcade.key.ENTER, arcade.key.RETURN):
                self._fortune_commit_answer()
        elif state['state'] == "finished":
            if key in (arcade.key.ENTER, arcade.key.RETURN):
                self.sub_view = None

    def _fortune_on_text(self, text):
        state = self.fortune_state
        if state['state'] == "asking":
            if text.isprintable():
                state['input_text'] += text
    
    

    def _fortune_commit_answer(self):
        state = self.fortune_state
        answer = state['input_text'].strip()
        if not answer:
            return
        state['lines'].append(("user", answer))
        index = len(answer) % len(state['fortune_results'])
        result = state['fortune_results'][index]
        state['lines'].append(("bot", result))
        state['result'] = result
        state['state'] = "finished"
        state['input_text'] = ""

    def _reset_fortune(self):
        self.fortune_state['lines'] = []
        self.fortune_state['input_text'] = ''
        self.fortune_state['result'] = ''
        self.fortune_state['state'] = 'asking'
        self.fortune_state['current_question'] = ''

    # -------- repair screen 子界面 --------
    def _draw_repair(self, x, y, w, h, term_green, font_terminal):
        import textwrap
        state = self.repair_state
        arcade.draw_lrbt_rectangle_filled(x, x+w, y, y+h, (0, 0, 0, 230))
        arcade.draw_lrbt_rectangle_outline(x, x+w, y, y+h, term_green, 2)
        arcade.draw_text("Connexion a l'ecran", x+18, y+h-38, term_green, 18, font_name=font_terminal, bold=True)
        arcade.draw_text("MOT DE PASSE :", x+18, y+h-68, term_green, 16, font_name=font_terminal)
        masked = self._get_masked_phrase()
        arcade.draw_text(masked, x+32, y+h-90, term_green, 13, font_name=font_terminal)
        option_gap = 20
        max_lines = 3
        max_width = w - 64
        font_size = 15
        char_width = 8
        max_chars_per_line = max_width // char_width
        lines = state['terminal_lines'][-max_lines:]
        y_draw = y+h-120
        for line in lines:
            wrapped = textwrap.wrap(line, width=max_chars_per_line)
            for subline in wrapped:
                arcade.draw_text(subline, x+32, y_draw, term_green, font_size, font_name=font_terminal)
                y_draw -= option_gap
        prompt = "> "
        if state['state'] == "guessing":
            arcade.draw_text(f"{prompt}{state['input_letter']}", x+32, y+32, term_green, 14, font_name=font_terminal)
        elif state['state'] == "finished":
            msg_lines = textwrap.wrap(state['message'], width=48)
            y_msg = y+32
            for line in msg_lines:
                arcade.draw_text(line, x+32, y_msg, arcade.color.GREEN, 14, font_name=font_terminal)
                y_msg -= 18
        elif state['state'] == "failed":
            msg_lines = textwrap.wrap(state['message'], width=48)
            y_msg = y+32
            for line in msg_lines:
                arcade.draw_text(line, x+32, y_msg, arcade.color.RED, 14, font_name=font_terminal)
                y_msg -= 18

    def _repair_on_key_press(self, key, modifiers):
        state = self.repair_state
        if state['state'] == "guessing":
            if key == arcade.key.BACKSPACE:
                state['input_letter'] = ""
            elif key in (arcade.key.ENTER, arcade.key.RETURN):
                self._repair_commit_letter_guess()
            elif arcade.key.A <= key <= arcade.key.Z:
                state['input_letter'] = chr(key).upper()
        elif state['state'] in ("finished", "failed"):
            if key in (arcade.key.ENTER, arcade.key.RETURN):
                self.sub_view = None

    def _repair_on_text(self, text):
        state = self.repair_state
        if state['state'] == "guessing":
            if len(text) == 1 and text.isalpha():
                state['input_letter'] = text.upper()

    def _repair_commit_letter_guess(self):
        state = self.repair_state
        letter = state['input_letter']
        state['input_letter'] = ""
        if not letter:
            return
        if letter in state['guessed_letters']:
            self._repair_log("Veuillez entrer une lettre differente !")
            return
        state['guessed_letters'].add(letter)
        if letter in state['target_phrase']:
            state['attemps'] += 1
            self._repair_log(f"Lettre correcte : {letter} (restants {15 - state['attemps']})")
        else:
            state['attemps'] += 1
            self._repair_log(f"Lettre incorrecte : {letter} (restants {15 - state['attemps']})")
        if self._repair_all_revealed():
            self._repair_log("Toutes les lettres sont revelees. Reparation reussie !")
            state['state'] = "finished"
            state['message'] = "Connexion reussie. Appuyez sur Entree pour revenir au terminal."
            return
        if state['attemps'] >= 15:
            self._repair_log("Échec : trop de tentatives.")
            state['state'] = "failed"
            state['message'] = "Échec de la connexion. Appuyez sur Entree pour quitter."
            return

    def _get_masked_phrase(self):
        state = self.repair_state
        return ' '.join([c if c == ' ' or c in state['guessed_letters'] else '_' for c in state['target_phrase']])

    def _repair_all_revealed(self):
        state = self.repair_state
        return all((c == ' ') or (c in state['guessed_letters']) for c in state['target_phrase'])

    def _repair_log(self, text):
        state = self.repair_state
        state['terminal_lines'].append(text)
        if len(state['terminal_lines']) > 80:
            state['terminal_lines'] = state['terminal_lines'][-80:]

    def _reset_repair(self):
        state = self.repair_state
        state['guessed_letters'] = set()
        state['attemps'] = 0
        state['input_letter'] = ''
        state['state'] = 'guessing'
        state['message'] = ''
        state['terminal_lines'] = [
            "Connexion distante chiffree. Vous devez dechiffrer le mot de passe. Entrez une lettre et appuyez sur Entree pour commencer a deviner. une lettre du mot de passe, vous avez 15 tentatives pour deviner tous les lettres."
        ]
        
