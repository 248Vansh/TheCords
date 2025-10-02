import { Cloud, CloudRain, CloudSnow, Sun, CloudDrizzle, Wind } from 'lucide-react';

export function WeatherIcon({ description, size = 20 }) {
  const desc = description.toLowerCase();
  if (desc.includes('rain') || desc.includes('shower')) return <CloudRain size={size} className="text-blue-500" />;
  if (desc.includes('snow')) return <CloudSnow size={size} className="text-blue-300" />;
  if (desc.includes('drizzle')) return <CloudDrizzle size={size} className="text-blue-400" />;
  if (desc.includes('cloud')) return <Cloud size={size} className="text-gray-500" />;
  if (desc.includes('wind')) return <Wind size={size} className="text-gray-600" />;
  if (desc.includes('clear') || desc.includes('sun')) return <Sun size={size} className="text-yellow-500" />;
  return <Cloud size={size} className="text-gray-400" />;
}