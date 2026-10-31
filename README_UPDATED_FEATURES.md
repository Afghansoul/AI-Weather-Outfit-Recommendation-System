# AI-Based Weather-Aware Outfit Recommendation System — Updated Build

## Added in this build
1. Afghan city/provincial-centre local coordinate fallback plus Open-Meteo geocoding (up to 100 results).
2. Automatic synchronization of current weather values with Streamlit widgets; season and weather condition are detected from the selected live weather data.
3. Daily forecast analysis for the selected destination/date and departure hour (temperature range, rain probability, precipitation, wind, and hourly humidity).
4. Outfit Planner with Random Forest prediction, saved plans, and weather-related in-app alerts.
5. Notification Centre with unread/read status.
6. Dashboard cards now include actual user plans and unread notification counts; dataset row count and model-file presence are read from local project files.
7. Added SQLite tables are created automatically without deleting existing users, weather records, recommendations, or favorites.

## Run locally
1. Keep a backup of your existing project folder and `database/weather_outfit.db`.
2. Extract this ZIP to a new folder.
3. Open the folder in VS Code.
4. Install dependencies:
   `pip install -r requirements.txt`
5. Start:
   `streamlit run app.py`

## Deployment
Commit and push the updated project files to the same GitHub repository connected to Streamlit Community Cloud. Keep the existing secrets/configuration if any. The SQLite database on Streamlit Community Cloud may not provide durable storage across redeployments/restarts; use this build for demonstration unless persistent hosting storage is configured.

## Important limits and honest reporting
- The offline Afghan gazetteer covers the 34 provincial capitals/major centres and several common Dari/Pashto/English spellings, including Pul-e-Alam (Logar). Smaller districts and villages still depend on Open-Meteo geocoding and are not guaranteed.
- Forecast planning is limited to the provider's available 7-day forecast window.
- Notifications are in-app notifications created when the user loads severe current weather or saves a plan. This build does not send push notifications while the browser/app is closed.
- The daily forecast endpoint does not provide daily humidity; the planner uses hourly humidity at the chosen departure hour.
- The model's previously reported ~91% score is on the controlled project dataset, not a guarantee of real-world performance.
- Live API calls and full browser UI interaction must be verified on the user's own computer/network before defense.
