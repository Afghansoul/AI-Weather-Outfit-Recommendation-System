import streamlit as st
import requests
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.database import (
    initialize_database,
    create_user,
    authenticate_user,
    get_user,
    get_user_recommendations,
    get_user_favorites,
    get_statistics,
    save_weather,
    save_recommendation,
    add_favorite,
    get_all_users,
    update_user_role,
    get_security_question,
    verify_security_answer,
    reset_password,
)
from ml.predict import get_prediction_confidence
from translations import translate
# --------------------------------------------------
# DATABASE
# --------------------------------------------------

initialize_database()

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="AI Weather-Aware Outfit Recommendation System",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
/* ==================================================
   PREMIUM / STREAMLIT UI
   Netflix-inspired visual language without replacing
   Streamlit's responsive layout or native widgets.
================================================== */
:root {
    --app-bg: var(--background-color);
    --app-surface: var(--secondary-background-color);
    --app-text: var(--text-color);
    --app-primary: var(--primary-color);
    --ui-border: color-mix(in srgb, var(--app-text) 13%, transparent);
    --ui-muted: color-mix(in srgb, var(--app-text) 68%, transparent);
    --ui-shadow: 0 14px 40px rgba(0,0,0,0.10);
    --ui-radius: 16px;
}

/* ---------- Global ---------- */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
section.main,
.main {
    background: var(--app-bg) !important;
    color: var(--app-text) !important;
}

[data-testid="stMainBlockContainer"] {
    max-width: 1380px;
    padding-top: 1.6rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4, h5, h6,
p, li,
[data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"],
[data-testid="stCaptionContainer"] {
    color: var(--app-text) !important;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] .block-container {
    background: var(--app-surface) !important;
    color: var(--app-text) !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.35rem;
    padding-left: 1rem;
    padding-right: 1rem;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
    color: var(--app-text) !important;
}

section[data-testid="stSidebar"] hr {
    border-color: var(--ui-border) !important;
    margin: 18px 0;
}

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 5px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    border: 1px solid transparent;
    border-radius: 11px;
    padding: 9px 10px;
    color: var(--app-text) !important;
    transition: background .18s ease, border-color .18s ease, transform .18s ease;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: color-mix(in srgb, var(--app-primary) 9%, transparent);
    border-color: var(--ui-border);
    transform: translateX(2px);
}

/* ---------- Language selector ---------- */
.language-selector-label {
    color: var(--app-text) !important;
    font-size: .82rem;
    font-weight: 650;
    margin-bottom: .25rem;
}

div[data-baseweb="select"] > div {
    background: var(--app-surface) !important;
    color: var(--app-text) !important;
    border: 1px solid var(--ui-border) !important;
    border-radius: 10px !important;
    min-height: 42px;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] input,
div[data-baseweb="select"] [data-testid="stMarkdownContainer"] {
    color: var(--app-text) !important;
}

ul[role="listbox"],
div[role="listbox"] {
    background: var(--app-surface) !important;
    color: var(--app-text) !important;
    border: 1px solid var(--ui-border) !important;
    border-radius: 10px !important;
}

li[role="option"] {
    color: var(--app-text) !important;
}

li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
    background: color-mix(in srgb, var(--app-primary) 14%, var(--app-surface)) !important;
}

/* ---------- Premium hero ---------- */
.hero {
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(circle at 90% 10%, color-mix(in srgb, var(--app-primary) 28%, transparent), transparent 34%),
        linear-gradient(135deg,
            color-mix(in srgb, var(--app-surface) 78%, var(--app-primary)),
            color-mix(in srgb, var(--app-bg) 74%, var(--app-primary)));
    padding: 38px 42px;
    border-radius: 20px;
    margin-bottom: 28px;
    border: 1px solid var(--ui-border);
    box-shadow: var(--ui-shadow);
}

.hero::after {
    content: "";
    position: absolute;
    width: 190px;
    height: 190px;
    right: -70px;
    bottom: -90px;
    border-radius: 50%;
    background: color-mix(in srgb, var(--app-primary) 18%, transparent);
    filter: blur(2px);
}

.hero h1, .hero h2, .hero h3, .hero p {
    position: relative;
    z-index: 1;
}

.hero h1, .hero h2, .hero h3 {
    letter-spacing: -0.6px;
}

/* ---------- Cards ---------- */
.card,
.metric-card {
    background: var(--app-surface);
    color: var(--app-text);
    border: 1px solid var(--ui-border);
    border-radius: var(--ui-radius);
    box-shadow: 0 7px 24px rgba(0,0,0,.055);
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}

.card:hover,
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--ui-shadow);
    border-color: color-mix(in srgb, var(--app-primary) 32%, var(--ui-border));
}

.card {
    padding: 24px;
    margin-bottom: 18px;
}

.metric-card {
    padding: 22px 20px;
    min-height: 115px;
    text-align: center;
}

.metric-number {
    font-size: 30px;
    font-weight: 760;
    color: var(--app-primary) !important;
    margin-bottom: 6px;
}

.metric-label {
    color: var(--ui-muted) !important;
    font-size: 13px;
    font-weight: 650;
}

/* ---------- Native widgets ---------- */
div[data-baseweb="input"],
div[data-baseweb="select"],
textarea,
input {
    border-radius: 10px;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    border-radius: 10px !important;
}

.stButton > button {
    border-radius: 10px;
    min-height: 44px;
    font-weight: 650;
    border: 1px solid var(--ui-border);
    transition: transform .16s ease, box-shadow .16s ease, filter .16s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 22px rgba(0,0,0,.12);
    filter: brightness(1.03);
}

.stButton > button[kind="primary"] {
    box-shadow: 0 8px 24px color-mix(in srgb, var(--app-primary) 20%, transparent);
}

/* ---------- Metrics / tables / alerts ---------- */
div[data-testid="stMetric"] {
    border: 1px solid var(--ui-border);
    border-radius: 14px;
    padding: 15px 17px;
    background: color-mix(in srgb, var(--app-surface) 88%, transparent);
}

div[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid var(--ui-border);
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

hr {
    border: none;
    border-top: 1px solid var(--ui-border);
    margin: 24px 0;
}


/* ---------- Outfit recommendation visual cards ---------- */
.outfit-visual {
    border: 1px solid var(--ui-border);
    border-radius: 18px;
    overflow: hidden;
    background: var(--app-surface);
    box-shadow: 0 12px 34px rgba(0,0,0,.10);
    margin-bottom: 18px;
}
.outfit-visual img {
    width: 100%;
    display: block;
}
.outfit-copy {
    padding: 18px 20px 20px;
}
.outfit-copy .eyebrow {
    color: var(--app-primary);
    font-size: .78rem;
    font-weight: 750;
    text-transform: uppercase;
    letter-spacing: .08em;
}
.outfit-copy h3 {
    margin: 6px 0 6px;
}
.outfit-copy p {
    margin: 0;
    color: var(--ui-muted) !important;
    line-height: 1.65;
}

/* ---------- Authentication ---------- */
.auth-page {
    max-width: 980px;
    margin: 0 auto;
    padding: 18px 18px 44px;
}

.auth-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 28px;
    margin: 8px 0 30px;
}

.auth-heading h1 {
    margin: 0 !important;
    font-size: clamp(2rem, 4vw, 3.15rem);
    line-height: 1.12;
    letter-spacing: -1px;
}

.auth-heading p {
    margin: 10px 0 0 !important;
    color: var(--ui-muted) !important;
    font-size: .98rem;
    line-height: 1.65;
}

.auth-language {
    width: 190px;
    flex: 0 0 190px;
}

.auth-form {
    max-width: 560px;
    margin: 0 auto;
}

/* Give authentication controls a clean product-like rhythm. */
.auth-page .stTextInput,
.auth-page .stSelectbox,
.auth-page .stButton,
.auth-page .stAlert {
    margin-bottom: 10px;
}

@media (max-width: 768px) {
    [data-testid="stMainBlockContainer"] {
        padding-left: .8rem;
        padding-right: .8rem;
        padding-top: 1rem;
    }

    .auth-page {
        padding: 8px 8px 28px;
    }

    .auth-header {
        display: block;
        margin-top: 4px;
        margin-bottom: 22px;
    }

    .auth-heading h1 {
        font-size: clamp(1.85rem, 9vw, 2.5rem);
    }

    .auth-heading p {
        font-size: .9rem;
    }

    .auth-language {
        width: 100%;
        max-width: 320px;
        margin-top: 16px;
    }

    .auth-form {
        max-width: 100%;
    }

    .hero {
        padding: 25px 22px;
        border-radius: 15px;
    }

    .hero h1 {
        font-size: 27px;
    }

    .card {
        padding: 18px;
    }
}

@media (max-width: 480px) {
    section[data-testid="stSidebar"] .block-container {
        padding-left: .7rem;
        padding-right: .7rem;
    }

    .metric-card {
        min-height: 95px;
        padding: 17px 12px;
    }

    .metric-number {
        font-size: 25px;
    }
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "forgot_step" not in st.session_state:
    st.session_state.forgot_step = 0
if "language" not in st.session_state:
    st.session_state.language = "English"

# --------------------------------------------------
# EXTRA UI TRANSLATIONS
# --------------------------------------------------

def ui_text(key, language):
    labels = {
        "English": {
            "navigation": "Navigation",
            "system_overview": "System Overview",
            "test_accuracy": "Test Accuracy",
            "outfit_categories": "Outfit Categories",
            "weather_conditions": "Weather Conditions",
            "temperature_analysis": "Temperature Analysis",
            "average": "Average",
            "lowest": "Lowest",
            "highest": "Highest",
            "recent_recommendations": "Recent Recommendations",
            "account": "Account",
            "created": "Created",
            "activity": "Activity",
            "role": "Role",
            "users": "Users",
            "user_management": "User Management",
            "manage_roles": "Manage User Roles",
            "algorithm": "Algorithm",
            "trees": "Trees",
            "dataset": "Dataset",
            "administrator_required": "Administrator access is required.",
            "model_active": "The trained Machine Learning model is active.",
            "no_users": "No users registered in the system.",
            "recent_activity": "Recent Recommendation Activity",
            "location": "Location",
            "favorite_rate": "Favorite Rate",
            "recent_activity_title": "Recent Activity",
            "system_workflow": "System Workflow",
            "model_status": "Model Status",
            "active": "Active",
            "quick_access": "Quick Access",
            "generate_recommendation": "Generate Recommendation",
            "view_history": "View History",
            "view_favorites": "View Favorites",
            "city": "City",
            "get_live_weather": "Get Live Weather",
            "live_weather": "Live Weather",
            "weather_loaded": "Live weather loaded successfully.",
            "weather_error": "Could not retrieve weather data. Check the city name or your internet connection.",
            "weather_source": "Weather Source",
            "open_meteo": "Open-Meteo",
            "outfit_details": "Outfit Details",
            "upper_body": "Upper Body",
            "lower_body": "Lower Body",
            "footwear": "Footwear",
            "outer_layer": "Outer Layer",
            "why_recommended": "Why This Recommendation?",
            "weather_basis": "Weather Basis",
            "world_map": "World Weather Map",
            "weather_charts": "Weather Analysis",
            "temperature_forecast": "24-Hour Temperature",
            "humidity_forecast": "24-Hour Humidity",
            "wind_forecast": "24-Hour Wind Speed",
            "precipitation_forecast": "24-Hour Precipitation",
            "weather_3d": "3D Weather Analysis",
            "coordinates": "Coordinates",
            "timezone": "Time Zone",
            "city_examples": "Try a city",
            "forecast_unavailable": "Forecast data is not available yet.",
            "city_found": "Location found",
            "search_cities": "Search Cities",
            "select_city": "Select City",
            "city_results": "Matching Cities",
            "load_selected_weather": "Load Selected City Weather",
            "city_selected": "Selected location",
            "no_city_results": "No matching cities found.",
        },
        "دری": {
            "navigation": "جهت‌یابی",
            "system_overview": "نمای کلی سیستم",
            "test_accuracy": "دقت آزمایشی",
            "outfit_categories": "دسته‌بندی لباس‌ها",
            "weather_conditions": "شرایط آب‌وهوا",
            "temperature_analysis": "تحلیل دما",
            "average": "میانگین",
            "lowest": "کمترین",
            "highest": "بیشترین",
            "recent_recommendations": "پیشنهادهای اخیر",
            "account": "حساب کاربری",
            "created": "تاریخ ایجاد",
            "activity": "فعالیت",
            "role": "نقش",
            "users": "کاربران",
            "user_management": "مدیریت کاربران",
            "manage_roles": "مدیریت نقش کاربران",
            "algorithm": "الگوریتم",
            "trees": "درخت‌ها",
            "dataset": "مجموعه داده",
            "administrator_required": "دسترسی مدیر لازم است.",
            "model_active": "مدل آموزش‌داده‌شده یادگیری ماشین فعال است.",
            "no_users": "هیچ کاربری در سیستم ثبت نشده است.",
            "recent_activity": "فعالیت اخیر پیشنهادها",
            "location": "موقعیت",
            "favorite_rate": "نرخ مورد علاقه",
            "recent_activity_title": "فعالیت اخیر",
            "system_workflow": "روند کاری سیستم",
            "model_status": "وضعیت مدل",
            "active": "فعال",
            "quick_access": "دسترسی سریع",
            "generate_recommendation": "ایجاد پیشنهاد جدید",
            "view_history": "مشاهده تاریخچه",
            "view_favorites": "مشاهده مورد علاقه‌ها",
            "city": "شهر",
            "get_live_weather": "دریافت آب‌وهوای فعلی",
            "live_weather": "آب‌وهوای فعلی",
            "weather_loaded": "اطلاعات آب‌وهوای فعلی با موفقیت دریافت شد.",
            "weather_error": "دریافت اطلاعات هوا ممکن نشد. نام شهر یا اتصال اینترنت را بررسی کنید.",
            "weather_source": "منبع آب‌وهوا",
            "open_meteo": "Open-Meteo",
            "outfit_details": "جزئیات لباس",
            "upper_body": "لباس بالاتنه",
            "lower_body": "لباس پایین‌تنه",
            "footwear": "کفش",
            "outer_layer": "لایه بیرونی",
            "why_recommended": "چرا این پیشنهاد؟",
            "weather_basis": "مبنای آب‌وهوا",
            "world_map": "نقشه جهانی آب‌وهوا",
            "weather_charts": "تحلیل آب‌وهوا",
            "temperature_forecast": "دمای ۲۴ ساعت آینده",
            "humidity_forecast": "رطوبت ۲۴ ساعت آینده",
            "wind_forecast": "سرعت باد در ۲۴ ساعت آینده",
            "precipitation_forecast": "بارندگی ۲۴ ساعت آینده",
            "weather_3d": "تحلیل سه‌بعدی آب‌وهوا",
            "coordinates": "مختصات",
            "timezone": "منطقه زمانی",
            "city_examples": "یک شهر را امتحان کنید",
            "forecast_unavailable": "اطلاعات پیش‌بینی هنوز در دسترس نیست.",
            "city_found": "موقعیت پیدا شد",
            "search_cities": "جستجوی شهرها",
            "select_city": "انتخاب شهر",
            "city_results": "شهرهای مطابق",
            "load_selected_weather": "دریافت آب‌وهوای شهر انتخاب‌شده",
            "city_selected": "موقعیت انتخاب‌شده",
            "no_city_results": "هیچ شهر مطابق پیدا نشد.",
        },
        "پښتو": {
            "navigation": "لارښود",
            "system_overview": "د سیستم عمومي کتنه",
            "test_accuracy": "ازمایښتي دقت",
            "outfit_categories": "د جامو کټګورۍ",
            "weather_conditions": "د هوا شرایط",
            "temperature_analysis": "د تودوخې تحلیل",
            "average": "اوسط",
            "lowest": "تر ټولو ټیټه",
            "highest": "تر ټولو لوړه",
            "recent_recommendations": "وروستي وړاندیزونه",
            "account": "حساب",
            "created": "د جوړېدو نېټه",
            "activity": "فعالیت",
            "role": "رول",
            "users": "کاروونکي",
            "user_management": "د کاروونکو مدیریت",
            "manage_roles": "د کاروونکو د رولونو مدیریت",
            "algorithm": "الګوریتم",
            "trees": "ونې",
            "dataset": "ډاټاسیټ",
            "administrator_required": "د مدیر لاسرسی اړین دی.",
            "model_active": "روزل شوی د ماشین زده‌کړې ماډل فعال دی.",
            "no_users": "په سیستم کې هېڅ کارن ثبت شوی نه دی.",
            "recent_activity": "د وړاندیزونو وروستی فعالیت",
            "location": "ځای",
            "favorite_rate": "د خوښې کچه",
            "recent_activity_title": "وروستی فعالیت",
            "system_workflow": "د سیستم کاري بهیر",
            "model_status": "د ماډل حالت",
            "active": "فعال",
            "quick_access": "چټک لاسرسی",
            "generate_recommendation": "نوی وړاندیز جوړول",
            "view_history": "تاریخچه کتل",
            "view_favorites": "خوښې کتل",
            "city": "ښار",
            "get_live_weather": "اوسنۍ هوا ترلاسه کول",
            "live_weather": "اوسنۍ هوا",
            "weather_loaded": "د اوسني هوا معلومات په بریالیتوب ترلاسه شول.",
            "weather_error": "د هوا معلومات ترلاسه نه شول. د ښار نوم یا انټرنېټ اړیکه وګورئ.",
            "weather_source": "د هوا سرچینه",
            "open_meteo": "Open-Meteo",
            "outfit_details": "د جامو جزیات",
            "world_map": "د نړۍ د هوا نقشه",
            "weather_charts": "د هوا تحلیل",
            "temperature_forecast": "د ۲۴ ساعتونو تودوخه",
            "humidity_forecast": "د ۲۴ ساعتونو رطوبت",
            "wind_forecast": "د ۲۴ ساعتونو باد سرعت",
            "precipitation_forecast": "د ۲۴ ساعتونو ورښت",
            "weather_3d": "د هوا درې‌بعدي تحلیل",
            "coordinates": "مختصات",
            "timezone": "وخت زون",
            "city_examples": "یو ښار وازمویئ",
            "forecast_unavailable": "د وړاندوینې معلومات لا تر اوسه نشته.",
            "city_found": "ځای وموندل شو",
            "search_cities": "ښارونه لټول",
            "select_city": "ښار وټاکئ",
            "city_results": "موندل شوي ښارونه",
            "load_selected_weather": "د ټاکل شوي ښار هوا ترلاسه کول",
            "city_selected": "ټاکل شوی ځای",
            "no_city_results": "د دې نوم سره هېڅ ښار ونه موندل شو.",
            "upper_body": "د بدن پاسنۍ برخه",
            "lower_body": "د بدن لاندینۍ برخه",
            "footwear": "بوټان",
            "outer_layer": "بهرنۍ طبقه",
            "why_recommended": "ولې دا وړاندیز؟",
            "weather_basis": "د هوا بنسټ",
        },
    }
    return labels.get(language, labels["English"]).get(key, key)


def security_questions_for(language):
    questions = {
        "English": [
            "What is your favorite city?",
            "What was the name of your first school?",
            "What is your father's name?",
            "What was your first pet's name?",
        ],
        "دری": [
            "شهر مورد علاقه شما چیست؟",
            "نام اولین مکتب شما چه بود؟",
            "نام پدر شما چیست؟",
            "نام اولین حیوان خانگی شما چه بود؟",
        ],
        "پښتو": [
            "ستاسو د خوښې ښار کوم دی؟",
            "ستاسو د لومړي ښوونځي نوم څه و؟",
            "ستاسو د پلار نوم څه دی؟",
            "ستاسو د لومړي کورني حیوان نوم څه و؟",
        ],
    }
    return questions.get(language, questions["English"])


# --------------------------------------------------
# AUTHENTICATION LANGUAGE SELECTOR
# --------------------------------------------------

def auth_language_selector():
    """Language selector available before login/register/forgot-password."""
    languages = ["English", "دری", "پښتو"]

    if st.session_state.language not in languages:
        st.session_state.language = "English"

    # Keep the selector compact and aligned with the authentication header.
    _, language_col = st.columns([5.6, 1.8])
    with language_col:
        st.markdown(
            '<div class="language-selector-label">🌐 Language</div>',
            unsafe_allow_html=True
        )
        selected = st.selectbox(
            "Language",
            languages,
            index=languages.index(st.session_state.language),
            key="auth_language_selector",
            label_visibility="collapsed"
        )

    if selected != st.session_state.language:
        st.session_state.language = selected
        st.session_state.lang = selected
        st.rerun()


# --------------------------------------------------
# AUTHENTICATION HEADER
# --------------------------------------------------

def auth_header(title_key, subtitle_key):
    """Responsive authentication header with language selector."""
    languages = ["English", "دری", "پښتو"]

    if st.session_state.language not in languages:
        st.session_state.language = "English"

    lang = st.session_state.language

    st.markdown('<div class="auth-page">', unsafe_allow_html=True)

    header_left, header_right = st.columns([4.2, 1.5], gap="large")

    with header_left:
        st.markdown(
            '<div class="auth-heading">'
            f'<h1>{translate(title_key, lang)}</h1>'
            f'<p>{translate(subtitle_key, lang)}</p>'
            '</div>',
            unsafe_allow_html=True
        )

    with header_right:
        st.markdown('<div class="auth-language">', unsafe_allow_html=True)
        st.markdown(
            '<div class="language-selector-label">🌐 Language</div>',
            unsafe_allow_html=True
        )
        selected = st.selectbox(
            "Language",
            languages,
            index=languages.index(lang),
            key="auth_language_selector",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if selected != lang:
        st.session_state.language = selected
        st.session_state.lang = selected
        st.rerun()

    st.markdown('<div class="auth-form">', unsafe_allow_html=True)
    return lang


def auth_footer_close():
    st.markdown('</div></div>', unsafe_allow_html=True)


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

def login_page():

    lang = auth_header("welcome_back", "login_subtitle")

    if st.session_state.get("reset_success", False):
        st.success(translate("password_reset", lang))
        st.session_state.reset_success = False

    col1, col2, col3 = st.columns([1, 1.4, 1])

    with col2:

        username = st.text_input(
            translate("username", lang),
            placeholder=translate("enter_username", lang),
            key="login_username"
        )

        password = st.text_input(
            translate("password", lang),
            type="password",
            placeholder=translate("enter_password", lang),
            key="login_password"
        )

        if st.button(
            translate("login", lang),
            width="stretch",
            type="primary"
        ):
            if not username or not password:
                st.error(translate("fill_login", lang))
            else:
                user = authenticate_user(username, password)

                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username.strip()
                    st.rerun()
                else:
                    st.error(translate("invalid_login", lang))

        st.write("")

        if st.button(
            translate("forgot_password", lang),
            width="stretch"
        ):
            st.session_state.auth_mode = "forgot"
            st.session_state.forgot_step = 0
            st.rerun()

        st.write("")

        if st.button(
            translate("create_account", lang),
            width="stretch"
        ):
            st.session_state.auth_mode = "register"
            st.rerun()

    auth_footer_close()

def forgot_password_page():

    lang = auth_header("forgot_title", "forgot_subtitle")

    col1, col2, col3 = st.columns([1, 1.4, 1])

    with col2:

        if st.session_state.get("forgot_step", 0) == 0:

            username = st.text_input(
                translate("username", lang),
                placeholder=translate("enter_username", lang),
                key="forgot_username_input"
            )

            if st.button(
                translate("find_account", lang),
                width="stretch",
                type="primary"
            ):
                if not username.strip():
                    st.error(translate("fill_login", lang))
                else:
                    question_id = get_security_question(username.strip())

                    if question_id is None:
                        st.error(translate("account_not_found", lang))
                    else:
                        st.session_state.forgot_username = username.strip()
                        st.session_state.forgot_question_id = question_id
                        st.session_state.forgot_step = 2
                        st.rerun()

        elif st.session_state.get("forgot_step") == 2:

            questions = security_questions_for(lang)
            question_id = st.session_state.get("forgot_question_id")

            if question_id is not None and 0 <= question_id < len(questions):
                st.info(questions[question_id])

                answer = st.text_input(
                    translate("security_answer", lang),
                    key="forgot_security_answer"
                )

                if st.button(
                    translate("verify_answer", lang),
                    width="stretch",
                    type="primary"
                ):
                    valid = verify_security_answer(
                        st.session_state.forgot_username,
                        answer
                    )

                    if valid:
                        st.session_state.forgot_step = 3
                        st.rerun()
                    else:
                        st.error(translate("incorrect_answer", lang))

        elif st.session_state.get("forgot_step") == 3:

            new_password = st.text_input(
                translate("new_password", lang),
                type="password",
                key="forgot_new_password"
            )

            confirm_password = st.text_input(
                translate("confirm_new_password", lang),
                type="password",
                key="forgot_confirm_password"
            )

            if st.button(
                translate("reset_password", lang),
                width="stretch",
                type="primary"
            ):
                if len(new_password) < 6:
                    st.error(translate("weak_password", lang))

                elif new_password != confirm_password:
                    st.error(translate("password_mismatch", lang))

                else:
                    success = reset_password(
                        st.session_state.forgot_username,
                        new_password
                    )

                    if success:
                        st.session_state.reset_success = True
                        st.session_state.forgot_step = 0
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error(translate("reset_failed", lang))

        st.write("")

        if st.button(
            translate("back_to_login", lang),
            width="stretch"
        ):
            st.session_state.forgot_step = 0
            st.session_state.auth_mode = "login"
            st.rerun()

    auth_footer_close()

def register_page():

    lang = auth_header("create_your_account", "register_subtitle")

    col1, col2, col3 = st.columns([1, 1.4, 1])

    with col2:

        username = st.text_input(
            translate("username", lang),
            placeholder=translate("username", lang),
            key="register_username"
        )

        password = st.text_input(
            translate("password", lang),
            type="password",
            placeholder=translate("password_minimum", lang),
            key="register_password"
        )

        confirm_password = st.text_input(
            translate("confirm_password", lang),
            type="password",
            placeholder=translate("confirm_password", lang),
            key="register_confirm_password"
        )

        questions = security_questions_for(lang)

        question = st.selectbox(
            translate("security_question", lang),
            questions,
            key="register_security_question"
        )

        answer = st.text_input(
            translate("security_answer", lang),
            key="register_security_answer"
        )

        if st.button(
            translate("create_account_button", lang),
            width="stretch",
            type="primary"
        ):

            username = username.strip()
            answer = answer.strip()
            question_id = questions.index(question)

            if not username or not password or not confirm_password:
                st.error(translate("fill_login", lang))

            elif not answer:
                st.error(translate("security_answer", lang))

            elif len(password) < 6:
                st.error(translate("weak_password", lang))

            elif password != confirm_password:
                st.error(translate("password_mismatch", lang))

            else:
                success, message = create_user(
                    username,
                    password,
                    question_id,
                    answer
                )

                if success:
                    st.success(translate("account_created", lang))
                    st.session_state.auth_mode = "login"
                    st.rerun()

                elif message == "username_taken":
                    st.error(translate("username_exists", lang))

                elif message == "weak_password":
                    st.error(translate("weak_password", lang))

                else:
                    st.error("Could not create the account.")

        st.write("")

        if st.button(
            translate("back_to_login", lang),
            width="stretch"
        ):
            st.session_state.auth_mode = "login"
            st.rerun()

    auth_footer_close()

def sidebar():

    user = get_user(st.session_state.username)

    # Keep one canonical language value everywhere in the app.
    languages = ["English", "دری", "پښتو"]

    if st.session_state.language not in languages:
        st.session_state.language = "English"

    language = st.sidebar.selectbox(
        "🌐 Language",
        languages,
        index=languages.index(st.session_state.language),
        key="language_selector"
    )

    st.session_state.language = language
    st.session_state.lang = language

    st.sidebar.markdown("## AI Outfit System")
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 **{st.session_state.username}**")
    st.sidebar.markdown("---")

    nav = {
        "dashboard": translate("dashboard", language),
        "weather": translate("weather_recommendation", language),
        "history": translate("history", language),
        "favorites": translate("favorites", language),
        "statistics": translate("statistics", language),
        "profile": translate("profile", language),
    }

    if user and user.get("role") == "admin":
        nav["admin"] = translate("admin_dashboard", language)

    page_label = st.sidebar.radio(
        translate("dashboard", language).split(" ")[-1] if False else "Navigation",
        list(nav.values()),
        key="main_navigation"
    )

    reverse_nav = {label: key for key, label in nav.items()}

    st.sidebar.markdown("---")

    if st.sidebar.button(
        translate("logout", language),
        width="stretch"
    ):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.auth_mode = "login"
        st.rerun()

    return reverse_nav[page_label]

def dashboard():

    lang = st.session_state.language

    user = get_user(st.session_state.username)

    if user is None:
        st.error(translate("user_not_found", lang))
        return

    recommendations = get_user_recommendations(user["id"])
    favorites = get_user_favorites(user["id"])

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------

    st.markdown(
        f"## {translate('welcome_dashboard', lang)}, {user['username']}"
    )
    st.caption(translate("dashboard_description", lang))

    # --------------------------------------------------
    # OVERVIEW
    # --------------------------------------------------

    st.markdown("---")
    st.subheader(ui_text("system_overview", lang))

    total_recommendations = len(recommendations)
    total_favorites = len(favorites)
    favorite_rate = (
        (total_favorites / total_recommendations) * 100
        if total_recommendations else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            translate("recommendations", lang),
            total_recommendations
        )

    with col2:
        st.metric(
            translate("favorite_outfits", lang),
            total_favorites
        )

    with col3:
        st.metric(
            ui_text("favorite_rate", lang),
            f"{favorite_rate:.1f}%"
        )

    with col4:
        st.metric(
            ui_text("test_accuracy", lang),
            "91%"
        )

    # --------------------------------------------------
    # MODEL STATUS
    # --------------------------------------------------

    st.markdown("---")
    st.subheader(ui_text("model_status", lang))

    col1, col2 = st.columns([2, 1])

    with col1:
        st.success(
            f"{ui_text('active', lang)} — Random Forest"
        )
        st.write(
            f"{ui_text('algorithm', lang)}: Random Forest | "
            f"{ui_text('trees', lang)}: 200 | "
            f"{ui_text('dataset', lang)}: 1500"
        )

    with col2:
        st.metric(
            ui_text("test_accuracy", lang),
            "91%"
        )

    # --------------------------------------------------
    # WORKFLOW
    # --------------------------------------------------

    st.markdown("---")
    st.subheader(ui_text("system_workflow", lang))

    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(border=True):
            st.markdown(f"**01 — {translate('weather_data', lang)}**")
            st.write(translate("weather_data_description", lang))

    with c2:
        with st.container(border=True):
            st.markdown(f"**02 — {translate('machine_learning', lang)}**")
            st.write(translate("ml_description", lang))

    with c3:
        with st.container(border=True):
            st.markdown(f"**03 — {translate('outfit_recommendation', lang)}**")
            st.write(translate("outfit_description", lang))

    # --------------------------------------------------
    # ACTIVITY
    # --------------------------------------------------

    st.markdown("---")
    st.subheader(ui_text("recent_activity_title", lang))

    if total_recommendations > 0:
        st.bar_chart(
            {
                translate("recommendations", lang): [total_recommendations],
                translate("favorite_outfits", lang): [total_favorites]
            }
        )
    else:
        st.info(translate("no_history", lang))

    # --------------------------------------------------
    # RECENT RECOMMENDATIONS
    # --------------------------------------------------

    st.subheader(translate("recommendations", lang))

    if recommendations:

        outfit_key_map = {
            "Heavy Winter Outfit": "heavy_winter_outfit",
            "Formal Winter Outfit": "formal_winter_outfit",
            "Winter Outfit": "winter_outfit",
            "Hot Weather Outfit": "hot_weather_outfit",
            "Light Summer Outfit": "light_summer_outfit",
            "Light Winter Outfit": "light_winter_outfit",
            "Rainy Cold Outfit": "rainy_cold_outfit",
            "Rainy Light Outfit": "rainy_light_outfit",
            "Sport Summer Outfit": "sport_summer_outfit",
            "Sport Winter Outfit": "sport_winter_outfit",
            "Spring Autumn Outfit": "spring_autumn_outfit",
        }

        recommendation_key_map = {
            "Heavy Winter Outfit": "heavy_winter_desc",
            "Formal Winter Outfit": "formal_winter_desc",
            "Winter Outfit": "winter_desc",
            "Hot Weather Outfit": "hot_weather_desc",
            "Light Summer Outfit": "light_summer_desc",
            "Light Winter Outfit": "light_winter_desc",
            "Rainy Cold Outfit": "rainy_cold_desc",
            "Rainy Light Outfit": "rainy_light_desc",
            "Sport Summer Outfit": "sport_summer_desc",
            "Sport Winter Outfit": "sport_winter_desc",
            "Spring Autumn Outfit": "spring_autumn_desc",
        }

        for item in recommendations[:5]:

            category = item.get("outfit_category", "Unknown")
            outfit_key = outfit_key_map.get(category)
            desc_key = recommendation_key_map.get(category)

            title = (
                translate(outfit_key, lang)
                if outfit_key else category
            )

            description = (
                translate(desc_key, lang)
                if desc_key
                else item.get("recommendation", "")
            )

            with st.container(border=True):

                st.markdown(f"### {title}")

                col_a, col_b, col_c = st.columns(3)

                with col_a:
                    st.write(
                        f"**{ui_text('location', lang)}:** "
                        f"{item.get('city', 'Unknown')}"
                    )

                with col_b:
                    st.write(
                        f"**{translate('temperature', lang)}:** "
                        f"{item.get('temperature', 'N/A')} °C"
                    )

                with col_c:
                    st.write(
                        f"**{translate('humidity', lang)}:** "
                        f"{item.get('humidity', 'N/A')}%"
                    )

                st.write(description)

    # --------------------------------------------------
    # QUICK ACCESS
    # --------------------------------------------------

    st.markdown("---")
    st.subheader(ui_text("quick_access", lang))

    st.info(
        f"{translate('weather_recommendation', lang)} → "
        f"{ui_text('generate_recommendation', lang)}"
    )

    st.info(
        f"{translate('history', lang)} → "
        f"{ui_text('view_history', lang)}"
    )

    st.info(
        f"{translate('favorites', lang)} → "
        f"{ui_text('view_favorites', lang)}"
    )

def search_cities(city):
    """Return geocoding candidates so the user can explicitly choose the city."""
    city = city.strip()
    if not city:
        return []

    try:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 10,
                "language": "en",
                "format": "json"
            },
            timeout=10
        )
        response.raise_for_status()
        results = response.json().get("results", [])

        # Put exact name matches first. The user still chooses the final
        # location, which prevents ambiguous names such as Beijing.
        results.sort(
            key=lambda r: (
                str(r.get("name", "")).lower() != city.lower(),
                str(r.get("feature_code", "")) != "PPLC",
                str(r.get("country", ""))
            )
        )
        return results
    except (requests.RequestException, ValueError, TypeError):
        return []


def get_weather_for_place(place):
    """Fetch current and 24-hour weather for a selected geocoding result."""
    try:
        latitude = float(place["latitude"])
        longitude = float(place["longitude"])

        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,relative_humidity_2m,"
                    "precipitation,rain,weather_code,wind_speed_10m"
                ),
                "hourly": (
                    "temperature_2m,relative_humidity_2m,"
                    "precipitation,wind_speed_10m,weather_code"
                ),
                "forecast_days": 2,
                "timezone": "auto"
            },
            timeout=10
        )
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        current = weather_data.get("current", {})
        hourly = weather_data.get("hourly", {})

        if not current:
            return None, "no_data"

        times = hourly.get("time", [])[:24]
        forecast = {
            "time": times,
            "temperature": hourly.get("temperature_2m", [])[:24],
            "humidity": hourly.get("relative_humidity_2m", [])[:24],
            "precipitation": hourly.get("precipitation", [])[:24],
            "wind_speed": hourly.get("wind_speed_10m", [])[:24],
            "weather_code": hourly.get("weather_code", [])[:24],
        }

        return {
            "city": place.get("name", ""),
            "country": place.get("country", ""),
            "country_code": place.get("country_code", ""),
            "admin1": place.get("admin1", ""),
            "latitude": latitude,
            "longitude": longitude,
            "timezone": weather_data.get("timezone", ""),
            "temperature": float(current.get("temperature_2m", 20)),
            "humidity": int(current.get("relative_humidity_2m", 50)),
            "wind_speed": float(current.get("wind_speed_10m", 10)),
            "rain": float(current.get("rain", 0)),
            "precipitation": float(current.get("precipitation", 0)),
            "weather_code": int(current.get("weather_code", 0)),
            "forecast": forecast,
        }, None

    except (requests.RequestException, ValueError, KeyError, TypeError):
        return None, "request_error"


def season_from_month(month):
    """Convert a calendar month to the season labels used by the ML dataset."""
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"
    return "Autumn"


def weather_condition_from_code(code):
    """Map Open-Meteo WMO weather codes to the ML condition labels."""
    try:
        code = int(code)
    except (TypeError, ValueError):
        return "Clear"

    if code == 0:
        return "Clear"
    if code in (1, 2, 3):
        return "Cloudy"
    if code in (45, 48):
        return "Cloudy"
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        return "Rainy"
    if code in (71, 73, 75, 77, 85, 86):
        return "Snowy"
    if code in (95, 96, 99):
        return "Stormy"
    return "Clear"


def get_live_weather(city):
    """Backward-compatible helper: use the first exact geocoding result."""
    results = search_cities(city)
    if not results:
        return None, "not_found"
    exact = next(
        (r for r in results if str(r.get("name", "")).lower() == city.strip().lower()),
        results[0]
    )
    return get_weather_for_place(exact)


def outfit_details(
    prediction,
    temperature,
    humidity,
    wind_speed,
    rain,
    condition,
    occasion,
    style,
    lang
):
    """Build a clear, multilingual explanation of the predicted outfit.

    This is a presentation layer around the trained model prediction. It does
    not replace the Random Forest model; it explains the predicted category in
    a user-friendly way.
    """

    base = {
        "Heavy Winter Outfit": {
            "upper": {
                "English": "Thermal shirt and a warm sweater",
                "دری": "پیراهن حرارتی و سویتر گرم",
                "پښتو": "حرارتي کمیس او ګرم سویټر",
            },
            "lower": {
                "English": "Warm long trousers",
                "دری": "پتلون بلند و گرم",
                "پښتو": "ګرم اوږد پتلون",
            },
            "footwear": {
                "English": "Insulated winter shoes or boots",
                "دری": "کفش یا بوت زمستانی عایق",
                "پښتو": "د ژمي عایق لرونکي بوټان",
            },
            "outer": {
                "English": "Heavy winter coat",
                "دری": "کاپشن یا پالتوی ضخیم زمستانی",
                "پښتو": "دروند ژمنی کوټ",
            },
        },
        "Formal Winter Outfit": {
            "upper": {
                "English": "Formal shirt with a warm sweater",
                "دری": "پیراهن رسمی همراه با سویتر گرم",
                "پښتو": "رسمي کمیس له ګرم سویټر سره",
            },
            "lower": {
                "English": "Formal trousers",
                "دری": "پتلون رسمی",
                "پښتو": "رسمي پتلون",
            },
            "footwear": {
                "English": "Closed formal shoes",
                "دری": "کفش رسمی بسته",
                "پښتو": "بند رسمي بوټان",
            },
            "outer": {
                "English": "Formal winter coat",
                "دری": "پالتوی رسمی زمستانی",
                "پښتو": "رسمي ژمنی کوټ",
            },
        },
        "Winter Outfit": {
            "upper": {
                "English": "Warm sweater or long-sleeve shirt",
                "دری": "سویتر گرم یا پیراهن آستین‌بلند",
                "پښتو": "ګرم سویټر یا اوږده لستوڼي کمیس",
            },
            "lower": {
                "English": "Long trousers",
                "دری": "پتلون بلند",
                "پښتو": "اوږد پتلون",
            },
            "footwear": {
                "English": "Warm closed shoes",
                "دری": "کفش بسته و گرم",
                "پښتو": "ګرم بند بوټان",
            },
            "outer": {
                "English": "Warm jacket or coat",
                "دری": "جاکت یا پالتوی گرم",
                "پښتو": "ګرم جاکټ یا کوټ",
            },
        },
        "Hot Weather Outfit": {
            "upper": {
                "English": "Breathable T-shirt or light shirt",
                "دری": "تی‌شرت یا پیراهن سبک و قابل‌تنفس",
                "پښتو": "سپک او د هوا تېرېدونکی کمیس یا ټي‌شرټ",
            },
            "lower": {
                "English": "Light trousers or shorts",
                "دری": "پتلون سبک یا شورت",
                "پښتو": "سپک پتلون یا شارټ",
            },
            "footwear": {
                "English": "Comfortable breathable shoes",
                "دری": "کفش راحت و قابل‌تنفس",
                "پښتو": "هوسا او د هوا تېرېدونکي بوټان",
            },
            "outer": {
                "English": "No heavy outer layer",
                "دری": "به لایه بیرونی ضخیم نیاز نیست",
                "پښتو": "درنې بهرنۍ طبقې ته اړتیا نشته",
            },
        },
        "Light Summer Outfit": {
            "upper": {
                "English": "Light breathable shirt or T-shirt",
                "دری": "پیراهن یا تی‌شرت سبک و قابل‌تنفس",
                "پښتو": "سپک د هوا تېرېدونکی کمیس یا ټي‌شرټ",
            },
            "lower": {
                "English": "Light trousers or shorts",
                "دری": "پتلون سبک یا شورت",
                "پښتو": "سپک پتلون یا شارټ",
            },
            "footwear": {
                "English": "Light comfortable shoes",
                "دری": "کفش سبک و راحت",
                "پښتو": "سپک او هوسا بوټان",
            },
            "outer": {
                "English": "Optional light layer",
                "دری": "در صورت نیاز یک لایه سبک",
                "پښتو": "د اړتیا په صورت کې سپکه طبقه",
            },
        },
        "Light Winter Outfit": {
            "upper": {
                "English": "Long-sleeve shirt and sweater",
                "دری": "پیراهن آستین‌بلند و سویتر",
                "پښتو": "اوږده لستوڼي کمیس او سویټر",
            },
            "lower": {
                "English": "Long trousers",
                "دری": "پتلون بلند",
                "پښتو": "اوږد پتلون",
            },
            "footwear": {
                "English": "Closed comfortable shoes",
                "دری": "کفش بسته و راحت",
                "پښتو": "بند او هوسا بوټان",
            },
            "outer": {
                "English": "Light jacket",
                "دری": "جاکت سبک",
                "پښتو": "سپک جاکټ",
            },
        },
        "Rainy Cold Outfit": {
            "upper": {
                "English": "Warm inner layer",
                "دری": "لایه داخلی گرم",
                "پښتو": "ګرمه داخلي طبقه",
            },
            "lower": {
                "English": "Long trousers",
                "دری": "پتلون بلند",
                "پښتو": "اوږد پتلون",
            },
            "footwear": {
                "English": "Waterproof shoes or boots",
                "دری": "کفش یا بوت ضدآب",
                "پښتو": "د اوبو ضد بوټان یا بوتان",
            },
            "outer": {
                "English": "Waterproof warm jacket",
                "دری": "جاکت گرم و ضدآب",
                "پښتو": "ګرم د اوبو ضد جاکټ",
            },
        },
        "Rainy Light Outfit": {
            "upper": {
                "English": "Light shirt with a waterproof layer",
                "دری": "پیراهن سبک همراه با لایه ضدآب",
                "پښتو": "سپک کمیس له د اوبو ضد طبقې سره",
            },
            "lower": {
                "English": "Comfortable trousers",
                "دری": "پتلون راحت",
                "پښتو": "هوسا پتلون",
            },
            "footwear": {
                "English": "Water-resistant shoes",
                "دری": "کفش مقاوم در برابر آب",
                "پښتو": "د اوبو پر وړاندې مقاوم بوټان",
            },
            "outer": {
                "English": "Light waterproof jacket",
                "دری": "جاکت سبک ضدآب",
                "پښتو": "سپک د اوبو ضد جاکټ",
            },
        },
        "Sport Summer Outfit": {
            "upper": {
                "English": "Breathable sports T-shirt",
                "دری": "تی‌شرت ورزشی قابل‌تنفس",
                "پښتو": "د ورزش د هوا تېرېدونکی ټي‌شرټ",
            },
            "lower": {
                "English": "Sports shorts or light trousers",
                "دری": "شورت ورزشی یا پتلون سبک",
                "پښتو": "ورزشي شارټ یا سپک پتلون",
            },
            "footwear": {
                "English": "Light athletic shoes",
                "دری": "کفش ورزشی سبک",
                "پښتو": "سپک ورزشي بوټان",
            },
            "outer": {
                "English": "No heavy outer layer",
                "دری": "به لایه بیرونی ضخیم نیاز نیست",
                "پښتو": "درنې بهرنۍ طبقې ته اړتیا نشته",
            },
        },
        "Sport Winter Outfit": {
            "upper": {
                "English": "Warm sports base layer",
                "دری": "لایه داخلی گرم ورزشی",
                "پښتو": "د ورزش ګرمه داخلي طبقه",
            },
            "lower": {
                "English": "Warm sports trousers",
                "دری": "پتلون گرم ورزشی",
                "پښتو": "ګرم ورزشي پتلون",
            },
            "footwear": {
                "English": "Suitable athletic shoes",
                "دری": "کفش مناسب ورزشی",
                "پښتو": "مناسب ورزشي بوټان",
            },
            "outer": {
                "English": "Warm sports jacket",
                "دری": "جاکت گرم ورزشی",
                "پښتو": "ګرم ورزشي جاکټ",
            },
        },
        "Spring Autumn Outfit": {
            "upper": {
                "English": "Light shirt or sweater",
                "دری": "پیراهن سبک یا سویتر",
                "پښتو": "سپک کمیس یا سویټر",
            },
            "lower": {
                "English": "Comfortable trousers",
                "دری": "پتلون راحت",
                "پښتو": "هوسا پتلون",
            },
            "footwear": {
                "English": "Comfortable everyday shoes",
                "دری": "کفش راحت روزمره",
                "پښتو": "هوسا ورځني بوټان",
            },
            "outer": {
                "English": "Light jacket or cardigan",
                "دری": "جاکت سبک یا ژاکت بافتنی",
                "پښتو": "سپک جاکټ یا سویټر",
            },
        },
    }

    fallback = {
        "upper": {
            "English": "Comfortable weather-appropriate top",
            "دری": "لباس بالاتنه مناسب با آب‌وهوا",
            "پښتو": "د هوا سره مناسب د پاسنۍ برخې کالي",
        },
        "lower": {
            "English": "Comfortable trousers",
            "دری": "پتلون راحت",
            "پښتو": "هوسا پتلون",
        },
        "footwear": {
            "English": "Suitable comfortable shoes",
            "دری": "کفش مناسب و راحت",
            "پښتو": "مناسب او هوسا بوټان",
        },
        "outer": {
            "English": "A suitable outer layer if needed",
            "دری": "در صورت نیاز یک لایه بیرونی مناسب",
            "پښتو": "د اړتیا په صورت کې مناسبه بهرنۍ طبقه",
        },
    }

    selected = base.get(prediction, fallback)
    upper = selected["upper"].get(lang, selected["upper"]["English"])
    lower = selected["lower"].get(lang, selected["lower"]["English"])
    footwear = selected["footwear"].get(lang, selected["footwear"]["English"])
    outer = selected["outer"].get(lang, selected["outer"]["English"])

    adjustments = []
    if rain:
        adjustments.append("rain")
    if float(wind_speed) >= 25:
        adjustments.append("strong wind")
    if float(humidity) >= 75:
        adjustments.append("high humidity")
    if float(temperature) <= 10:
        adjustments.append("cold temperature")
    if float(temperature) >= 30:
        adjustments.append("hot temperature")

    basis_text = {
        "English": f"Based on {temperature:.1f}°C, {humidity:.0f}% humidity, {wind_speed:.1f} km/h wind, {condition} weather, {occasion} occasion and {style} style.",
        "دری": f"بر اساس دمای {temperature:.1f}°C، رطوبت {humidity:.0f}%، باد {wind_speed:.1f} کیلومتر در ساعت، هوای {condition}، مناسبت {occasion} و سبک {style}.",
        "پښتو": f"د {temperature:.1f}°C تودوخې، {humidity:.0f}% رطوبت، {wind_speed:.1f} km/h باد، {condition} هوا، {occasion} مناسبت او {style} سټایل پر بنسټ.",
    }

    return {
        "basis": basis_text.get(lang, basis_text["English"]),
        "upper": upper,
        "lower": lower,
        "footwear": footwear,
        "outer": outer,
        "adjustments": adjustments,
    }


def render_weather_visualizations(live_weather, lang):
    """Render the map, 24-hour charts and a compact 3D weather visualization."""

    if not live_weather:
        return

    st.markdown(f"### 🗺️ {ui_text('world_map', lang)}")

    location_df = pd.DataFrame([{
        "latitude": live_weather["latitude"],
        "longitude": live_weather["longitude"],
    }])
    st.map(location_df, latitude="latitude", longitude="longitude", zoom=7, use_container_width=True)

    map_info_col1, map_info_col2, map_info_col3 = st.columns(3)
    map_info_col1.metric(ui_text("location", lang), f"{live_weather['city']}, {live_weather['country']}")
    map_info_col2.metric(ui_text("coordinates", lang), f"{live_weather['latitude']:.2f}, {live_weather['longitude']:.2f}")
    map_info_col3.metric(ui_text("timezone", lang), live_weather.get("timezone", "—"))

    forecast = live_weather.get("forecast", {})
    times = forecast.get("time", [])
    if not times:
        st.info(ui_text("forecast_unavailable", lang))
        return

    n = min(len(times), len(forecast.get("temperature", [])), len(forecast.get("humidity", [])), len(forecast.get("wind_speed", [])), len(forecast.get("precipitation", [])))
    if n == 0:
        st.info(ui_text("forecast_unavailable", lang))
        return

    chart_df = pd.DataFrame({
        "time": pd.to_datetime(times[:n]),
        "temperature": forecast["temperature"][:n],
        "humidity": forecast["humidity"][:n],
        "wind": forecast["wind_speed"][:n],
        "precipitation": forecast["precipitation"][:n],
    })

    st.markdown(f"### 📊 {ui_text('weather_charts', lang)}")

    c1, c2 = st.columns(2)
    with c1:
        fig_temp = px.line(chart_df, x="time", y="temperature", markers=True, title=ui_text("temperature_forecast", lang))
        fig_temp.update_layout(height=330, margin=dict(l=10, r=10, t=55, b=10), yaxis_title="°C", xaxis_title="")
        st.plotly_chart(fig_temp, use_container_width=True)
    with c2:
        fig_humidity = px.line(chart_df, x="time", y="humidity", markers=True, title=ui_text("humidity_forecast", lang))
        fig_humidity.update_layout(height=330, margin=dict(l=10, r=10, t=55, b=10), yaxis_title="%", xaxis_title="")
        st.plotly_chart(fig_humidity, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig_wind = px.line(chart_df, x="time", y="wind", markers=True, title=ui_text("wind_forecast", lang))
        fig_wind.update_layout(height=330, margin=dict(l=10, r=10, t=55, b=10), yaxis_title="km/h", xaxis_title="")
        st.plotly_chart(fig_wind, use_container_width=True)
    with c4:
        fig_rain = px.bar(chart_df, x="time", y="precipitation", title=ui_text("precipitation_forecast", lang))
        fig_rain.update_layout(height=330, margin=dict(l=10, r=10, t=55, b=10), yaxis_title="mm", xaxis_title="")
        st.plotly_chart(fig_rain, use_container_width=True)

    st.markdown(f"### 🧊 {ui_text('weather_3d', lang)}")
    fig_3d = go.Figure(data=[go.Scatter3d(
        x=chart_df["temperature"],
        y=chart_df["humidity"],
        z=chart_df["wind"],
        mode="lines+markers",
        text=[t.strftime("%H:%M") for t in chart_df["time"]],
        hovertemplate="Time: %{text}<br>Temperature: %{x:.1f} °C<br>Humidity: %{y:.0f}%<br>Wind: %{z:.1f} km/h<extra></extra>",
    )])
    fig_3d.update_layout(
        height=520,
        margin=dict(l=0, r=0, t=20, b=0),
        scene=dict(
            xaxis_title="Temperature (°C)",
            yaxis_title="Humidity (%)",
            zaxis_title="Wind (km/h)",
        ),
    )
    st.plotly_chart(fig_3d, use_container_width=True)

def outfit_image_path(prediction):
    """Return a local recommendation image for the predicted category."""
    image_map = {
        "Heavy Winter Outfit": "winter.png",
        "Formal Winter Outfit": "formal.png",
        "Winter Outfit": "winter.png",
        "Hot Weather Outfit": "summer.png",
        "Light Summer Outfit": "summer.png",
        "Light Winter Outfit": "light.png",
        "Rainy Cold Outfit": "rainy.png",
        "Rainy Light Outfit": "rainy.png",
        "Sport Summer Outfit": "sport.png",
        "Sport Winter Outfit": "sport.png",
        "Spring Autumn Outfit": "light.png",
    }
    filename = image_map.get(prediction, "light.png")
    path = Path(__file__).parent / "assets" / "outfits" / filename
    return path if path.exists() else None


def weather_page():

    lang = st.session_state.language

    st.title(
        f"🌤️ {translate('weather_outfit_title', lang)}"
    )

    st.write(
        translate(
            "weather_outfit_description",
            lang
        )
    )

    # --------------------------------------------------
    # LIVE WEATHER
    # --------------------------------------------------

    st.markdown(
        f"### 🌍 {ui_text('live_weather', lang)}"
    )

    if "weather_city" not in st.session_state:
        st.session_state.weather_city = "Kabul"

    city = st.text_input(
        ui_text("city", lang),
        key="weather_city",
        placeholder=ui_text("city_examples", lang)
    )
    city = city.strip() or "Kabul"

    if st.button(
        f"🔎 {ui_text('search_cities', lang)}",
        width="stretch"
    ):
        candidates = search_cities(city)
        st.session_state.city_candidates = candidates
        st.session_state.city_query = city
        st.session_state.selected_city_index = 0
        if candidates:
            st.success(f"{ui_text('city_found', lang)}: {len(candidates)}")
            st.rerun()
        else:
            st.error(ui_text("no_city_results", lang))

    candidates = st.session_state.get("city_candidates", [])
    live_weather = st.session_state.get("live_weather")

    if candidates:
        labels = []
        for place in candidates:
            parts = [place.get("name", "")]
            if place.get("admin1") and place.get("admin1") != place.get("name"):
                parts.append(place.get("admin1"))
            if place.get("country"):
                parts.append(place.get("country"))
            labels.append(", ".join([p for p in parts if p]))

        selected_index = st.selectbox(
            ui_text("select_city", lang),
            range(len(candidates)),
            index=min(
                int(st.session_state.get("selected_city_index", 0)),
                len(candidates) - 1
            ),
            format_func=lambda i: labels[i],
            key="selected_city_result"
        )

        selected_place = candidates[selected_index]
        st.caption(
            f"{ui_text('city_selected', lang)}: {labels[selected_index]}"
        )

        if st.button(
            f"🌐 {ui_text('load_selected_weather', lang)}",
            type="primary",
            width="stretch"
        ):
            weather, error = get_weather_for_place(selected_place)
            if weather:
                st.session_state.live_weather = weather
                st.session_state.selected_city_index = selected_index
                st.session_state.weather_temperature = float(weather["temperature"])
                st.session_state.weather_humidity = int(weather["humidity"])
                st.session_state.weather_wind_speed = float(weather["wind_speed"])
                st.session_state.weather_rain = (
                    translate("yes", lang)
                    if weather["rain"] > 0
                    else translate("no", lang)
                )
                st.success(ui_text("weather_loaded", lang))
                st.rerun()
            else:
                st.error(ui_text("weather_error", lang))

    # --------------------------------------------------
    # WEATHER INPUTS
    # --------------------------------------------------

    st.markdown(
        f"### 🌡️ {translate('weather_information', lang)}"
    )

    col1, col2 = st.columns(2)

    with col1:

        temperature = st.number_input(
            translate("temperature", lang),
            min_value=-30.0,
            max_value=50.0,
            value=(
                float(live_weather["temperature"])
                if live_weather else 20.0
            ),
            step=1.0,
            key="weather_temperature"
        )

        humidity = st.slider(
            translate("humidity", lang),
            min_value=0,
            max_value=100,
            value=(
                int(live_weather["humidity"])
                if live_weather else 50
            ),
            key="weather_humidity"
        )

        wind_speed = st.number_input(
            translate("wind_speed", lang),
            min_value=0.0,
            max_value=150.0,
            value=(
                float(live_weather["wind_speed"])
                if live_weather else 10.0
            ),
            step=1.0,
            key="weather_wind_speed"
        )

        rain_options = [
            translate("no", lang),
            translate("yes", lang)
        ]

        default_rain = (
            translate("yes", lang)
            if live_weather and live_weather["rain"] > 0
            else translate("no", lang)
        )

        rain_text = st.selectbox(
            translate("rain", lang),
            rain_options,
            index=rain_options.index(default_rain),
            key="weather_rain"
        )

    with col2:

        season_map = {
            translate("spring", lang): "Spring",
            translate("summer", lang): "Summer",
            translate("autumn", lang): "Autumn",
            translate("winter", lang): "Winter"
        }

        condition_map = {
            translate("clear", lang): "Clear",
            translate("cloudy", lang): "Cloudy",
            translate("rainy", lang): "Rainy",
            translate("snowy", lang): "Snowy",
            translate("stormy", lang): "Stormy"
        }

        occasion_map = {
            translate("casual", lang): "Casual",
            translate("formal", lang): "Formal",
            translate("sport", lang): "Sport",
            translate("business", lang): "Business",
            translate("traditional", lang): "Traditional"
        }

        style_map = {
            translate("casual", lang): "Casual",
            translate("sporty", lang): "Sporty",
            translate("formal", lang): "Formal",
            translate("business", lang): "Business",
            translate("traditional", lang): "Traditional"
        }

        if live_weather:
            from datetime import datetime

            detected_season = season_from_month(
                datetime.now().month
            )
            detected_condition = weather_condition_from_code(
                live_weather["weather_code"]
            )
        else:
            detected_season = "Summer"
            detected_condition = "Clear"

        season_labels = list(season_map.keys())
        condition_labels = list(condition_map.keys())

        selected_season = st.selectbox(
            translate("season", lang),
            season_labels,
            index=season_labels.index(
                next(
                    label for label, value in season_map.items()
                    if value == detected_season
                )
            ),
            key="weather_season"
        )

        selected_condition = st.selectbox(
            translate("weather_condition", lang),
            condition_labels,
            index=condition_labels.index(
                next(
                    label for label, value in condition_map.items()
                    if value == detected_condition
                )
            ),
            key="weather_condition"
        )

        selected_occasion = st.selectbox(
            translate("occasion", lang),
            list(occasion_map.keys()),
            key="weather_occasion"
        )

        selected_style = st.selectbox(
            translate("clothing_style", lang),
            list(style_map.keys()),
            key="weather_style"
        )

    rain = 1 if rain_text == translate("yes", lang) else 0
    season = season_map[selected_season]
    condition = condition_map[selected_condition]
    occasion = occasion_map[selected_occasion]
    style = style_map[selected_style]

    if live_weather:
        st.info(
            f"📍 {live_weather['city']}, {live_weather['country']}  |  "
            f"🌡️ {live_weather['temperature']:.1f} °C  |  "
            f"💧 {live_weather['humidity']}%  |  "
            f"💨 {live_weather['wind_speed']:.1f} km/h"
        )
        st.caption(
            f"{ui_text('weather_source', lang)}: "
            f"{ui_text('open_meteo', lang)}"
        )

        render_weather_visualizations(live_weather, lang)

    st.markdown("---")

    # --------------------------------------------------
    # PREDICTION
    # --------------------------------------------------

    if st.button(
        f"🤖 {translate('predict_outfit', lang)}",
        type="primary",
        width="stretch"
    ):

        user = get_user(
            st.session_state.username
        )

        if user is None:
            st.error(
                translate("user_not_found", lang)
            )
            return

        prediction, confidence = get_prediction_confidence(
            temperature,
            humidity,
            wind_speed,
            rain,
            season,
            condition,
            occasion,
            style
        )

        weather_id = save_weather(
            user["id"],
            temperature,
            humidity,
            wind_speed,
            rain,
            season,
            condition
        )

        recommendation_keys = {
            "Heavy Winter Outfit": "heavy_winter_desc",
            "Formal Winter Outfit": "formal_winter_desc",
            "Winter Outfit": "winter_desc",
            "Hot Weather Outfit": "hot_weather_desc",
            "Light Summer Outfit": "light_summer_desc",
            "Light Winter Outfit": "light_winter_desc",
            "Rainy Cold Outfit": "rainy_cold_desc",
            "Rainy Light Outfit": "rainy_light_desc",
            "Sport Summer Outfit": "sport_summer_desc",
            "Sport Winter Outfit": "sport_winter_desc",
            "Spring Autumn Outfit": "spring_autumn_desc"
        }

        outfit_name_keys = {
            "Heavy Winter Outfit": "heavy_winter_outfit",
            "Formal Winter Outfit": "formal_winter_outfit",
            "Winter Outfit": "winter_outfit",
            "Hot Weather Outfit": "hot_weather_outfit",
            "Light Summer Outfit": "light_summer_outfit",
            "Light Winter Outfit": "light_winter_outfit",
            "Rainy Cold Outfit": "rainy_cold_outfit",
            "Rainy Light Outfit": "rainy_light_outfit",
            "Sport Summer Outfit": "sport_summer_outfit",
            "Sport Winter Outfit": "sport_winter_outfit",
            "Spring Autumn Outfit": "spring_autumn_outfit"
        }

        description_key = recommendation_keys.get(prediction)
        outfit_name_key = outfit_name_keys.get(prediction)

        recommendation_text = (
            translate(description_key, lang)
            if description_key
            else translate("choose_appropriate_clothing", lang)
        )

        displayed_prediction = (
            translate(outfit_name_key, lang)
            if outfit_name_key
            else prediction
        )

        recommendation_id = save_recommendation(
            user["id"],
            weather_id,
            prediction,
            recommendation_text,
            "Random Forest"
        )

        st.success(
            translate("prediction_success", lang)
        )

        st.markdown(
            f"### 👕 {translate('recommended_outfit', lang)}"
        )

        details = outfit_details(
            prediction,
            temperature,
            humidity,
            wind_speed,
            rain,
            condition,
            occasion,
            style,
            lang
        )

        # Professional visual recommendation: the ML prediction remains the
        # decision-maker; the local image is only the presentation layer.
        image_path = outfit_image_path(prediction)
        image_col, copy_col = st.columns([1.15, 1], gap="large")

        with image_col:
            if image_path:
                st.image(str(image_path), width="stretch")

        with copy_col:
            st.markdown(
                '<div class="outfit-copy">'
                f'<div class="eyebrow">{translate("recommended_outfit", lang)}</div>'
                f'<h3>{displayed_prediction}</h3>'
                f'<p>{details["basis"]}</p>'
                '</div>',
                unsafe_allow_html=True
            )

        detail_col1, detail_col2 = st.columns(2)

        with detail_col1:
            with st.container(border=True):
                st.markdown(f"**{ui_text('upper_body', lang)}**")
                st.write(details["upper"])

            with st.container(border=True):
                st.markdown(f"**{ui_text('footwear', lang)}**")
                st.write(details["footwear"])

        with detail_col2:
            with st.container(border=True):
                st.markdown(f"**{ui_text('lower_body', lang)}**")
                st.write(details["lower"])

            with st.container(border=True):
                st.markdown(f"**{ui_text('outer_layer', lang)}**")
                st.write(details["outer"])

        st.markdown(
            f"### {ui_text('why_recommended', lang)}"
        )
        st.info(recommendation_text)

        if details["adjustments"]:
            adjustment_labels = {
                "rain": {"English": "rain detected", "دری": "بارندگی تشخیص داده شد", "پښتو": "باران تشخیص شو"},
                "strong wind": {"English": "strong wind", "دری": "باد شدید", "پښتو": "شدید باد"},
                "high humidity": {"English": "high humidity", "دری": "رطوبت بلند", "پښتو": "لوړ رطوبت"},
                "cold temperature": {"English": "cold temperature", "دری": "دمای سرد", "پښتو": "سړه تودوخه"},
                "hot temperature": {"English": "hot temperature", "دری": "دمای گرم", "پښتو": "ګرمه تودوخه"},
            }
            factors = [adjustment_labels[x][lang] for x in details["adjustments"]]
            if lang == "English":
                st.caption("Additional weather factors: " + ", ".join(factors) + ".")
            elif lang == "دری":
                st.caption("عوامل اضافی آب‌وهوا: " + "، ".join(factors) + ".")
            else:
                st.caption("د هوا اضافي عوامل: " + "، ".join(factors) + ".")

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric(
            translate("model_confidence", lang),
            f"{confidence:.2f}%"
        )
        metric_col2.metric(
            translate("model", lang),
            "Random Forest"
        )
        metric_col3.metric(
            translate("recommendation_id", lang),
            recommendation_id
        )

        st.markdown(
            f"### 📋 {translate('input_weather_data', lang)}"
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            translate("temperature", lang),
            f"{temperature} °C"
        )
        c2.metric(
            translate("humidity", lang),
            f"{humidity}%"
        )
        c3.metric(
            translate("wind_speed", lang),
            f"{wind_speed} km/h"
        )
        c4.metric(
            translate("rain", lang),
            rain_text
        )

# --------------------------------------------------
# HISTORY
# --------------------------------------------------

def history_page():

    lang = st.session_state.language

    st.title(
        f"📚 {translate('recommendation_history', lang)}"
    )

    user = get_user(
        st.session_state.username
    )

    records = get_user_recommendations(
        user["id"]
    )

    if not records:

        st.info(
            translate(
                "no_history",
                lang
            )
        )

        return

    for record in records:

        with st.container(border=True):

            # ------------------------------------------
            # TRANSLATE OUTFIT NAME
            # ------------------------------------------

            outfit_name_keys = {

                "Heavy Winter Outfit":
                    "heavy_winter_outfit",

                "Formal Winter Outfit":
                    "formal_winter_outfit",

                "Winter Outfit":
                    "winter_outfit",

                "Hot Weather Outfit":
                    "hot_weather_outfit",

                "Light Summer Outfit":
                    "light_summer_outfit",

                "Light Winter Outfit":
                    "light_winter_outfit",

                "Rainy Cold Outfit":
                    "rainy_cold_outfit",

                "Rainy Light Outfit":
                    "rainy_light_outfit",

                "Sport Summer Outfit":
                    "sport_summer_outfit",

                "Sport Winter Outfit":
                    "sport_winter_outfit",

                "Spring Autumn Outfit":
                    "spring_autumn_outfit"
            }

            outfit_key = outfit_name_keys.get(
                record["outfit_category"]
            )

            displayed_outfit = translate(
                outfit_key,
                lang
            ) if outfit_key else record["outfit_category"]

            st.subheader(
                f"👕 {displayed_outfit}"
            )
               
        # ------------------------------------------
        # TRANSLATE RECOMMENDATION
        # ------------------------------------------

        recommendation_keys = {

            "Heavy Winter Outfit":
                "heavy_winter_desc",

            "Formal Winter Outfit":
                "formal_winter_desc",

            "Winter Outfit":
                "winter_desc",

            "Hot Weather Outfit":
                "hot_weather_desc",

            "Light Summer Outfit":
                "light_summer_desc",

            "Light Winter Outfit":
                "light_winter_desc",

            "Rainy Cold Outfit":
                "rainy_cold_desc",

            "Rainy Light Outfit":
                "rainy_light_desc",

            "Sport Summer Outfit":
                "sport_summer_desc",

            "Sport Winter Outfit":
                "sport_winter_desc",

            "Spring Autumn Outfit":
                "spring_autumn_desc"
        }

        recommendation_key = recommendation_keys.get(
            record["outfit_category"]
        )

        displayed_recommendation = translate(
            recommendation_key,
            lang
        ) if recommendation_key else record["recommendation"]

        st.write(
            displayed_recommendation
        )
           
        col1, col2, col3 = st.columns(3)
        # ------------------------------------------
        # TRANSLATE SEASON
        # ------------------------------------------

        season_keys = {
            "Spring": "spring",
            "Summer": "summer",
            "Autumn": "autumn",
            "Winter": "winter"
        }

        season_key = season_keys.get(
            record["season"]
        )

        displayed_season = translate(
            season_key,
            lang
        ) if season_key else record["season"]

        col1.write(
            f"🌡️ {translate('temperature', lang)}: "
            f"{record['temperature']} °C"
        )

        col2.write(
            f"💧 {translate('humidity', lang)}: "
            f"{record['humidity']}%"
        )

        col3.write(
            f"🍃 {translate('season_label', lang)}: "
            f"{displayed_season}"
        )

        if st.button(
            f"⭐ {translate('add_to_favorites', lang)}",
            key=f"favorite_{record['id']}"
        ):

            success = add_favorite(
                user["id"],
                record["id"]
            )

            if success:

                st.success(
                    translate(
                        "added_to_favorites",
                        lang
                    )
                )

            else:

                st.warning(
                    translate(
                        "already_favorite",
                        lang
                    )
                )


# --------------------------------------------------
# FAVORITES
# --------------------------------------------------

def favorites_page():
    lang = st.session_state.get("lang", "English")
    st.title(
        f"⭐ {translate('favorite_outfits', lang)}"
    )

    user = get_user(
        st.session_state.username
    )

    favorites = get_user_favorites(
        user["id"]
    )

    if not favorites:

        st.info(
            translate(
                "no_favorite_recommendations",
                lang
            )
        )

        return

    for favorite in favorites:

        with st.container(border=True):

            # ------------------------------------------
            # TRANSLATE OUTFIT NAME
            # ------------------------------------------

            outfit_keys = {

                "Heavy Winter Outfit":
                    "heavy_winter_outfit",

                "Formal Winter Outfit":
                    "formal_winter_outfit",

                "Winter Outfit":
                    "winter_outfit",

                "Hot Weather Outfit":
                    "hot_weather_outfit",

                "Light Summer Outfit":
                    "light_summer_outfit",

                "Light Winter Outfit":
                    "light_winter_outfit",

                "Rainy Cold Outfit":
                    "rainy_cold_outfit",

                "Rainy Light Outfit":
                    "rainy_light_outfit",

                "Sport Summer Outfit":
                    "sport_summer_outfit",

                "Sport Winter Outfit":
                    "sport_winter_outfit",

                "Spring Autumn Outfit":
                    "spring_autumn_outfit"
            }

            outfit_key = outfit_keys.get(
                favorite["outfit_category"]
            )

            displayed_outfit = translate(
                outfit_key,
                lang
            ) if outfit_key else favorite["outfit_category"]

            # ------------------------------------------
            # TRANSLATE RECOMMENDATION
            # ------------------------------------------

            recommendation_keys = {

                "Heavy Winter Outfit":
                    "heavy_winter_desc",

                "Formal Winter Outfit":
                    "formal_winter_desc",

                "Winter Outfit":
                    "winter_desc",

                "Hot Weather Outfit":
                    "hot_weather_desc",

                "Light Summer Outfit":
                    "light_summer_desc",

                "Light Winter Outfit":
                    "light_winter_desc",

                "Rainy Cold Outfit":
                    "rainy_cold_desc",

                "Rainy Light Outfit":
                    "rainy_light_desc",

                "Sport Summer Outfit":
                    "sport_summer_desc",

                "Sport Winter Outfit":
                    "sport_winter_desc",

                "Spring Autumn Outfit":
                    "spring_autumn_desc"
            }

            recommendation_key = recommendation_keys.get(
                favorite["outfit_category"]
            )

            displayed_recommendation = translate(
                recommendation_key,
                lang
            ) if recommendation_key else favorite["recommendation"]

            # ------------------------------------------
            # DISPLAY
            # ------------------------------------------

            st.subheader(
                f"👕 {displayed_outfit}"
            )

            st.write(
                displayed_recommendation
            )
# --------------------------------------------------
# STATISTICS
# --------------------------------------------------

def statistics_page():

    lang = st.session_state.language

    user = get_user(st.session_state.username)

    if user is None:
        st.error(translate("user_not_found", lang))
        return

    recommendations = get_user_recommendations(user["id"])
    favorites = get_user_favorites(user["id"])

    st.title(translate("statistics", lang))
    st.caption("Your recommendation and weather activity overview.")

    total_recommendations = len(recommendations)
    total_favorites = len(favorites)

    weather_ids = {
        item.get("weather_id")
        for item in recommendations
        if item.get("weather_id") is not None
    }

    total_weather = len(weather_ids)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            translate("recommendations", lang),
            total_recommendations
        )

    with col2:
        st.metric(
            translate("favorite_outfits", lang),
            total_favorites
        )

    with col3:
        st.metric(
            translate("weather_data", lang),
            total_weather
        )

    if not recommendations:
        st.markdown("---")
        st.info(translate("no_history", lang))
        return

    st.markdown("---")
    st.subheader(ui_text("outfit_categories", lang))

    category_counts = {}

    for record in recommendations:
        category = record.get("outfit_category", "Unknown")
        category_counts[category] = category_counts.get(category, 0) + 1

    st.bar_chart(category_counts)

    st.markdown("---")
    st.subheader(ui_text("weather_conditions", lang))

    weather_counts = {}

    for record in recommendations:
        condition = record.get("weather_condition", "Unknown")
        weather_counts[condition] = weather_counts.get(condition, 0) + 1

    st.bar_chart(weather_counts)

    temperatures = []

    for record in recommendations:
        value = record.get("temperature")
        if value is not None:
            try:
                temperatures.append(float(value))
            except (TypeError, ValueError):
                pass

    if temperatures:
        st.markdown("---")
        st.subheader(ui_text("temperature_analysis", lang))

        temp1, temp2, temp3 = st.columns(3)

        with temp1:
            st.metric(ui_text("average", lang), f"{sum(temperatures) / len(temperatures):.1f} °C")

        with temp2:
            st.metric(ui_text("lowest", lang), f"{min(temperatures):.1f} °C")

        with temp3:
            st.metric(ui_text("highest", lang), f"{max(temperatures):.1f} °C")

    st.markdown("---")
    st.subheader(ui_text("recent_recommendations", lang))

    for record in recommendations[:5]:
        category = record.get("outfit_category", "Unknown")
        recommendation = record.get("recommendation", "")
        temperature = record.get("temperature", "N/A")
        humidity = record.get("humidity", "N/A")
        season = record.get("season", "N/A")

        st.markdown(
            f"**{category}**  \n"
            f"{recommendation}  \n"
            f"{translate('temperature', lang)}: {temperature} °C  |  "
            f"{translate('humidity', lang)}: {humidity}%  |  "
            f"{translate('season_label', lang)}: {season}"
        )

def profile_page():

    lang = st.session_state.language

    user = get_user(st.session_state.username)

    if user is None:
        st.error(translate("user_not_found", lang))
        return

    recommendations = get_user_recommendations(user["id"])
    favorites = get_user_favorites(user["id"])

    st.title(translate("profile", lang))
    st.caption("Account information and personal activity.")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(translate("username", lang))
        st.write(user["username"])

    with col2:
        st.subheader(ui_text("role", lang))
        st.write(user.get("role", "user").title())

    st.markdown("---")

    st.subheader(ui_text("account", lang))
    st.write(f"**{ui_text('created', lang)}:** {user['created_at']}")

    st.markdown("---")

    st.subheader(ui_text("activity", lang))

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            translate("recommendations", lang),
            len(recommendations)
        )

    with c2:
        st.metric(
            translate("favorite_outfits", lang),
            len(favorites)
        )

    st.markdown("---")

    st.subheader(translate("machine_learning", lang))
    st.write(translate("ml_description", lang))
    st.write("Random Forest — 200 trees — test accuracy: 91%.")

def admin_page():

    lang = st.session_state.language

    # Security check: the page should never be reachable by a normal user.
    current_user = get_user(st.session_state.username)

    if not current_user or current_user.get("role") != "admin":
        st.error(ui_text("administrator_required", lang))
        return

    stats = get_statistics()

    st.title(translate("admin_dashboard", lang))
    st.caption("System administration and model information.")

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(ui_text("users", lang), stats["users"])
    col2.metric(translate("weather_data", lang), stats["weather_records"])
    col3.metric(translate("recommendations", lang), stats["recommendations"])
    col4.metric(translate("favorite_outfits", lang), stats["favorites"])

    st.markdown("---")
    st.subheader(translate("machine_learning", lang))

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(ui_text("algorithm", lang), "Random Forest")
    col2.metric(ui_text("trees", lang), "200")
    col3.metric(ui_text("dataset", lang), "1500")
    col4.metric("Test Accuracy", "91%")

    st.success(ui_text("model_active", lang))

    st.markdown("---")
    st.subheader(ui_text("user_management", lang))

    users = get_all_users()

    if not users:
        st.info(ui_text("no_users", lang))
        return

    user_data = [
        {
            "ID": user["id"],
            "Username": user["username"],
            "Role": user["role"],
            "Created At": user["created_at"],
        }
        for user in users
    ]

    st.dataframe(
        user_data,
        width="stretch",
        hide_index=True
    )

    st.markdown("---")
    st.subheader(ui_text("manage_roles", lang))

    for user in users:

        if user["username"] == st.session_state.username:
            continue

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.write(f"**{user['username']}**")

        with col2:
            new_role = st.selectbox(
                "Role",
                ["user", "admin"],
                index=0 if user["role"] == "user" else 1,
                key=f"role_{user['id']}"
            )

        with col3:
            if st.button(
                "Update",
                key=f"update_role_{user['id']}",
                width="stretch"
            ):
                if update_user_role(user["id"], new_role):
                    st.success(
                        f"Role updated for {user['username']}."
                    )
                    st.rerun()

# --------------------------------------------------
# APPLICATION ROUTER
# --------------------------------------------------

if not st.session_state.logged_in:

    if st.session_state.auth_mode == "login":

        login_page()

    elif st.session_state.auth_mode == "forgot":

        forgot_password_page()

    else:

        register_page()

    st.stop()


page = sidebar()

if page == "dashboard":

    dashboard()

elif page == "weather":

    weather_page()

elif page == "history":

    history_page()

elif page == "favorites":

    favorites_page()

elif page == "statistics":

    statistics_page()

elif page == "profile":

    profile_page()

elif page == "admin":

    admin_page()
