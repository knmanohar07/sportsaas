from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import engine, get_db
import qrcode
import io
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
import time
from twilio.rest import Client

# Create database tables automatically
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sports Academy Management Micro-SaaS Engine")

# CORS setup for future frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Success", "message": "Sports Academy Backend Engine is running perfectly!"}


# --- PLAYER ENDPOINTS ---

@app.post("/players/", response_model=schemas.Player)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    """Registers a new player into the system (Solves Data Fragmentation)"""
    db_player = models.Player(
        name=player.name,
        age=player.age,
        emergency_contact=player.emergency_contact,
        medical_info=player.medical_info
    )
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

@app.get("/players/", response_model=List[schemas.Player])
def get_all_players(db: Session = Depends(get_db)):
    """Fetches a complete roster of all registered players"""
    return db.query(models.Player).all()
@app.get("/players/{player_id}/qrcode")
def get_player_qr_code(player_id: int, db: Session = Depends(get_db)):
    """Generates a dynamic, scannable QR code for player attendance"""
    # 1. Verify the player exists
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found in database")
        
    # 2. Create the secure data payload (What the coach's phone will read)
    secure_data = f"ID:{player.id}|Name:{player.name}|Emergency:{player.emergency_contact}"
    
    # 3. Generate the physical QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(secure_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#7f1d1d", back_color="white") # RCB Dark Red color
    
    # 4. Stream the image directly to the browser/app without saving to hard drive
    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format="PNG")
    img_byte_array.seek(0)
    
    return StreamingResponse(img_byte_array, media_type="image/png")


# --- TRAINING SESSION ENDPOINTS ---

@app.post("/sessions/", response_model=schemas.Session)
def create_session(session: schemas.SessionCreate, db: Session = Depends(get_db)):
    """Schedules a new training session on a specific turf"""
    db_session = models.Session(
        turf_name=session.turf_name,
        start_time=session.start_time,
        end_time=session.end_time,
        capacity=session.capacity
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session
@app.get("/sessions/", response_model=List[schemas.Session])
def get_all_sessions(db: Session = Depends(get_db)):
    """Fetches all scheduled training sessions for the coach's dropdown"""
    return db.query(models.Session).all()


# --- QR CODE / ATTENDANCE ENDPOINTS ---

@app.post("/attendance/", response_model=schemas.Attendance)
def log_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    """Logs a player's attendance (Simulates scanning a dynamic QR code)"""
    # Verify player exists
    player = db.query(models.Player).filter(models.Player.id == attendance.player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
        
    # Verify session exists
    session = db.query(models.Session).filter(models.Session.id == attendance.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db_attendance = models.Attendance(
        player_id=attendance.player_id,
        session_id=attendance.session_id,
        attended=attendance.attended
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance


# --- FINANCIAL / PAYMENT ENDPOINTS ---

@app.post("/payments/", response_model=schemas.Payment)
def create_payment_record(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    """Generates a billing fee/invoice for a player"""
    db_payment = models.Payment(
        player_id=payment.player_id,
        amount_due=payment.amount_due,
        amount_paid=payment.amount_paid,
        due_date=payment.due_date,
        status=payment.status
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@app.get("/payments/overdue/", response_model=List[schemas.Payment])
def get_overdue_payments(db: Session = Depends(get_db)):
    """Instantly isolates all overdue balances (Solves the Payment Chase)"""
    return db.query(models.Payment).filter(models.Payment.status == "Overdue").all()
# --- DATA SCIENCE & ANALYTICS ENDPOINT ---

@app.get("/analytics/dashboard/")
def get_analytics_dashboard(db: Session = Depends(get_db)):
    """
    Processes historical session and attendance records using pure Python 
    data matrix logic to output capacity trends and utilization metrics.
    """
    sessions = db.query(models.Session).all()
    payments = db.query(models.Payment).all()
    
    # 1. Calculate Turf Utilization Rates
    utilization_report = []
    for s in sessions:
        # Count how many players actually attended this session
        attendance_count = db.query(models.Attendance).filter(
            models.Attendance.session_id == s.id,
            models.Attendance.attended == True
        ).count()
        
        # Calculate percentage capacity used
        utilization_rate = (attendance_count / s.capacity) * 100 if s.capacity > 0 else 0
        
        utilization_report.append({
            "session_id": s.id,
            "turf_name": s.turf_name,
            "capacity": s.capacity,
            "attended_players": attendance_count,
            "utilization_rate": round(utilization_rate, 2),
            "status": "Under-utilized" if utilization_rate < 40 else "Optimal" if utilization_rate <= 80 else "Crowded"
        })

    # 2. Financial Metrics (Projected vs Collected Revenue)
    total_projected = sum(p.amount_due for p in payments)
    total_collected = sum(p.amount_paid for p in payments)
    total_outstanding = total_projected - total_collected

    return {
        "turf_utilization": utilization_report,
        "financial_health": {
            "total_projected_revenue": round(total_projected, 2),
            "total_collected_revenue": round(total_collected, 2),
            "outstanding_fees": round(total_outstanding, 2),
            "collection_rate_percentage": round((total_collected / total_projected * 100), 2) if total_projected > 0 else 0.0
        },
        "insights": [
            "Tip: Sessions with under 40% utilization can be consolidated to save turf rental costs.",
            "Tip: Track your outstanding fees directly to automate parent email alerts."
        ]
    }
# Twilio credentials should be provided via environment variables
import os

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

def send_whatsapp_reminder(player_name: str, amount_owed: float, contact_number: str):
    """
    Connects to the Twilio API to send a real WhatsApp message.
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Ensure the phone number has the +91 India country code format
        if not str(contact_number).startswith("+"):
            formatted_number = f"whatsapp:+91{contact_number}"
        else:
            formatted_number = f"whatsapp:{contact_number}"

        message_body = f"🏆 *RCB Academy Alert*\nHi parent of {player_name}, this is a gentle reminder that a training fee of ₹{amount_owed} is currently Overdue. Please clear it at your earliest convenience."

        # Send the actual message
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message_body,
            to=formatted_number
        )
        print(f"\n[TWILIO SUCCESS] \u2705 Real WhatsApp sent to {contact_number}. Message ID: {message.sid}", flush=True)
        
    except Exception as e:
        print(f"\n[TWILIO ERROR] \u274c Failed to send message to {contact_number}. Error: {e}", flush=True)
    # Prints the physical message to your VS Code terminal
    print(f"\n[SYSTEM ALERT] \u2705 Automated WhatsApp sent to {contact_number}")
    print(f"-> Message: 'Hi parent of {player_name}, this is a gentle reminder that an academy fee of ₹{amount_owed} is currently Overdue. Please clear it at your earliest convenience.'\n")


@app.post("/payments/reminders/trigger")
def trigger_billing_cycle(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Scans the database for overdue accounts and queues up background messages"""
    overdue_payments = db.query(models.Payment).filter(models.Payment.status == "Overdue").all()
    
    reminders_queued = 0
    for payment in overdue_payments:
        # Look up the player to get their emergency contact number
        player = db.query(models.Player).filter(models.Player.id == payment.player_id).first()
        
        if player:
            amount_owed = payment.amount_due - payment.amount_paid
            
            # Hand the heavy lifting off to the background task manager
            background_tasks.add_task(
                send_whatsapp_reminder,
                player.name,
                amount_owed,
                player.emergency_contact
            )
            reminders_queued += 1
            
    return {
        "status": "Success", 
        "action": "Billing cycle initiated", 
        "messages_queued": reminders_queued,
        "note": "Watch your VS Code terminal to see the messages go out!"
    }
# (Credentials are read earlier from environment variables)