import { useState, useEffect } from "react";
import { Navigation, Loader2, MapPin, Route as RouteIcon } from "lucide-react";
import { RouteSegment } from "./components/RouteSegment";
import FuelEstimator from "./components/FuelEstimator"; // ✅ Only once
import Select from "react-select";
import ChatbotWidget from "./Chatbot"; // Floating chatbot

function App() {
  const [cities, setCities] = useState([]);
  const [start, setStart] = useState(null);
  const [end, setEnd] = useState(null);
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loadingCities, setLoadingCities] = useState(true);

  // Clock state
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const interval = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  // Fetch cities dynamically
  useEffect(() => {
    fetch("http://127.0.0.1:8000/cities")
      .then((res) => res.json())
      .then((data) => {
        if (data.cities) {
          setCities(
            data.cities.map((city) => ({
              value: city,
              label: city,
            }))
          );
        }
      })
      .catch((err) => {
        console.error("Failed to load cities:", err);
        setError("Unable to load city list. Try again later.");
      })
      .finally(() => setLoadingCities(false));
  }, []);

  // Route planner submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!start || !end) {
      setError("Please select both start and end cities");
      return;
    }
    if (start.value === end.value) {
      setError("Start and end cities must be different");
      return;
    }

    setLoading(true);
    setError("");
    setRouteData(null);

    try {
      const res = await fetch("http://127.0.0.1:8000/route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start: start.value, end: end.value }),
      });

      if (!res.ok) throw new Error("Failed to fetch route");
      const data = await res.json();
      setRouteData(data);
    } catch (err) {
      console.error(err);
      setError(
        "Unable to fetch route. Please check your connection and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  // Calculate total route distance in km
  const totalDistanceKm = routeData?.route_segments?.reduce((acc, seg) => {
    const lastTraffic = seg.traffic?.[0];
    if (lastTraffic?.distance?.value) {
      return acc + lastTraffic.distance.value / 1000; // meters → km
    }
    return acc;
  }, 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 relative">
      {/* Top-right Clock */}
      <div className="absolute top-6 right-6 text-gray-700 font-semibold text-lg bg-white px-4 py-2 rounded-xl shadow-md">
        {time.toLocaleTimeString()}
      </div>

      <div className="max-w-5xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12 fade-in">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl mb-4 shadow-xl">
            <Navigation size={32} className="text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2 tracking-tight">
            Smart Route Planner
          </h1>
          <p className="text-lg text-gray-600">
            Plan your journey with real-time weather, safety guidelines, and AI assistance
          </p>
        </div>

        {/* Route Planner Form */}
        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-2xl shadow-xl p-8 mb-8 slide-up"
        >
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <div>
              <label
                htmlFor="start"
                className="block text-sm font-semibold text-gray-700 mb-2"
              >
                <MapPin size={16} className="inline mr-1 text-green-600" />
                Starting Point
              </label>
              <Select
                id="start"
                options={cities}
                value={start}
                onChange={(opt) => setStart(opt)}
                isLoading={loadingCities}
                isClearable
                placeholder="Select or search city..."
              />
            </div>
            <div>
              <label
                htmlFor="end"
                className="block text-sm font-semibold text-gray-700 mb-2"
              >
                <MapPin size={16} className="inline mr-1 text-red-600" />
                Destination
              </label>
              <Select
                id="end"
                options={cities}
                value={end}
                onChange={(opt) => setEnd(opt)}
                isLoading={loadingCities}
                isClearable
                placeholder="Select or search city..."
              />
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || loadingCities}
            className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white font-semibold py-4 px-6 rounded-xl hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                Finding Best Route...
              </>
            ) : (
              <>
                <RouteIcon size={20} />
                Find Best Route
              </>
            )}
          </button>
        </form>

        {/* Route Results */}
        {routeData?.route_segments?.length > 0 && (
          <div className="space-y-6 slide-up">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-1 flex-1 bg-gradient-to-r from-blue-600 to-blue-400 rounded-full"></div>
              <h2 className="text-2xl font-bold text-gray-900">Your Route</h2>
              <div className="h-1 flex-1 bg-gradient-to-l from-blue-600 to-blue-400 rounded-full"></div>
            </div>

            {/* Route Segments */}
            {routeData.route_segments.map((segment, index) => (
              <RouteSegment key={index} segment={segment} index={index} />
            ))}

            {/* Fuel Estimator below route segments */}
            <FuelEstimator distance={totalDistanceKm} />

            <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-xl p-6 text-center">
              <p className="text-green-800 font-semibold">
                Journey Complete! Safe travels on your route.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Floating Chatbot */}
      <ChatbotWidget
        buttonClassName="fixed bottom-6 right-6 bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 rounded-full shadow-xl hover:from-blue-700 hover:to-blue-800 transition"
        panelClassName="fixed bottom-20 right-6 w-80 shadow-2xl rounded-xl overflow-hidden bg-white border border-gray-200 transition-transform duration-300"
      />
    </div>
  );
}

export default App;