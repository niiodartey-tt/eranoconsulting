from fastapi import FastAPI
app = FastAPI(title="Eranos Consulting API")

@app.get("/")
async def root():
    return {"msg":"Eranos Consulting API - dev"}
