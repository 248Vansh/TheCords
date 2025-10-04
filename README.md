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
