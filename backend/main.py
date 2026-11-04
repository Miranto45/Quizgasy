# -*- coding: utf-8 -*-
"""
FANONTANIANA - Bataille de Quiz Malagasy
Backend FastAPI + SQLite (base de donnees simple, sans installation)

Lancer :  uvicorn main:app --reload --port 8000
Docs   :  http://127.0.0.1:8000/docs
"""

import json
import sqlite3
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_PATH = "fanontaniana.db"

app = FastAPI(
    title="Fanontaniana API",
    description="Bataille de Quiz malagasy - Backend FastAPI (projet L3 Python)",
    version="1.0.0",
)

# ------------------------------------------------------------------
# Base de donnees
# ------------------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS quiz (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            description TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL REFERENCES quiz(id) ON DELETE CASCADE,
            question TEXT NOT NULL,
            choix TEXT NOT NULL,          -- JSON : liste de 4 choix
            bonne_reponse INTEGER NOT NULL, -- index du bon choix (0..3)
            points INTEGER NOT NULL DEFAULT 10
        );
        CREATE TABLE IF NOT EXISTS joueurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pseudo TEXT NOT NULL UNIQUE,
            points INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS parties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            joueur_id INTEGER NOT NULL REFERENCES joueurs(id) ON DELETE CASCADE,
            quiz_id INTEGER NOT NULL REFERENCES quiz(id) ON DELETE CASCADE,
            score INTEGER NOT NULL,
            date TEXT NOT NULL
        );
        """
    )
    # Quiz sy fanontaniana fanombohana (momba an'i Madagasikara, amin'ny teny malagasy)
    if conn.execute("SELECT COUNT(*) AS n FROM quiz").fetchone()["n"] == 0:
        quiz_demo = [
            ("Jeografia sy Voakajy", "Tany, ranomasina, tendrombohitra sy zavaboary malagasy"),
            ("Tantara sy Mpanjaka", "Tantaran'i Madagasikara, mpanjaka sy fahaleovantena"),
            ("Kolontsaina sy Fomban-drazana", "Fanao, sakafo, mozika sy fomban-drazana malagasy"),
            ("Vokatra sy Toekarena", "Vokatra malaza sy toekarenan'i Madagasikara"),
            ("Biby sy Zavaboary", "Biby tsy fahita afa-tsy eto Madagasikara sy ny zavaboary"),
        ]
        for titre, desc in quiz_demo:
            conn.execute("INSERT INTO quiz (titre, description) VALUES (?, ?)", (titre, desc))
        questions_demo = [
            # Quiz 1 : Jeografia sy Voakajy
            (1, "Inona no renivohitr'i Madagasikara?", ["Toamasina", "Antananarivo", "Fianarantsoa", "Mahajanga"], 1),
            (1, "Inona no zavamaniry manana ravina toy ny sof'ny olona, mariky Madagasikara?", ["Ravinalo (arizoana)", "Baobab", "Vary", "Lavanila"], 0),
            (1, "Inona no ranomasina manelanelana an'i Madagasikara sy Afrika?", ["Ranomasimbe Indianina", "Ranomasimbe Atlantika", "Lakandranon'i Mozambika", "Farihy Alaotra"], 2),
            (1, "Firy ny isan'ny faritra (regions) misy eto Madagasikara?", ["6", "11", "22", "23"], 3),
            (1, "Inona no vola ampiasaina eto Madagasikara?", ["Farantsa", "Ariary", "Dolare", "Naod"], 1),
            (1, "Inona no parc national malaza manana ny 'Tsingy'?", ["Isalo", "Andasibe", "Bemaraha", "Ranomafana"], 2),
            (1, "Inona no tendrombohitra avo indrindra eto Madagasikara?", ["Tsaratanana (Maromokotro)", "Andringitra (Boby)", "Ankaratra", "Isalo"], 0),
            (1, "Inona no ony lava indrindra eto Madagasikara?", ["Betsiboka", "Mangoro", "Onilahy", "Ikopa"], 1),
            (1, "Aiza no misy ny Farihy Alaotra, farihy lehibe indrindra eto Madagasikara?", ["Antsirabe", "Ambatondrazaka", "Toliara", "Sambava"], 1),
            (1, "Inona no tanàna lehibe faharoa eto Madagasikara, malaza amin'ny seranan-tsampo?", ["Toamasina", "Fianarantsoa", "Mahajanga", "Antsirabe"], 0),
            (1, "Inona no renivohitr'ny faritra Vakinankaratra?", ["Antsirabe", "Ambatolampy", "Moramanga", "Behenjy"], 0),
            (1, "Inona no ala manokana misy tsilo, any amin'ny tapany atsimo-andrefan'i Madagasikara?", ["Ala tsilo (Didiereaceae)", "Ala mando", "Mangrove", "Ala pine"], 0),
            # Quiz 2 : Tantara sy Mpanjaka
            (2, "Iza no mpanjaka nanambany ny Fanjakan'Imerina ka nampiray azy?", ["Andrianampoinimerina", "Ratsimilaho", "Andriamanelo", "Ralambo"], 0),
            (2, "Iza no nanorina ny Fanjakan'Imerina?", ["Andriamanelo", "Radama I", "Ratsimilaho", "Raombana"], 0),
            (2, "Iza no mpanjaka nanitatra ny fanjakana ka noraisin'i Angletera ho mpanjakan'i Madagasikara?", ["Andrianampoinimerina", "Radama I", "Ralambo", "Andriamanelo"], 1),
            (2, "Iza no mpanjakavavy nanjaka nanomboka tamin'ny 1828, nanamafy ny fanjanahana ny tany?", ["Ranavalona I", "Rasoherina", "Ranavalona II", "Ranavalona III"], 0),
            (2, "Taona firy i Madagasikara nahazo ny fahaleovantena?", ["1947", "1960", "1972", "1975"], 1),
            (2, "Inona no datin'ny fahaleovantena isantarana isan-taona?", ["26 Jona", "29 Martsa", "14 Jolay", "1 Janoary"], 0),
            (2, "Iza no filoham-pirenena voalohany tamin'ny Repoblika Malagasy?", ["Philibert Tsiranana", "Didier Ratsiraka", "Albert Zafy", "Marc Ravalomanana"], 0),
            (2, "Inona no nitranga tamin'ny volana martsa 1947 eto Madagasikara?", ["Fikomana (insolasyon) mahery vaika", "Fahaleovantena", "Lalàmpanorenana voalohany", "Famadihana"], 0),
            (2, "Inona no taona nanombohan'ny fanjanahantany frantsay an'i Madagasikara?", ["1896", "1960", "1885", "1910"], 0),
            (2, "Iza no mpanoratra malagasy nalaza tamin'ny taonjato faha-19, nanoratra diary sy tantara?", ["Raombana", "Jean-Joseph Rabearivelo", "Dox", "Rainandriamampandry"], 0),
            # Quiz 3 : Kolontsaina sy Fomban-drazana
            (3, "Inona ny anaran'ny lamba vita amin'ny landibe, omena ho mari-pifanajana amin'ny fomban-drazana?", ["Lamba baony", "Lamba-panjana", "Lamba hoany", "Sany"], 1),
            (3, "Inona no atao hoe 'Famadihana'?", ["Fihavanana", "Famerenana ny razana", "Fivoriana", "Fanomezana"], 1),
            (3, "Inona no sakafo malagasy malaza, rongony ahitra sy hena?", ["Ravitoto", "Romazava", "Kitoza", "Vary amin'anana"], 1),
            (3, "Inona ny anaran'ny fomban-drazana mifototra amin'ny fitiavana sy fifanajana?", ["Famadihana", "Fihavanana", "Kabary", "Joro"], 1),
            (3, "Inona no teny ofisialy roa eto Madagasikara?", ["Malagasy sy Frantsay", "Malagasy sy Anglisy", "Frantsay sy Anglisy", "Malagasy sy Deutsch"], 0),
            (3, "Inona no hiram-pirenena malagasy?", ["Ry Tanindrazanay Malala Ô", "Mila ho anao", "Hira fahafaham-tena", "Zanahary"], 0),
            (3, "Inona no atao hoe 'Kabary'?", ["Fitenenana amin'ny fomban-drazana", "Fihazana", "Sakafo", "Lamba"], 0),
            (3, "Inona no zavamaneno malagasy vita amin'ny bozaka?", ["Valiha", "Kabosy", "Lokanga", "Korintsana"], 0),
            (3, "Inona no anaran'ny tantara foronina ampitaina amin'ny alina, momba ny biby?", ["Angano", "Fihavanana", "Kabary", "Vakodrazana"], 0),
            (3, "Inona no sakafo malagasy vita amin'ny ravina manioka?", ["Ravitoto", "Romazava", "Vary amin'anana", "Kitoza"], 0),
            (3, "Inona no atao hoe 'Vary amin'anana'?", ["Sakafo malagasy amin'ny maraina", "Zava-maneno", "Lamba", "Fomban-drazana"], 0),
            # Quiz 4 : Vokatra sy Toekarena
            (4, "Inona no vokatra malaza indrindra avy amin'ny faritra SAVA?", ["Lavanila", "Vary", "Dite", "Kafe"], 0),
            (4, "Inona no tanàna malaza amin'ny fanondranana lavanila?", ["Sambava sy Antalaha", "Toliara", "Morondava", "Fianarantsoa"], 0),
            (4, "Inona no vatosoa (vato sarobidy) malaza avy any Ilakaka, any atsimo?", ["Safira", "Varahina", "Volamena", "Lalanitra"], 0),
            (4, "Inona no tanàna malaza amin'ny fanaovana zavakanto amin'ny hazo?", ["Ambositra", "Ambanja", "Ambatondrazaka", "Ambilobe"], 0),
            (4, "Inona no sakafo fototra amin'ny sakafo malagasy isan'andro?", ["Vary", "Tsaramaso", "Kisoa", "Voasary"], 0),
            (4, "Inona no toerana malaza any Morondava, misy baobab mifanindry ao an-dalana?", ["Lalan'ny Renala (Allée des baobabs)", "Tsingy de Bemaraha", "Farihy Itasy", "Ilakaka"], 0),
            (4, "Inona no voankazo maitso, be ranony, avy any amin'ny faritra atsinanana?", ["Litchy", "Voasary", "Paoma", "Mango"], 0),
            # Quiz 5 : Biby sy Zavaboary
            (5, "Inona no biby mpanjono (carnivore) lehibe indrindra eto Madagasikara?", ["Fosa", "Lambo", "Totoroka", "Amboa"], 0),
            (5, "Firy eo ho eo ny karazana babakoto (lemur) hita eto Madagasikara?", ["Efa ho 100", "10", "5", "1000"], 0),
            (5, "Inona no vorona tsy manidina goavana, efa lany tamingana, hita teto Madagasikara?", ["Vorombe (Aepyornis)", "Akoho", "Gisa", "Fody"], 0),
            (5, "Inona no biby tsy misy mihitsy eto Madagasikara?", ["Liona", "Babakoto", "Fosa", "Tanalahy"], 0),
            (5, "Inona no biby manana rantsantsa maherijery (maso), tsy fahita afa-tsy eto Madagasikara sy amin'ny tany vitsivitsy?", ["Tanalahy", "Amboa", "Omby", "Akoho"], 0),
            (5, "Aiza no misy ny Parc National Andasibe, malaza amin'ny Indry?", ["Any atsinanana (Moramanga)", "Any atsimo", "Any andrefana", "Any avaratra"], 0),
            (5, "Inona no biby an-dranomasina goavana mahazatra hitsidika any amin'ny nosy Sainte-Marie?", ["Zazavavindrano (baleine)", "Trondro kely", "Akora", "Foza"], 0),
        ]
        for quiz_id, q, choix, bonne in questions_demo:
            conn.execute(
                "INSERT INTO questions (quiz_id, question, choix, bonne_reponse) VALUES (?, ?, ?, ?)",
                (quiz_id, q, json.dumps(choix), bonne),
            )
    conn.commit()
    conn.close()


# ------------------------------------------------------------------
# Modeles (validation des donnees)
# ------------------------------------------------------------------

class QuizIn(BaseModel):
    titre: str
    description: str = ""


class QuestionIn(BaseModel):
    question: str
    choix: List[str]
    bonne_reponse: int
    points: int = 10


class JoueurIn(BaseModel):
    pseudo: str


class Reponse(BaseModel):
    question_id: int
    choix: int  # index choisi par le joueur


class PartieIn(BaseModel):
    joueur_id: int
    quiz_id: int
    reponses: List[Reponse]


# ------------------------------------------------------------------
# Endpoints : Quiz
# ------------------------------------------------------------------

@app.get("/", tags=["General"])
def accueil():
    return {"message": "Tongasoa eto amin'ny Fanontaniana API! Jereo /docs raha hijery ny API."}


@app.get("/quiz", tags=["Quiz"])
def liste_quiz():
    conn = get_db()
    quiz = [dict(r) for r in conn.execute("SELECT * FROM quiz ORDER BY id")]
    for q in quiz:
        q["nb_questions"] = conn.execute(
            "SELECT COUNT(*) AS n FROM questions WHERE quiz_id = ?", (q["id"],)
        ).fetchone()["n"]
    conn.close()
    return quiz


@app.post("/quiz", tags=["Quiz"], status_code=201)
def creer_quiz(data: QuizIn):
    conn = get_db()
    cur = conn.execute("INSERT INTO quiz (titre, description) VALUES (?, ?)", (data.titre, data.description))
    conn.commit()
    quiz_id = cur.lastrowid
    conn.close()
    return {"id": quiz_id, "titre": data.titre, "description": data.description}


@app.delete("/quiz/{quiz_id}", tags=["Quiz"])
def supprimer_quiz(quiz_id: int):
    conn = get_db()
    if not conn.execute("SELECT id FROM quiz WHERE id = ?", (quiz_id,)).fetchone():
        conn.close()
        raise HTTPException(404, "Tsy hita ilay quiz")
    conn.execute("DELETE FROM questions WHERE quiz_id = ?", (quiz_id,))
    conn.execute("DELETE FROM quiz WHERE id = ?", (quiz_id,))
    conn.commit()
    conn.close()
    return {"message": "Voafafa ny quiz"}


@app.get("/quiz/{quiz_id}/questions", tags=["Questions"])
def questions_du_quiz(quiz_id: int, melanger: bool = True):
    conn = get_db()
    if not conn.execute("SELECT id FROM quiz WHERE id = ?", (quiz_id,)).fetchone():
        conn.close()
        raise HTTPException(404, "Tsy hita ilay quiz")
    rows = conn.execute("SELECT id, question, choix, points FROM questions WHERE quiz_id = ?", (quiz_id,)).fetchall()
    conn.close()
    questions = []
    for r in rows:
        questions.append({
            "id": r["id"],
            "question": r["question"],
            "choix": json.loads(r["choix"]),
            "points": r["points"],
        })
    if melanger:
        import random
        random.shuffle(questions)
    return questions


@app.post("/quiz/{quiz_id}/questions", tags=["Questions"], status_code=201)
def ajouter_question(quiz_id: int, data: QuestionIn):
    if len(data.choix) < 2:
        raise HTTPException(400, "Tsy maintsy misy fanontaniana 2 farafahakeliny (choix)")
    if not (0 <= data.bonne_reponse < len(data.choix)):
        raise HTTPException(400, "Tsy mety ny laharan'ny valiny marina (bonne_reponse)")
    conn = get_db()
    if not conn.execute("SELECT id FROM quiz WHERE id = ?", (quiz_id,)).fetchone():
        conn.close()
        raise HTTPException(404, "Tsy hita ilay quiz")
    cur = conn.execute(
        "INSERT INTO questions (quiz_id, question, choix, bonne_reponse, points) VALUES (?, ?, ?, ?, ?)",
        (quiz_id, data.question, json.dumps(data.choix), data.bonne_reponse, data.points),
    )
    conn.commit()
    qid = cur.lastrowid
    conn.close()
    return {"id": qid, **data.model_dump()}


@app.put("/questions/{question_id}", tags=["Questions"])
def modifier_question(question_id: int, data: QuestionIn):
    conn = get_db()
    if not conn.execute("SELECT id FROM questions WHERE id = ?", (question_id,)).fetchone():
        conn.close()
        raise HTTPException(404, "Tsy hita ny fanontaniana")
    conn.execute(
        "UPDATE questions SET question = ?, choix = ?, bonne_reponse = ?, points = ? WHERE id = ?",
        (data.question, json.dumps(data.choix), data.bonne_reponse, data.points, question_id),
    )
    conn.commit()
    conn.close()
    return {"id": question_id, **data.model_dump()}


@app.delete("/questions/{question_id}", tags=["Questions"])
def supprimer_question(question_id: int):
    conn = get_db()
    if not conn.execute("SELECT id FROM questions WHERE id = ?", (question_id,)).fetchone():
        conn.close()
        raise HTTPException(404, "Tsy hita ny fanontaniana")
    conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()
    return {"message": "Voafafa ny fanontaniana"}


# ------------------------------------------------------------------
# Endpoints : Joueurs et parties
# ------------------------------------------------------------------

@app.post("/joueurs", tags=["Joueurs"], status_code=201)
def creer_ou_recuperer_joueur(data: JoueurIn):
    conn = get_db()
    row = conn.execute("SELECT * FROM joueurs WHERE pseudo = ?", (data.pseudo,)).fetchone()
    if row:
        conn.close()
        return dict(row)
    cur = conn.execute("INSERT INTO joueurs (pseudo) VALUES (?)", (data.pseudo,))
    conn.commit()
    joueur = {"id": cur.lastrowid, "pseudo": data.pseudo, "points": 0}
    conn.close()
    return joueur


@app.get("/joueurs", tags=["Joueurs"])
def liste_joueurs():
    conn = get_db()
    joueurs = [dict(r) for r in conn.execute("SELECT * FROM joueurs ORDER BY points DESC, pseudo")]
    conn.close()
    return joueurs


@app.post("/parties", tags=["Parties"])
def jouer_partie(data: PartieIn):
    """Le joueur envoie ses reponses ; l'API corrige et calcule les points."""
    conn = get_db()
    if not conn.execute("SELECT id FROM joueurs WHERE id = ?", (data.joueur_id,)).fetchone():
        conn.close()
        raise HTTPException(404, "Tsy hita ny mpilalao")
    rows = conn.execute("SELECT id, bonne_reponse, points FROM questions WHERE quiz_id = ?", (data.quiz_id,)).fetchall()
    reponses = {r["id"]: r for r in rows}
    score, bonnes, total = 0, 0, len(data.reponses)
    for rep in data.reponses:
        q = reponses.get(rep.question_id)
        if q and rep.choix == q["bonne_reponse"]:
            score += q["points"]
            bonnes += 1
    conn.execute(
        "INSERT INTO parties (joueur_id, quiz_id, score, date) VALUES (?, ?, ?, ?)",
        (data.joueur_id, data.quiz_id, score, datetime.utcnow().isoformat()),
    )
    conn.execute("UPDATE joueurs SET points = points + ? WHERE id = ?", (score, data.joueur_id))
    conn.commit()
    joueur = conn.execute("SELECT points FROM joueurs WHERE id = ?", (data.joueur_id,)).fetchone()["points"]
    conn.close()
    return {
        "score": score,
        "bonnes_reponses": bonnes,
        "total_questions": total,
        "points_total_joueur": joueur,
    }


@app.get("/duel/{quiz_id}", tags=["Parties"])
def duel(quiz_id: int, joueur1: Optional[int] = None, joueur2: Optional[int] = None):
    """Compare la derniere partie de chaque joueur sur ce quiz : bataille !"""
    conn = get_db()
    resultats = {}
    for jid, label in [(joueur1, "joueur1"), (joueur2, "joueur2")]:
        if jid is None:
            continue
        row = conn.execute(
            "SELECT p.score, p.date, j.pseudo FROM parties p JOIN joueurs j ON j.id = p.joueur_id "
            "WHERE p.joueur_id = ? AND p.quiz_id = ? ORDER BY p.id DESC LIMIT 1",
            (jid, quiz_id),
        ).fetchone()
        resultats[label] = dict(row) if row else None
    conn.close()
    s1 = (resultats.get("joueur1") or {}).get("score")
    s2 = (resultats.get("joueur2") or {}).get("score")
    if s1 is None or s2 is None:
        gagnant = None
    elif s1 > s2:
        gagnant = resultats["joueur1"]["pseudo"]
    elif s2 > s1:
        gagnant = resultats["joueur2"]["pseudo"]
    else:
        gagnant = "Fetra (masaka)!"
    return {"resultats": resultats, "gagnant": gagnant}


@app.get("/classement", tags=["Parties"])
def classement():
    conn = get_db()
    rows = conn.execute(
        "SELECT j.pseudo, j.points, "
        "COUNT(p.id) AS nb_parties, COALESCE(MAX(p.score), 0) AS meilleur_score "
        "FROM joueurs j LEFT JOIN parties p ON p.joueur_id = j.id "
        "GROUP BY j.id ORDER BY j.points DESC LIMIT 20"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


init_db()
