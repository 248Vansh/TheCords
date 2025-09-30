import React, { useState } from "react";
import axios from "axios";

const cities = [
  "Delhi", "Mumbai", "Kolkata", "Chennai", "Bengaluru",
  "Lucknow", "Guwahati", "Jaipur", "Patna", "Siliguri"
];

function App() {
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [route, setRoute] = useState("");

  const handleSubmit = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/route", {
        start,
        end
      });
      setRoute(res.data.initial_route);
    } catch (err) {
      console.error(err);
      setRoute("Error fetching route. Please try again.");
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">🚗 Smart Route Planner</h1>

      <div className="mb-4">
        <input
          list="cities"
          className="border rounded p-2 w-full"
          placeholder="Start city"
          value={start}
          onChange={(e) => setStart(e.target.value)}
        />
      </div>

      <div className="mb-4">
        <input
          list="cities"
          className="border rounded p-2 w-full"
          placeholder="End city"
          value={end}
          onChange={(e) => setEnd(e.target.value)}
        />
        <datalist id="cities">
          {cities.map((c) => (
            <option key={c} value={c} />
          ))}
        </datalist>
      </div>

      <button
        onClick={handleSubmit}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        Find Route
      </button>

      {route && (
        <div className="mt-6 p-4 border rounded bg-gray-50">
          <h2 className="font-semibold mb-2">Suggested Route:</h2>
          <p>{route}</p>
        </div>
      )}
    </div>
  );
}

export default App;
