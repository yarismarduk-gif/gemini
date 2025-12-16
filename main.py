from fastapi import FastAPI, HTTPException
import logging

# Configuro logging per debug su Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inizializzo FastAPI
app = FastAPI()

# Assumo che tavily_client venga importato o inizializzato altrove
try:
    from tavily import TavilyClient
    import os
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

        # Estraggo l'answer se presente
        answer = response.get("answer")

        # Estraggo i risultati grezzi
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