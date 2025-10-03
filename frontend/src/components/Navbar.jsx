import { Navigation } from "lucide-react";

export default function Navbar({ time }) {
  return (
    <nav className="bg-white shadow-md fixed top-0 left-0 w-full z-50">
      <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
        
        {/* Left: Logo + App Name */}
        <div className="flex items-center gap-2">
          <Navigation size={26} className="text-blue-600" />
          <span className="text-xl font-bold text-gray-900">Smart Route Planner</span>
        </div>

        {/* Right: Links + Clock */}
        <div className="flex items-center gap-8">
          <div className="hidden md:flex gap-8">
            <a href="/" className="text-gray-700 hover:text-blue-600 font-medium">
              Home
            </a>
            <a href="/" className="text-gray-700 hover:text-blue-600 font-medium">
              Planner
            </a>
            <a href="/about" className="text-gray-700 hover:text-blue-600 font-medium">
              About
            </a>
          </div>

          <div className="text-gray-700 font-semibold bg-slate-50 px-4 py-2 rounded-lg shadow-sm">
            {time.toLocaleTimeString()}
          </div>
        </div>
      </div>
    </nav>
  );
}
