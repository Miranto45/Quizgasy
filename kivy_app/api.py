# -*- coding: utf-8 -*-
"""Client API : mitantatra amin'ny backend FastAPI (tsy mila lib hafa, urllib fotsiny)."""

import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


SERVEUR = "http://192.168.239.87:8000"

def api(chemin: str, methode: str = "GET", data=None):
    """Mandefa fangatahana amin'ilay API. Mamerina dict/liste."""
    url = SERVEUR.rstrip("/") + chemin
    corps = json.dumps(data).encode("utf-8") if data is not None else None
    req = Request(url, data=corps, method=methode)
    req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req, timeout=10) as reponse:
            return json.loads(reponse.read().decode("utf-8"))
    except HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        raise RuntimeError("Nisy olana ny API (%s): %s" % (e.code, detail))
    except Exception as e:
        raise RuntimeError("Tsy tafakatra amin'ny serveur. Ataovy aloha : uvicorn main:app --port 8000\n(%s)" % e)
