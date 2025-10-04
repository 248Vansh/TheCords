import { useState, useEffect } from "react";

export default function FuelEstimator({ start, end, distance }) {
  const [vehicle, setVehicle] = useState("");
  const [fuelType, setFuelType] = useState("Petrol");
  const [origin, setOrigin] = useState(start || "");
  const [destination, setDestination] = useState(end || "");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false); // ✅ new loading state

  useEffect(() => {
    if (start) setOrigin(start);
    if (end) setDestination(end);
  }, [start, end]);

  const VEHICLES_LIST = [
    "Honda City",
    "Maruti Swift",
    "Hyundai Creta",
    "Toyota Fortuner",
    "Royal Enfield Classic"
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!vehicle || !origin || !destination) return;

    setLoading(true);   // ✅ start loader
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/fuel_cost", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          vehicle,
          fuel_type: fuelType,
          start: origin,
          end: destination
        }),
      });

      if (!response.ok) throw new Error("Backend error");

      const data = await response.json();
      console.log("Fuel API Response:", data);
      setResult(data);

    } catch (err) {
      console.error("Error fetching fuel estimate:", err);
    } finally {
      setLoading(false);  // ✅ stop loader
    }
  };

  return (
    <div className="bg-white p-6 rounded-2xl shadow-md mb-6">
      <h3 className="font-semibold mb-4 text-gray-900">Fuel Cost Estimator</h3>
      <form onSubmit={handleSubmit} className="space-y-4">

        <select
          value={vehicle}
          onChange={(e) => setVehicle(e.target.value)}
          className="w-full border rounded p-2"
        >
          <option value="">Select vehicle model</option>
          {VEHICLES_LIST.map((v) => (
            <option key={v} value={v}>{v}</option>
          ))}
        </select>

        <select
          value={fuelType}
          onChange={(e) => setFuelType(e.target.value)}
          className="w-full border rounded p-2"
        >
          <option value="Petrol">Petrol</option>
          <option value="Diesel">Diesel</option>
          <option value="CNG">CNG</option>
        </select>

        {/* Editable but pre-filled with route */}
        <input
          type="text"
          placeholder="Enter origin"
          value={origin}
          onChange={(e) => setOrigin(e.target.value)}
          className="w-full border rounded p-2"
        />

        <input
          type="text"
          placeholder="Enter destination"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          className="w-full border rounded p-2"
        />

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white py-2 px-4 rounded w-full flex items-center justify-center"
        >
          {loading ? (
            <>
              <span className="mr-2">Calculating...</span>
              <svg
                className="animate-spin h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                ></path>
              </svg>
            </>
          ) : (
            "Estimate Fuel Cost"
          )}
        </button>
      </form>

      {result && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded">
          <p><strong>Vehicle:</strong> {result.vehicle}</p>
          <p><strong>Fuel Type:</strong> {result.fuel_type}</p>
          <p><strong>Distance:</strong> {result.distance_km} km</p>
          <p><strong>Practical Mileage:</strong> {result.practical_mileage} km/l</p>
          <p><strong>Price per liter:</strong> ₹{result.price_per_liter}</p>
          <p className="font-semibold"><strong>Estimated Cost:</strong> ₹{result.estimated_cost}</p>
        </div>
      )}
    </div>
  );
}
