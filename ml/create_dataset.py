import csv
import random
from pathlib import Path


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

OUTPUT_FILE = Path(__file__).parent / "dataset.csv"

NUMBER_OF_ROWS = 1500

random.seed(42)


# --------------------------------------------------
# POSSIBLE VALUES
# --------------------------------------------------

SEASONS = [
    "Winter",
    "Spring",
    "Summer",
    "Autumn"
]

CONDITIONS = [
    "Clear",
    "Cloudy",
    "Rainy",
    "Snowy",
    "Stormy"
]

OCCASIONS = [
    "Casual",
    "Formal",
    "Sport",
    "Business",
    "Traditional"
]

STYLES = [
    "Casual",
    "Sporty",
    "Formal",
    "Business",
    "Traditional"
]


# --------------------------------------------------
# OUTFIT CLASSIFICATION RULE
# --------------------------------------------------

def determine_outfit(
    temperature,
    humidity,
    wind_speed,
    rain,
    season,
    condition,
    occasion,
    style
):

    # Snow / extreme cold
    if condition == "Snowy" or temperature <= 0:

        return "Heavy Winter Outfit"

    # Very cold weather
    if temperature <= 8:

        if occasion == "Formal":
            return "Formal Winter Outfit"

        return "Winter Outfit"

    # Rain
    if rain == 1 or condition == "Rainy":

        if temperature <= 15:
            return "Rainy Cold Outfit"

        return "Rainy Light Outfit"

    # Cold / cool
    if temperature <= 15:

        if style == "Sporty" or occasion == "Sport":
            return "Sport Winter Outfit"

        return "Light Winter Outfit"

    # Mild weather
    if temperature <= 22:

        if occasion == "Formal":
            return "Formal Mild Outfit"

        return "Spring Autumn Outfit"

    # Warm weather
    if temperature <= 30:

        if style == "Sporty" or occasion == "Sport":
            return "Sport Summer Outfit"

        return "Light Summer Outfit"

    # Very hot weather
    return "Hot Weather Outfit"


# --------------------------------------------------
# GENERATE DATASET
# --------------------------------------------------

rows = []


for _ in range(NUMBER_OF_ROWS):

    temperature = round(
        random.uniform(-10, 42),
        1
    )

    humidity = random.randint(
        20,
        95
    )

    wind_speed = round(
        random.uniform(0, 45),
        1
    )

    season = random.choice(
        SEASONS
    )

    condition = random.choice(
        CONDITIONS
    )

    occasion = random.choice(
        OCCASIONS
    )

    style = random.choice(
        STYLES
    )

    # Rain probability
    if condition in ["Rainy", "Stormy"]:

        rain = 1

    elif condition == "Snowy":

        rain = 0

    else:

        rain = 1 if random.random() < 0.12 else 0


    outfit_category = determine_outfit(
        temperature,
        humidity,
        wind_speed,
        rain,
        season,
        condition,
        occasion,
        style
    )


    rows.append([
        temperature,
        humidity,
        wind_speed,
        rain,
        season,
        condition,
        occasion,
        style,
        outfit_category
    ])


# --------------------------------------------------
# SAVE CSV
# --------------------------------------------------

columns = [
    "temperature",
    "humidity",
    "wind_speed",
    "rain",
    "season",
    "weather_condition",
    "occasion",
    "style",
    "outfit_category"
]


with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow(columns)

    writer.writerows(rows)


print("=" * 55)
print("DATASET CREATED SUCCESSFULLY")
print("=" * 55)
print(f"File: {OUTPUT_FILE}")
print(f"Rows: {len(rows)}")
print(f"Columns: {len(columns)}")
print()
print("Columns:")

for column in columns:
    print(f" - {column}")

print("=" * 55)
