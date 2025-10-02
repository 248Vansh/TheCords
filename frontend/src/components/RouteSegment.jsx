import { MapPin, ArrowRight, AlertCircle } from 'lucide-react';
import { WeatherIcon } from './WeatherIcon';

function parseWeatherInfo(locationStr) {
  // Try to match "CityName (Weather: Description, Temp°C)"
  const startIdx = locationStr.indexOf("(Weather:");
  if (startIdx === -1) return { city: locationStr, description: 'Unknown', temperature: '--' };

  const city = locationStr.slice(0, startIdx).trim();
  const weatherPart = locationStr.slice(startIdx + 9, locationStr.length - 1).trim(); // remove "(Weather:" and ")"
  const commaIdx = weatherPart.lastIndexOf(","); 
  if (commaIdx === -1) return { city, description: weatherPart, temperature: '--' };

  const description = weatherPart.slice(0, commaIdx).trim();
  const temperature = weatherPart.slice(commaIdx + 1).replace("°C","").trim();

  return { city, description, temperature };
}

export function RouteSegment({ segment, index }) {
  const fromInfo = parseWeatherInfo(segment.from);
  const toInfo = parseWeatherInfo(segment.to);

  return (
    <div className="route-segment bg-white rounded-2xl shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 text-white flex items-center justify-center font-semibold text-sm">
            {index + 1}
          </div>
          <span className="text-sm font-medium text-gray-500">Segment</span>
        </div>
        <div className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium">
          {segment.highway}
        </div>
      </div>

      <div className="space-y-4 md:flex md:gap-4">
        {/* From */}
        <div className="flex-1 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <MapPin size={18} className="text-green-600" />
            <span className="font-semibold text-gray-900">{fromInfo.city}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <WeatherIcon description={fromInfo.description} size={16} />
            <span>{fromInfo.description}</span>
            <span className="ml-auto font-medium">{fromInfo.temperature}°C</span>
          </div>
        </div>

        <div className="pt-6 hidden md:block">
          <ArrowRight size={24} className="text-gray-400" />
        </div>

        {/* To */}
        <div className="flex-1 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <MapPin size={18} className="text-red-600" />
            <span className="font-semibold text-gray-900">{toInfo.city}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <WeatherIcon description={toInfo.description} size={16} />
            <span>{toInfo.description}</span>
            <span className="ml-auto font-medium">{toInfo.temperature}°C</span>
          </div>
        </div>
      </div>

      {segment.guidelines && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mt-4">
          <div className="flex items-start gap-3">
            <AlertCircle size={18} className="text-amber-600 mt-1 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-amber-900 text-sm mb-1">Safety Guidelines</h4>
              <p className="text-sm text-amber-800 leading-relaxed">{segment.guidelines}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}