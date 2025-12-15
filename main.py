import os
import requests
from fastapi import FastAPI, HTTPException
from tavily import TavilyClient

# --- Chiavi API ---
tavily_api_key = os.environ.get("TAVILY_API_KEY")
openweathermap_api_key = os.environ.get("OPENWEATHERMAP_API_KEY")

# --- Inizializzazione ---
app = FastAPI()

if tavily_api_key:
    tavily_client = TavilyClient(api_key=tavily_api_key)
else:
    print("ATTENZIONE: TAVILY_API_KEY non impostata.")
    tavily_client = None

# --- Endpoint base ---
@app.get("/")
def read_root():
    return {"message": "Ciao! La mia API è pronta a cercare e a dare il meteo."}

# --- Endpoint ricerca web ---
@app.get("/search")
def search_web(query: str):
    if not tavily_client:
        raise HTTPException(status_code=500, detail="Servizio di ricerca non configurato.")
    try:
        response = tavily_client.search(query=query, search_depth="basic")
        if response and response.get("answer"):
            return {"summary": response["answer"]}
        else:
            return {"summary": "Nessun risultato trovato."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la ricerca: {str(e)}")

# --- Endpoint meteo ---
@app.get("/meteo")
def get_weather(citta: str):
    if not openweathermap_api_key:
        raise HTTPException(status_code=500, detail="Servizio meteo non configurato.")

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': citta,
        'appid': openweathermap_api_key,
        'units': 'metric',
        'lang': 'it'
    }
    try:
        api_response = requests.get(base_url, params=params)
        api_response.raise_for_status()
        data = api_response.json()

        main_data = data.get("main", {})
        weather_data = data.get("weather", [{}])[0]
        temperatura = main_data.get("temp")
        descrizione = weather_data.get("description")

        if temperatura is not None and descrizione is not None:
            return {
                "citta": data.get("name"),
                "temperatura_celsius": temperatura,
                "descrizione": descrizione.capitalize()
            }
        else:
            raise HTTPException(status_code=500, detail="Dati meteo mancanti nella risposta dell'API esterna.")

    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Chiave API per il meteo non valida o non autorizzata.")
        elif http_err.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Città '{citta}' non trovata.")
        else:
            raise HTTPException(status_code=500, detail=f"Errore HTTP dal servizio meteo: {http_err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore generico durante la richiesta meteo: {str(e)}")

# --- Avvio locale (non richiesto da Vercel, utile per test) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)