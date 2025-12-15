@app.get("/search")
def search_web(query: str):
    if not tavily_client:
        raise HTTPException(status_code=500, detail="Servizio di ricerca non configurato.")
    try:
        response = tavily_client.search(query=query, search_depth="advanced")

        # Estraggo l'answer se presente
        answer = response.get("answer", None)

        # Estraggo i risultati grezzi
        results = response.get("results", [])

        if answer:
            return {"summary": answer, "sources": results}
        elif results:
            return {"summary": "Nessun riassunto disponibile, ma ho trovato delle fonti.",
                    "sources": results}
        else:
            return {"summary": "Nessun risultato trovato."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la ricerca: {str(e)}")