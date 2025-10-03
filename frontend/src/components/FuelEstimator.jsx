import { useState } from "react";

export default function FuelEstimator({ distance }) {
  const [vehicle, setVehicle] = useState("");
  const [fuelType, setFuelType] = useState("Petrol");
  const [result, setResult] = useState(null);

  // Hardcoded average mileage (km/l) for demo purposes
  const VEHICLE_MILEAGE = {
    "Honda City": 16,
    "Maruti Swift": 18,
    "Hyundai Creta": 15,
    "Toyota Fortuner": 10,
    "Royal Enfield Classic": 35
  };

  // Hardcoded fuel prices in INR/l
  const FUEL_PRICES = {
    Petrol: 110,
    Diesel: 100,
    CNG: 80
  };

  const VEHICLES_LIST = Object.keys(VEHICLE_MILEAGE);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!vehicle) return;

    // Use hardcoded mileage or default to 15 km/l
    const baseMileage = VEHICLE_MILEAGE[vehicle] || 15;
    const practicalMileage = (baseMileage * 0.85).toFixed(1);

    const pricePerLiter = FUEL_PRICES[fuelType] || 110;
    const estimatedCost = ((distance / practicalMileage) * pricePerLiter).toFixed(0);

    setResult({
      vehicle,
      fuel_type: fuelType,
      distance_km: distance.toFixed(1),
      practical_mileage: practicalMileage,
      price_per_liter: pricePerLiter,
      estimated_cost: estimatedCost
    });
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

        <button
          type="submit"
          className="bg-blue-600 text-white py-2 px-4 rounded w-full"
        >
          Estimate Fuel Cost
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

