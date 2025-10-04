# Dynamic RAG Travel Assistant with Pathway

## Overview

This project is a **Dynamic RAG (Retrieval-Augmented Generation)** Travel Assistant leveraging the **Pathway** framework for real-time data ingestion, processing, and AI-powered recommendations. It combines **ETL pipelines**, **dynamic document retrieval**, and **AI generation** to provide users with accurate travel routes, traffic updates, weather forecasts, and fuel cost estimations.

Pathway empowers this system by enabling **dynamic, reactive updates** to structured and unstructured data sources without requiring heavy polling or manual reloads. With Pathway, changes in CSV datasets are immediately reflected in the application's outputs, making it ideal for live travel guidance.

## Features

* **Dynamic Route Planning**: Fetches optimal routes between cities using a combination of structured CSV highway data and AI-generated fallback routes.
* **Real-Time Traffic & Weather**: Integrates Google Maps traffic information and live weather data to provide users with actionable insights.
* **Fuel Cost Estimation**: Calculates realistic fuel costs using vehicle specifications, fuel type, and distance between locations. Supports Gemini-based distance retrieval.
* **Dynamic RAG for LLMs**: Uses Pathway to implement a Dynamic RAG workflow where LLMs can query structured highway data and receive instant, accurate responses.
* **ETL Integration**: CSV highway datasets are processed via Pathway ETL pipelines, automatically transforming raw data into structured tables for AI consumption.
* **Frontend Integration**: Provides endpoints for route lookup, city listing, chat interactions, and fuel cost calculations.

## Architecture

### Pathway ETL Pipeline

```python
from pathway import Table, io

documents = io.csv.read(
    path="./highways/highways_full.csv",
    schema=HighwaySchema,
    mode="dynamic"  # Ensures live updates are reflected
)
```

* **Dynamic Mode**: Pathway monitors the CSV for changes. Updates propagate automatically to downstream AI queries without frontend reloads.
* **Schema Enforcement**: Ensures structured ingestion of highway and city data.

### AI & Dynamic RAG

* Queries to the LLM first attempt to retrieve from the **highway CSV**.
* If CSV data is insufficient, the model falls back to AI-generated routes.
* This **Dynamic RAG** approach ensures high accuracy while keeping the system responsive.

## Tech Stack

* **Backend:** FastAPI (Python 3.12)
* **Data Pipeline:** Pathway (for real-time CSV table updates and Dynamic RAG ETL processing)
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

> Fuel price can come from **Gemini API** or local DB fallback. Pathway can integrate Dynamic RAG to suggest more accurate fuel price estimates from structured datasets.

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
  * `dynamic`: Updates Pathway table in real-time when CSV changes, enabling **Dynamic RAG**.
* **ETL:** Pathway reads CSV into an internal table. Frontend can consume updated data via API without reloading if `dynamic` mode is enabled.
* Pathway's Dynamic RAG ensures your travel assistant **reacts to dataset changes in near real-time**, combining ETL and AI guidance seamlessly.

### Fuel Cost Endpoint

* Uses Gemini to fetch distances and price data.
* Local DB fallback ensures continuity if Gemini fails.
* Calculates practical mileage and estimated fuel costs based on vehicle specifications.

### Pathway Advantages

* Real-time, reactive updates to CSV datasets.
* Seamless ETL integration with structured schemas.
* Dynamic RAG workflow minimizes redundant LLM calls.
* High reliability for AI-powered travel applications.

## API Endpoints

* `POST /route` - Returns route segments with traffic, weather, and driving tips.
* `GET /cities` - Lists all cities available in the highway dataset.
* `POST /chat` - Chat interface for travel advice.
* `POST /fuel_cost` - Estimates fuel cost for a given vehicle, fuel type, and route.

## Usage

1. Set environment variables in `.env` (e.g., `GOOGLE_MAPS_API_KEY`).
2. Run the FastAPI backend.
3. Frontend automatically consumes endpoints.
4. Update CSV datasets, and Pathway ensures changes propagate dynamically.

## Future Enhancements

* Expand Dynamic RAG capabilities to incorporate more document types.
* Integrate real-time user location for live traffic rerouting.
* Enhance fuel cost predictions with live market data ingestion.

---

*Powered by Pathway: Dynamic, reactive ETL + AI pipelines made effortless.*
