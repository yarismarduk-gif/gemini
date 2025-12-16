from fastapi import FastAPI, HTTPException
import logging
import os
import requests

# Configuro logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inizializzo FastAPI
app = FastAPI()

# Inizializzo Tavily client (se hai la libreria e la chiave API)
try:
    from tavily import TavilyClient
    api_key = os.getenv("TAVILY_API_KEY")
    tavily_client = TavilyClient(api_key=api_key) if api_key else None
except Exception as e:
    logger.error(f"Errore nell'inizializzazione di TavilyClient: {e}")
    tavily_client = None


@app.get("/search")
def search_web(query: str):
    if not tavily_client:
        raise HTTPException(status_code=500, detail="Servizio di ricerca non configurato.")
    try:
        response = tavily_client.search(query=query, search_depth="advanced")

        answer = response.get("answer")
        results = response.get("results", [])

        if answer:
            return {"summary": answer, "sources": results}
        elif results:
            return {
                "summary": "Nessun riassunto disponibile, ma ho trovato delle fonti.",
                "sources": results
            }
        else:
            return {"summary": "Nessun risultato trovato."}
    except Exception as e:
        logger.error(f"Errore durante la ricerca: {e}")
        raise HTTPException(status_code=500, detail=f"Errore durante la ricerca: {str(e)}")


@app.get("/weather")
def get_weather(city: str):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Chiave OpenWeather non configurata.")

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=it"
        response = requests.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Errore dal servizio meteo.")

        data = response.json()
        return {
            "city": city,
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        }
    except Exception as e:
        logger.error(f"Errore durante la richiesta meteo: {e}")
        raise HTTPException(status_code=500, detail=f"Errore durante la richiesta meteo: {str(e)}")