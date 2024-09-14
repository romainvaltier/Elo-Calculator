from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from database import Database
from pilot import Pilot

# Définir le modèle Pydantic pour le pilote
class PilotModel(BaseModel):
    id: int
    licenseNumber: str
    firstName: str
    lastName: str
    pseudo: str
    elo: int

    class Config:
        from_attributes = True  # Utilisé pour les modèles Pydantic V2

app = FastAPI()

def get_db():
    db = Database()
    db.create("database.db")  # Remplacez par le chemin correct vers votre base de données
    try:
        yield db
    finally:
        db.close()

@app.get("/rankings", response_model=List[PilotModel])
def get_rankings(minimum_races: int = 3, db: Database = Depends(get_db)):
    """
    Endpoint pour récupérer le classement des pilotes.
    """
    try:
        pilots = db.get_all_pilots_by_rank(minimum_races)
        if not pilots:
            raise HTTPException(status_code=404, detail="No pilots found with the specified number of races")
        # Arrondir les valeurs Elo à l'entier le plus proche
        for pilot in pilots:
            pilot.elo = round(pilot.elo)
        return pilots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pilots", response_model=List[PilotModel])
def list_all_pilots(db: Database = Depends(get_db)):
    """
    Endpoint pour lister tous les pilotes.
    """
    try:
        pilots = db.get_all_pilots_by_rank(0)  # Obtenir tous les pilotes sans restriction de courses
        if not pilots:
            raise HTTPException(status_code=404, detail="No pilots found")
        # Arrondir les valeurs Elo à l'entier le plus proche
        for pilot in pilots:
            pilot.elo = round(pilot.elo)
        return pilots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fermer la connexion à la base de données lors de la fermeture de l'application
@app.on_event("shutdown")
def shutdown_event():
    db.close()
