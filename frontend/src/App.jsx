import { useState, useEffect } from "react";
import { Navigation, Loader2, MapPin, Route as RouteIcon } from "lucide-react";
import { RouteSegment } from "./components/RouteSegment";
import Select from "react-select";

function App() {
  const [cities, setCities] = useState([]);
  const [start, setStart] = useState(null);
  const [end, setEnd] = useState(null);
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loadingCities, setLoadingCities] = useState(true);

  // Chatbot states
  const [chatMessage, setChatMessage] = useState("");
  const [chatReply, setChatReply] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

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

  // Chatbot submission
  const handleChat = async (e) => {
    e.preventDefault();
    if (!chatMessage.trim()) return;

    setChatLoading(true);
    setChatReply("");

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: chatMessage }),
      });
      const data = await res.json();
      setChatReply(data.reply);
    } catch (err) {
      console.error(err);
      setChatReply("⚠️ Error connecting to server.");
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
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

            {routeData.route_segments.map((segment, index) => (
              <RouteSegment key={index} segment={segment} index={index} />
            ))}

            <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-xl p-6 text-center">
              <p className="text-green-800 font-semibold">
                Journey Complete! Safe travels on your route.
              </p>
            </div>
          </div>
        )}

        {/* Chatbot Section */}
        <div className="mt-12 bg-white rounded-2xl shadow-xl p-6 slide-up">
          <h2 className="text-2xl font-bold mb-4">Ask Smart Assistant</h2>
          <form onSubmit={handleChat} className="flex gap-3">
            <input
              type="text"
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              placeholder="Ask about safety, weather, routes..."
              className="flex-1 border border-gray-300 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={chatLoading}
              className="bg-blue-600 text-white px-6 py-2 rounded-xl hover:bg-blue-700 transition"
            >
              {chatLoading ? "..." : "Send"}
            </button>
          </form>

          {chatReply && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-xl">
              <p className="text-gray-800">{chatReply}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;