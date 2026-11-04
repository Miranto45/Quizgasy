# -*- coding: utf-8 -*-
"""
FANONTANIANA - Bataille de Quiz Malagasy
Application Kivy (frontend) - quiz momba an'i Madagasikara, compte de points,
bataille (duel) miaraka, ary fitantanana ny quiz (fanampina, famafana).

Mila ilay backend aloha :  (backend/) uvicorn main:app --port 8000
Lancer :                   python main.py
"""

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager

from api import api

KV = """
ScreenManager:
    EcranMenu:
        name: "menu"
    EcranQuizList:
        name: "quizlist"
    EcranQuiz:
        name: "quiz"
    EcranValiny:
        name: "valiny"
    EcranBataille:
        name: "bataille"
    EcranClassement:
        name: "classement"
    EcranFitantanana:
        name: "fitantanana"

<EcranMenu>:
    BoxLayout:
        orientation: "vertical"
        padding: 30
        spacing: 15
        canvas.before:
            Color:
                rgba: 0.10, 0.25, 0.18, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "FANONTANIANA"
            font_size: "42sp"
            bold: True
            color: 1, 0.85, 0.2, 1
        Label:
            text: "Bataille de Quiz malagasy\\nMomba an'i Madagasikara"
            font_size: "18sp"
        TextInput:
            id: pseudo
            hint_text: "Ampidiro ny anaranao (pseudo)"
            multiline: False
            size_hint_y: None
            height: "48dp"
            font_size: "18sp"
        Widget:
        Button:
            text: "Milalao Quiz"
            size_hint_y: None
            height: "56dp"
            background_color: 0.15, 0.55, 0.3, 1
            on_release: root.mankany_quiz()
        Button:
            text: "Bataille (duel) miaraka"
            size_hint_y: None
            height: "56dp"
            background_color: 0.7, 0.35, 0.1, 1
            on_release: app.ouvrir_bataille()
        BoxLayout:
            size_hint_y: None
            height: "56dp"
            spacing: 10
            Button:
                text: "Classement"
                on_release: app.ecran_classement()
            Button:
                text: "Fitantanana quiz"
                on_release: app.refresh_fitantanana()

<EcranQuizList>:
    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 10
        Label:
            text: "Fidio ny quiz"
            font_size: "26sp"
            bold: True
            size_hint_y: None
            height: "40dp"
        ScrollView:
            GridLayout:
                id: liste
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                row_default_height: "56dp"
                row_force_default: True
                spacing: 8
        Button:
            text: "< Averina"
            size_hint_y: None
            height: "48dp"
            on_release: app.root.current = "menu"

<EcranQuiz>:
    BoxLayout:
        orientation: "vertical"
        padding: 25
        spacing: 12
        Label:
            id: infos
            text: ""
            font_size: "15sp"
            size_hint_y: None
            height: "30dp"
            color: 0.7, 0.9, 0.7, 1
        Label:
            id: fanontaniana
            text: ""
            font_size: "22sp"
            bold: True
        GridLayout:
            id: choix
            cols: 2
            spacing: 10
            size_hint_y: None
            height: "220dp"

<EcranValiny>:
    BoxLayout:
        orientation: "vertical"
        padding: 30
        spacing: 15
        Label:
            id: isa
            text: ""
            font_size: "34sp"
            bold: True
            color: 1, 0.85, 0.2, 1
        Label:
            id: details
            text: ""
            font_size: "18sp"
        Widget:
        Button:
            id: btn_manaraka
            text: "Hita, mandeha hafa"
            size_hint_y: None
            height: "52dp"
            on_release: app.valiny_manaraka()

<EcranBataille>:
    BoxLayout:
        orientation: "vertical"
        padding: 25
        spacing: 12
        Label:
            text: "BATAILLE"
            font_size: "32sp"
            bold: True
            color: 1, 0.6, 0.2, 1
            size_hint_y: None
            height: "44dp"
        TextInput:
            id: pseudo1
            hint_text: "Anaran'ny mpilalao 1"
            multiline: False
            size_hint_y: None
            height: "46dp"
        TextInput:
            id: pseudo2
            hint_text: "Anaran'ny mpilalao 2"
            multiline: False
            size_hint_y: None
            height: "46dp"
        ScrollView:
            GridLayout:
                id: liste_quiz
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                row_default_height: "52dp"
                row_force_default: True
                spacing: 8
        Label:
            id: vokatra
            text: ""
            font_size: "17sp"
        Button:
            text: "< Averina"
            size_hint_y: None
            height: "48dp"
            on_release: app.root.current = "menu"

<EcranClassement>:
    BoxLayout:
        orientation: "vertical"
        padding: 25
        spacing: 10
        Label:
            text: "CLASSEMENT (isa)"
            font_size: "28sp"
            bold: True
            color: 1, 0.85, 0.2, 1
            size_hint_y: None
            height: "44dp"
        Label:
            id: liste
            text: ""
            font_size: "17sp"
        Button:
            text: "< Averina"
            size_hint_y: None
            height: "48dp"
            on_release: app.root.current = "menu"

<EcranFitantanana>:
    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 8
        Label:
            text: "FITANTANANA NY QUIZ"
            font_size: "24sp"
            bold: True
            size_hint_y: None
            height: "38dp"
        TextInput:
            id: titre_quiz
            hint_text: "Lohateny quiz vaovao"
            multiline: False
            size_hint_y: None
            height: "44dp"
        BoxLayout:
            size_hint_y: None
            height: "46dp"
            spacing: 8
            Button:
                text: "Quiz vaovao +"
                background_color: 0.15, 0.55, 0.3, 1
                on_release: root.quiz_vaovao()
            Button:
                text: "Fafao quiz nofidina"
                background_color: 0.7, 0.2, 0.15, 1
                on_release: root.fafao_quiz()
        ScrollView:
            size_hint_y: 1.5
            GridLayout:
                id: liste_quiz
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                row_default_height: "48dp"
                row_force_default: True
                spacing: 6
        Label:
            text: "Fanontaniana vaovao (ho an'ny quiz nofidina)"
            bold: True
            size_hint_y: None
            height: "26dp"
        TextInput:
            id: q_texte
            hint_text: "Ny fanontaniana"
            multiline: False
            size_hint_y: None
            height: "42dp"
        TextInput:
            id: q_choix
            hint_text: "Choix : A; B; C; D  (asaroy ; )"
            multiline: False
            size_hint_y: None
            height: "42dp"
        BoxLayout:
            size_hint_y: None
            height: "44dp"
            spacing: 8
            TextInput:
                id: q_marina
                hint_text: "Laharana valiny marina (0-3)"
                multiline: False
            Button:
                text: "Ampio +"
                size_hint_x: 0.4
                background_color: 0.15, 0.55, 0.3, 1
                on_release: root.ampio_fanontaniana()
        Button:
            text: "< Averina"
            size_hint_y: None
            height: "46dp"
            on_release: app.root.current = "menu"
"""


class EcranMenu(Screen):
    def mankany_quiz(self):
        pseudo = self.ids.pseudo.text.strip()
        if not pseudo:
            self.ids.pseudo.hint_text = "Tsy maintsy ampidirina ny anarana!"
            return
        app = App.get_running_app()
        try:
            app.joueur = api("/joueurs", "POST", {"pseudo": pseudo})
        except RuntimeError as e:
            self.ids.pseudo.text = str(e)
            return
        app.mode_bataille = False
        app.ecran_quiz_list()


class EcranQuizList(Screen):
    pass


class EcranQuiz(Screen):
    pass


class EcranValiny(Screen):
    pass


class EcranBataille(Screen):
    pass


class EcranClassement(Screen):
    pass


class EcranFitantanana(Screen):
    def quiz_vaovao(self):
        titre = self.ids.titre_quiz.text.strip()
        if not titre:
            return
        try:
            api("/quiz", "POST", {"titre": titre, "description": ""})
            self.ids.titre_quiz.text = ""
            App.get_running_app().refresh_fitantanana()
        except RuntimeError as e:
            self.ids.titre_quiz.text = str(e)

    def fafao_quiz(self):
        app = App.get_running_app()
        if app.quiz_nofidina:
            api("/quiz/%d" % app.quiz_nofidina, "DELETE")
            app.quiz_nofidina = 0
            app.refresh_fitantanana()

    def ampio_fanontaniana(self):
        app = App.get_running_app()
        if not app.quiz_nofidina:
            return
        texte = self.ids.q_texte.text.strip()
        choix = [c.strip() for c in self.ids.q_choix.text.split(";") if c.strip()]
        try:
            marina = int(self.ids.q_marina.text.strip())
        except ValueError:
            self.ids.q_marina.text = "0-3!"
            return
        if not texte or len(choix) < 2 or not (0 <= marina < len(choix)):
            return
        api("/quiz/%d/questions" % app.quiz_nofidina, "POST",
            {"question": texte, "choix": choix, "bonne_reponse": marina, "points": 10})
        self.ids.q_texte.text = ""
        self.ids.q_choix.text = ""
        self.ids.q_marina.text = ""
        app.refresh_fitantanana()


class FanontanianaApp(App):
    title = "Fanontaniana - Bataille de Quiz"
    joueur = None
    quiz_nofidina = NumericProperty(0)      # quiz nofidina ao amin'ny fitantanana
    quiz_id_actif = NumericProperty(0)      # quiz milalaoka izao
    questions_actuelles = ListProperty([])
    index_question = NumericProperty(0)
    reponses_envoyees = ListProperty([])
    mode_bataille = False
    tour_bataille = ""

    def build(self):
        return Builder.load_string(KV)

    # ---------------- Quiz normale ----------------

    def ecran_quiz_list(self):
        grille = self.root.get_screen("quizlist").ids.liste
        grille.clear_widgets()
        for q in api("/quiz"):
            btn = Button(text="%s  (%d fanontaniana)" % (q["titre"], q["nb_questions"]))
            btn.quiz_id = q["id"]
            btn.bind(on_release=lambda b: self.din_quiz(b.quiz_id))
            grille.add_widget(btn)
        self.root.current = "quizlist"

    def din_quiz(self, quiz_id):
        self.quiz_id_actif = quiz_id
        self.questions_actuelles = api("/quiz/%d/questions" % quiz_id)
        self.index_question = 0
        self.reponses_envoyees = []
        self.alefa_fanontaniana()

    def alefa_fanontaniana(self):
        if self.index_question >= len(self.questions_actuelles):
            self.alefa_valiny()
            return
        q = self.questions_actuelles[self.index_question]
        ecran = self.root.get_screen("quiz")
        ecran.ids.infos.text = "Quiz #%d - Fanontaniana %d/%d" % (
            self.quiz_id_actif, self.index_question + 1, len(self.questions_actuelles))
        ecran.ids.fanontaniana.text = q["question"]
        grille = ecran.ids.choix
        grille.clear_widgets()
        for i, choix in enumerate(q["choix"]):
            btn = Button(text=choix)
            btn.bind(on_release=lambda b, i=i: self.valiny_fidina(i))
            grille.add_widget(btn)
        self.root.current = "quiz"

    def valiny_fidina(self, index_choisi):
        q = self.questions_actuelles[self.index_question]
        self.reponses_envoyees.append({"question_id": q["id"], "choix": index_choisi})
        self.index_question += 1
        self.alefa_fanontaniana()

    def alefa_valiny(self):
        """Mandefa ny valiny amin'ilay API : izy no manisa ny isa."""
        ecran = self.root.get_screen("valiny")
        try:
            self.vokatra_partie = api("/parties", "POST", {
                "joueur_id": self.joueur["id"],
                "quiz_id": self.quiz_id_actif,
                "reponses": self.reponses_envoyees,
            })
        except RuntimeError as e:
            ecran.ids.isa.text = "Nisy olana"
            ecran.ids.details.text = str(e)
            self.root.current = "valiny"
            return
        v = self.vokatra_partie
        if self.mode_bataille:
            ecran.ids.isa.text = "%s: %d isa" % (self.joueur["pseudo"], v["score"])
            ecran.ids.details.text = "Marina: %d / %d\n\nAndraso kely..." % (
                v["bonnes_reponses"], v["total_questions"])
            Clock.schedule_once(lambda dt: self._bataille_manaraka(), 2.5)
        else:
            ecran.ids.isa.text = "ISA: %d" % v["score"]
            ecran.ids.details.text = "Marina: %d / %d\nIsao manontolo: %d" % (
                v["bonnes_reponses"], v["total_questions"], v["points_total_joueur"])
        self.root.current = "valiny"

    def valiny_manaraka(self):
        """Bouton 'Hita' amin'ny ecran valiny."""
        if self.mode_bataille:
            self._bataille_manaraka()
        else:
            self.root.current = "menu"

    # ---------------- Bataille (duel) ----------------

    def ouvrir_bataille(self):
        ecran = self.root.get_screen("bataille")
        grille = ecran.ids.liste_quiz
        grille.clear_widgets()
        ecran.ids.vokatra.text = ""
        for q in api("/quiz"):
            btn = Button(text=q["titre"])
            btn.quiz_id = q["id"]
            btn.bind(on_release=self.fidio_quiz_bataille)
            grille.add_widget(btn)
        self.root.current = "bataille"

    def fidio_quiz_bataille(self, bouton):
        ecran = self.root.get_screen("bataille")
        p1 = ecran.ids.pseudo1.text.strip()
        p2 = ecran.ids.pseudo2.text.strip()
        if not p1 or not p2:
            ecran.ids.vokatra.text = "Ampidiro ny anaran'ny mpilalao roa!"
            return
        try:
            self.joueur1 = api("/joueurs", "POST", {"pseudo": p1})
            self.joueur2 = api("/joueurs", "POST", {"pseudo": p2})
        except RuntimeError as e:
            ecran.ids.vokatra.text = str(e)
            return
        self.mode_bataille = True
        self.tour_bataille = "joueur1"
        self.joueur = self.joueur1
        self.din_quiz(bouton.quiz_id)

    def _bataille_manaraka(self):
        if self.tour_bataille == "joueur1":
            self.tour_bataille = "joueur2"
            self.joueur = self.joueur2
            self.din_quiz(self.quiz_id_actif)  # ny mpilalao faharoa koa milalao
            return
        # Vita ny roa : jerena ny fandresena ao amin'ilay API
        duel = api("/duel/%d?joueur1=%d&joueur2=%d" % (
            self.quiz_id_actif, self.joueur1["id"], self.joueur2["id"]))
        r1 = (duel["resultats"].get("joueur1") or {}).get("score", 0)
        r2 = (duel["resultats"].get("joueur2") or {}).get("score", 0)
        ecran = self.root.get_screen("bataille")
        ecran.ids.vokatra.text = (
            "%s: %d isa  |  %s: %d isa\n>> %s <<" % (
                self.joueur1["pseudo"], r1, self.joueur2["pseudo"], r2, duel["gagnant"]))
        self.mode_bataille = False
        self.tour_bataille = ""
        self.root.current = "bataille"

    # ---------------- Classement sy fitantanana ----------------

    def ecran_classement(self):
        rows = api("/classement")
        texte = "\n".join(
            "%d. %s - %d isa (%d partie, tsara indrindra %d)" % (
                i + 1, r["pseudo"], r["points"], r["nb_parties"], r["meilleur_score"])
            for i, r in enumerate(rows)) or "Mbola tsy misy mpilalao."
        self.root.get_screen("classement").ids.liste.text = texte
        self.root.current = "classement"

    def refresh_fitantanana(self):
        ecran = self.root.get_screen("fitantanana")
        grille = ecran.ids.liste_quiz
        grille.clear_widgets()
        for q in api("/quiz"):
            label = "> %s" % q["titre"] if q["id"] == self.quiz_nofidina else q["titre"]
            btn = Button(text=label)
            btn.quiz_id = q["id"]
            btn.bind(on_release=self.fidio_quiz_fitantanana)
            grille.add_widget(btn)
        self.root.current = "fitantanana"

    def fidio_quiz_fitantanana(self, bouton):
        self.quiz_nofidina = bouton.quiz_id
        self.refresh_fitantanana()


if __name__ == "__main__":
    FanontanianaApp().run()
