import { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ChatbotWidget from "./Chatbot"; // Floating chatbot
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./components/Home";
import About from "./components/About";

function App() {

  // Clock state
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const interval = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Router>
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 relative">
      {/* Top-right Clock */}
      <Navbar time={time} />
      <main className="flex-1 pt-24">
        <Routes>
          <Route exact path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>
      <Footer />
      {/* Floating Chatbot */}
      <ChatbotWidget
        buttonClassName="fixed bottom-6 right-6 bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 rounded-full shadow-xl hover:from-blue-700 hover:to-blue-800 transition"
        panelClassName="fixed bottom-20 right-6 w-80 shadow-2xl rounded-xl overflow-hidden bg-white border border-gray-200 transition-transform duration-300"
      />
    </div>
    </Router>
  );
}

export default App;