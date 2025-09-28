import pathway as pw
from weather import get_weather

# Prepare data
cities = ["Delhi", "Mumbai", "Bangalore"]
table_data = [{"city": city, "weather": get_weather(city)} for city in cities]

# Create a table
table = pw.Table.from_records(table_data)

# Define a UDF
@pw.udf
def risk_advice(weather: str) -> str:
    if "Rain" in weather or "Mist" in weather:
        return "⚠️ Risky route today"
    return "✅ Route looks safe"

# Apply UDF
result = table.select(
    city=pw.this.city,
    weather=pw.this.weather,
    advice=risk_advice(pw.this.weather)
)

# Print result
pw.debug.print(result)







