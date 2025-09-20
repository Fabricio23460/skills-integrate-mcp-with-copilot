"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path
from models.database import get_db, Activity, Participant, SessionLocal

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Inicializar la base de datos con actividades predeterminadas
def init_db():
    db = SessionLocal()
    # Solo inicializar si no hay actividades
    if db.query(Activity).count() == 0:
        default_activities = [
            {
                "name": "Chess Club",
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_capacity": 12,
                "category": "Academic"
            },
            {
                "name": "Programming Class",
                "description": "Learn programming fundamentals and build software projects",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                "max_capacity": 20,
                "category": "Technology"
            },
            {
                "name": "Gym Class",
                "description": "Physical education and sports activities",
                "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                "max_capacity": 30,
                "category": "Sports"
            }
        ]
        
        for activity_data in default_activities:
            activity = Activity(**activity_data)
            db.add(activity)
        
        db.commit()
    db.close()

# Inicializar la base de datos al iniciar la aplicación
init_db()

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")

@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    activities = db.query(Activity).all()
    result = {}
    for activity in activities:
        participants = [p.email for p in activity.participants]
        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_capacity,
            "participants": participants
        }
    return result

@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity"""
    # Validate activity exists
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Verificar si el estudiante ya está inscrito
    existing_participant = db.query(Participant).filter(
        Participant.activity_id == activity.id,
        Participant.email == email
    ).first()
    
    if existing_participant:
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    # Verificar si hay espacio disponible
    current_participants = db.query(Participant).filter(
        Participant.activity_id == activity.id
    ).count()
    
    if current_participants >= activity.max_capacity:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Crear nuevo participante
    new_participant = Participant(email=email, activity_id=activity.id)
    db.add(new_participant)
    db.commit()
    
    return {"message": f"Successfully signed up for {activity_name}"}

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
@app.delete("/activities/{activity_name}/signup")
def remove_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Remove a student from an activity"""
    # Validate activity exists
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Buscar y eliminar al participante
    participant = db.query(Participant).filter(
        Participant.activity_id == activity.id,
        Participant.email == email
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="Student not found in this activity")

    db.delete(participant)
    db.commit()
    
    return {"message": f"Successfully removed from {activity_name}"}
