# Pathway Travel Assistant

A web-based travel assistant that provides **routes, traffic, weather, and fuel cost estimates** in real-time using **Pathway**, Google Maps, and Gemini APIs.

---

## Features

* Generate **step-by-step routes** between cities.
* Include **live traffic information** and **weather updates**.
* Estimate **fuel cost** based on vehicle, fuel type, and distance.
* Supports **CSV-based highway datasets** for route generation.
* **Dynamic CSV updates** (Pathway automatically updates internal tables).
* **Gemini AI integration** for route suggestions and guidance.
* **CORS-enabled FastAPI backend** for frontend integration.

---

## Tech Stack

* **Backend:** FastAPI (Python 3.12)
* **Data Pipeline:** Pathway (for real-time CSV table updates)
* **APIs:**

  * Google Maps Directions API (for distances and traffic)
  * Gemini API (AI-powered route guidance and fuel price estimates)
* **Frontend:** Any frontend (React/VanillaJS) can consume REST endpoints.
* **Data:** CSV datasets (`highways_full.csv`) for highways, cities, and distances.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/pathway-travel-assistant.git
cd pathway-travel-assistant
```

2. Create a Python virtual environment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:

```env
GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_KEY
GEMINI_API_KEY=YOUR_GEMINI_KEY
```

---

## Running the Server

```bash
uvicorn main:app --reload
```

* The API will be available at `http://127.0.0.1:8000`.
* Swagger docs: `http://127.0.0.1:8000/docs`

---

## Endpoints

### 1. `/route` [POST]

Generate route between two cities.

**Request Body:**

```json
{
  "start": "Amritsar",
  "end": "Atari"
}
```

**Response:**

```json
{
  "route_segments": [
    {
      "from": "Amritsar (Weather: Clear, 25°C)",
      "to": "Atari (Weather: Cloudy, 27°C)",
      "highway": "NH3",
      "traffic": [...],
      "distance_km": 35,
      "guidelines": "🚗 Drive safely, avoid sharp turns..."
    }
  ],
  "total_distance_km": 35
}
```

---

### 2. `/fuel_cost` [POST]

Estimate fuel cost for a trip.

**Request Body:**

```json
{
  "vehicle": "Honda City",
  "fuel_type": "Petrol",
  "start": "Amritsar",
  "end": "Atari"
}
```

**Response:**

```json
{
  "vehicle": "Honda City",
  "fuel_type": "Petrol",
  "distance_km": 230,
  "official_mileage": 16,
  "practical_mileage": 13.6,
  "price_per_liter": 98,
  "estimated_cost": 1662.35
}
```

> Fuel price can come from **Gemini API** or local DB fallback.

---

### 3. `/cities` [GET]

Returns the list of available cities from the highways dataset.

**Response:**

```json
{
  "cities": ["Amritsar", "Atari", "Delhi", "Mumbai", ...]
}
```

---

### 4. `/chat` [POST]

Ask a question to the travel assistant.

**Request Body:**

```json
{
  "message": "How should I travel from Amritsar to Atari today?"
}
```

**Response:**

```json
{
  "reply": "🚗 Take NH3 from Amritsar to Atari. Expect light traffic and sunny weather. Fuel up before leaving. Drive safely! ⛽"
}
```

---

## Data Management

* **CSV Dataset:** `highways/highways_full.csv`
* **Schema:** `HighwaySchema` (start_city, end_city, highway, etc.)
* **Pathway Mode:**

  * `static`: Reads CSV once on server start.
  * `dynamic`: Updates Pathway table in real-time when CSV changes.
* **ETL-like Behavior:** Pathway reads CSV into an internal table. Frontend can consume updated data via API without reloading if `dynamic` mode is enabled.

---

## Notes

* **Distance Calculation:** Currently uses Gemini AI (Google Maps fallback optional).
* **Fuel Price:** Gemini AI provides latest price; fallback to local DB if unavailable.
* **Traffic & Weather:** Cached for efficiency, updated per request.

---

## Future Improvements

* Real-time frontend updates using WebSockets.
* Expanded CSV dataset with more cities and highways.
* Dynamic fuel prices integrated with real-time APIs.
* Enhanced Gemini prompts for more accurate route suggestions.
