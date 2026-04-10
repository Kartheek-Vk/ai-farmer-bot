import streamlit as st

from ai_farmer_backend import decision_function


st.set_page_config(
    page_title="AI Smart Farmer Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# Dark, minimal SaaS-style visual system.
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #0b1020 0%, #111827 100%);
            color: #f9fafb;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 1.5rem;
            max-width: 1400px;
        }
        h1, h2, h3 {
            letter-spacing: -0.02em;
            font-weight: 800;
        }
        p, label, div {
            color: #d1d5db;
        }
        .hero-card {
            background: linear-gradient(135deg, rgba(30,41,59,0.95), rgba(15,23,42,0.95));
            border: 1px solid rgba(148,163,184,0.18);
            border-radius: 24px;
            padding: 1.5rem;
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.28);
            margin-bottom: 1rem;
        }
        .panel-card {
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 22px;
            padding: 1.25rem;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.22);
            height: 100%;
        }
        .metric-card {
            background: linear-gradient(180deg, rgba(17,24,39,0.95), rgba(15,23,42,0.95));
            border: 1px solid rgba(148,163,184,0.16);
            border-radius: 22px;
            padding: 1.2rem;
            min-height: 180px;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.24);
        }
        .card-label {
            font-size: 0.92rem;
            color: #94a3b8;
            margin-bottom: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .card-value {
            font-size: 2rem;
            font-weight: 800;
            color: #f8fafc;
            line-height: 1.15;
        }
        .card-subvalue {
            font-size: 1.1rem;
            color: #cbd5e1;
            margin-top: 0.5rem;
        }
        .profit-positive {
            color: #22c55e;
        }
        .trend-up {
            color: #22c55e;
        }
        .trend-down {
            color: #ef4444;
        }
        .confidence-high {
            color: #22c55e;
        }
        .confidence-medium {
            color: #facc15;
        }
        .confidence-low {
            color: #fb7185;
        }
        .crop-highlight {
            color: #facc15;
        }
        .footer {
            text-align: center;
            color: #94a3b8;
            padding-top: 1rem;
            padding-bottom: 0.5rem;
            font-size: 0.95rem;
        }
        div[data-testid="stButton"] button {
            background: linear-gradient(135deg, #84cc16, #22c55e);
            color: #04130a;
            border: none;
            border-radius: 14px;
            font-weight: 800;
            width: 100%;
            padding: 0.8rem 1rem;
            box-shadow: 0 10px 24px rgba(34, 197, 94, 0.28);
        }
        div[data-testid="stButton"] button:hover {
            filter: brightness(1.05);
        }
        div[data-testid="stNumberInput"] input,
        div[data-testid="stTextInput"] input {
            background-color: rgba(30, 41, 59, 0.9) !important;
            color: #f8fafc !important;
            border-radius: 12px !important;
            border: 2px solid rgba(148, 163, 184, 0.3) !important;
            padding: 10px 12px !important;
            font-size: 14px !important;
            cursor: text !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        div[data-testid="stNumberInput"] input:focus,
        div[data-testid="stTextInput"] input:focus {
            background-color: rgba(30, 41, 59, 1) !important;
            border: 2px solid #84cc16 !important;
            outline: none !important;
            box-shadow: 0 0 0 3px rgba(132, 204, 22, 0.1) !important;
        }
        div[data-testid="stNumberInput"] input::placeholder,
        div[data-testid="stTextInput"] input::placeholder {
            color: #94a3b8 !important;
        }
        div[data-testid="stTextInput"] {
            pointer-events: auto !important;
        }
        div[data-testid="stTextInput"] label {
            color: #d1d5db !important;
            margin-bottom: 0.5rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_metric_card(title: str, value: str, extra: str = "", value_class: str = "") -> None:
    class_attr = f"card-value {value_class}".strip()
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="card-label">{title}</div>
            <div class="{class_attr}">{value}</div>
            <div class="card-subvalue">{extra}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_list_card(title: str, items: list[str]) -> None:
    content = "".join(f"<li>{item}</li>" for item in items) if items else "<li>No alerts available</li>"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="card-label">{title}</div>
            <ul style="margin:0; padding-left: 1.2rem; color:#e5e7eb; line-height:1.8;">
                {content}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_currency(value: float) -> str:
    return f"Rs. {value:,.0f}"


def parse_float(label: str, raw_value: str) -> float:
    if raw_value is None or not str(raw_value).strip():
        raise ValueError(f"{label} is required.")
    return float(raw_value)


def get_price_trend(result: dict) -> tuple[str, str]:
    current_price = float(result.get("price", 0))
    predicted_price = float(result.get("predicted_price", 0))
    if predicted_price > current_price:
        return "Price trend: rising", "trend-up"
    return "Price trend: softening", "trend-down"


def get_confidence_style(result: dict) -> tuple[str, str]:
    confidence = float(result.get("confidence", 0))
    if confidence >= 85:
        return "High confidence prediction", "confidence-high"
    if confidence >= 60:
        return "Moderate confidence prediction", "confidence-medium"
    return "Low confidence prediction", "confidence-low"


def build_probability_items(result: dict) -> list[str]:
    top_probabilities = result.get("top_probabilities", [])
    return [
        f"{str(item.get('crop', 'N/A')).title()}: {float(item.get('probability', 0)):.2f}%"
        for item in top_probabilities
    ]


if "result" not in st.session_state:
    st.session_state.result = None


st.markdown(
    """
    <div class="hero-card">
        <h1 style="margin-bottom:0.35rem;">🌾 AI Smart Farmer Assistant</h1>
        <p style="font-size:1.05rem; margin:0; color:#cbd5e1;">
            Profit Optimization &amp; Decision Support System
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([1, 1.35], gap="large")


with left_col:
    st.subheader("Input Panel")
    st.caption("Enter soil and climate values to generate a recommendation.")

    with st.container(border=True):
        n_input = st.text_input("Nitrogen (N)", placeholder="e.g. 90", key="n_input")
        p_input = st.text_input("Phosphorus (P)", placeholder="e.g. 40", key="p_input")
        k_input = st.text_input("Potassium (K)", placeholder="e.g. 40", key="k_input")
        temp_input = st.text_input("Temperature", placeholder="e.g. 25", key="temp_input")
        humidity_input = st.text_input("Humidity", placeholder="e.g. 80", key="humidity_input")
        ph_input = st.text_input("pH", placeholder="e.g. 6.5", key="ph_input")
        rainfall_input = st.text_input("Rainfall", placeholder="e.g. 200", key="rainfall_input")

    st.divider()

    if st.button("🚀 Get Recommendation"):
        values = [
            st.session_state.n_input,
            st.session_state.p_input,
            st.session_state.k_input,
            st.session_state.temp_input,
            st.session_state.humidity_input,
            st.session_state.ph_input,
            st.session_state.rainfall_input
        ]
        labels = ["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)", "Temperature", "Humidity", "pH", "Rainfall"]
        
        empty_fields = [labels[i] for i, v in enumerate(values) if not str(v).strip()]
        
        if empty_fields:
            st.warning(f"⚠️ Please fill in these fields: {', '.join(empty_fields)}")
        else:
            with st.spinner("Analyzing farm conditions and generating recommendation..."):
                try:
                    n_value = parse_float("Nitrogen (N)", n_input)
                    p_value = parse_float("Phosphorus (P)", p_input)
                    k_value = parse_float("Potassium (K)", k_input)
                    temp_value = parse_float("Temperature", temp_input)
                    humidity_value = parse_float("Humidity", humidity_input)
                    ph_value = parse_float("pH", ph_input)
                    rainfall_value = parse_float("Rainfall", rainfall_input)

                    st.session_state.result = decision_function(
                        n_value, p_value, k_value, temp_value, humidity_value, ph_value, rainfall_value
                    )
                except Exception as error:
                    st.session_state.result = None
                    st.error(f"Unable to generate recommendation: {error}")


with right_col:
    st.subheader("Decision Dashboard")
    st.caption("Recommendation outputs are shown in a Bento Grid layout.")

    result = st.session_state.result

    if result is None:
        st.info("Complete the input form and click the button to view the recommendation dashboard.")
    else:
        row1_col1, row1_col2 = st.columns(2, gap="medium")
        row2_col1, row2_col2 = st.columns(2, gap="medium")
        row3_col1, row3_col2 = st.columns(2, gap="medium")
        row4_col1, row4_col2 = st.columns(2, gap="medium")
        row5_col1, row5_col2 = st.columns(2, gap="medium")

        trend_text, trend_class = get_price_trend(result)
        confidence_text, confidence_class = get_confidence_style(result)

        with row1_col1:
            render_metric_card(
                "🌾 Recommended Crop",
                str(result.get("crop", "N/A")).title(),
                "Best match from the trained crop model",
                "crop-highlight",
            )

        with row1_col2:
            render_metric_card(
                "💰 Expected Profit",
                format_currency(float(result.get("profit", 0))),
                "Estimated from price minus cost",
                "profit-positive" if float(result.get("profit", 0)) > 0 else "",
            )

        with row2_col1:
            render_metric_card(
                "📊 Price & Cost",
                format_currency(float(result.get("price", 0))),
                f"Current price | Cost: {format_currency(float(result.get('cost', 0)))}",
            )

        with row2_col2:
            render_metric_card(
                "📈 Predicted Price",
                format_currency(float(result.get("predicted_price", 0))),
                trend_text,
                trend_class,
            )

        with row3_col1:
            render_metric_card(
                "🎯 Model Confidence",
                f"{float(result.get('confidence', 0)):.2f}%",
                confidence_text,
                confidence_class,
            )

        with row3_col2:
            probability_items = build_probability_items(result)
            render_list_card("📊 Prediction Probabilities", probability_items)

        with row4_col1:
            alerts = result.get("alerts", [])
            render_list_card("⚠️ Risk Alerts", alerts)

        with row4_col2:
            render_metric_card(
                "🧠 Recommendation Message",
                str(result.get("recommendation", "N/A")),
                "Decision layer summary",
            )

        with row5_col1:
            render_metric_card(
                "🕒 Selling Advice",
                str(result.get("selling_advice", "N/A")),
                "Market timing support based on price forecast",
                trend_class,
            )

        with row5_col2:
            explanation = result.get("reason")
            if not explanation:
                explanation = (
                    f"{str(result.get('crop', 'This crop')).title()} is suggested based on the provided soil nutrients, "
                    f"weather inputs, and the backend model prediction."
                )
            render_metric_card(
                "📌 Explanation",
                explanation,
                "Why this recommendation was produced",
            )

st.divider()
st.markdown('<div class="footer">Built with AI for Smart Farming 🌱</div>', unsafe_allow_html=True)
