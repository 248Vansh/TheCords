import { CloudLightning, Map, Brain } from "lucide-react";

export default function About() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 pt-24 pb-16 px-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">About Smart Route Planner</h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            An innovative application built on <span className="font-semibold text-blue-600">Pathway</span> with
            <span className="font-semibold text-blue-600"> dynamic RAG</span>, designed to make travel safer and smarter.
          </p>
        </div>

        {/* Problem Statement */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-10">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <CloudLightning className="text-blue-600" />
            The Problem
          </h2>
          <p className="text-gray-700 leading-relaxed">
            Travelers on national highways often face unexpected challenges like sudden weather changes,
            unsafe routes, and inefficient travel planning. Existing navigation tools do not always update
            in real time, leaving users without the information they need to make the best decisions on the road.
          </p>
        </div>

        {/* Our Solution */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-10">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Map className="text-green-600" />
            Our Solution
          </h2>
          <p className="text-gray-700 leading-relaxed">
            Smart Route Planner continuously analyzes national highways and dynamically fetches
            <span className="font-semibold text-green-700"> real-time weather data</span>. 
            It instantly suggests the safest and most efficient path for your journey, while providing
            AI-powered assistance and safety guidelines along the way.
          </p>
        </div>

        {/* Technology */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <Brain className="text-purple-600" />
            The Technology
          </h2>
          <p className="text-gray-700 leading-relaxed">
            The application is built on <span className="font-semibold text-blue-600">Pathway</span>, 
            a real-time data processing engine, combined with 
            <span className="font-semibold text-blue-600"> dynamic Retrieval-Augmented Generation (RAG)</span>.
            This ensures the system ingests live highway and weather data, updates responses instantly, 
            and keeps your route recommendations accurate at all times.
          </p>
        </div>
      </div>
    </div>
  );
}
