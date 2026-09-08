# LandGuard AI — Complete Functional Prototype

SIH26001 — AI-Based Landslide Early Warning and Risk Monitoring System in NER.

## What this version includes
- Responsive web command center
- Risk cells with calculated risk + confidence
- Risk map visualization
- Evidence Verification screen
- Evidence Fusion concept
- Local Impact Graph
- Response Prioritizer
- Action/alert queue with persistence
- Citizen/field report submission with offline flag
- Mobile field mode
- System architecture and validation plan
- Python backend API + SQLite database
- Transparent demo risk engine (not a fake trained ML model)

## Run locally
Requires Python 3.9+.

```bash
cd backend
python server.py
```
Open `http://localhost:8000`.

## API
- `GET /api/health`
- `GET /api/cells`
- `GET /api/reports`
- `POST /api/reports`
- `GET /api/alerts`
- `POST /api/alerts`

## Important honesty boundary
The included risk engine uses a transparent weighted scoring formula over simulated demonstration inputs. It is deliberately not presented as a trained landslide-prediction model. For production, replace the data adapters and scoring layer with validated rainfall, satellite/SAR, DEM, historical landslide and sensor pipelines; train/calibrate models on domain data; and validate thresholds with disaster-management experts.

## Suggested demo flow
1. Command Center: show high-risk cells and the Predict → Verify → Localize → Act loop.
2. Risk Map: show road/village localization concept.
3. Evidence Verification: explain why risk and confidence are separate.
4. Create an alert and show it in Action & Alerts.
5. Submit a field report, optionally mark it offline, then show it in the verification queue.
6. Mobile Field Mode: show how a field team operates with weak connectivity.
7. Architecture/Data & Validation: explain what is implemented now and what connects to real data in the next stage.
