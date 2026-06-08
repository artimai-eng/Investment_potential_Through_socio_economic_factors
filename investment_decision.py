
import streamlit as st
import pandas as pd
import mysql.connector

if "connected" not in st.session_state:
    st.session_state.connected = False
    st.session_state.conn = None

st.title("Investment Decision Support System")
st.caption("Using WHO Socioeconomic Indicators (2000–2015)")

st.sidebar.header("Database Connection")

host = st.sidebar.text_input("Host", "localhost")
user = st.sidebar.text_input("Username", "root")
password = st.sidebar.text_input("Password", type="password")
database = st.sidebar.text_input("Database", "who_db")

if st.sidebar.button("Connect"):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        st.session_state.connected = True
        st.session_state.conn = conn
        st.success("Connected successfully!")

    except Exception as e:
        st.error(f"Connection failed: {e}")
        st.stop()


if st.session_state.connected:

    conn = st.session_state.conn

    def run_query(query):
        return pd.read_sql(query, conn)

    countries = run_query(
        "SELECT DISTINCT country FROM life_expect ORDER BY country"
    )

    st.header("Country Investment Analysis")

    selected_country = st.selectbox(
        "Select Country",
        countries["country"]
    )

    query = f"""
        SELECT
            AVG(gdp) AS avg_gdp,
            AVG(life_expectancy) AS avg_life_expec,
            AVG(schooling) AS avg_schooling,
            AVG(adult_mortality) AS avg_mortality,
            AVG(polio) AS avg_polio
        FROM life_expect
        WHERE country = '{selected_country}'
    """

    df = run_query(query)
    row = df.iloc[0]


    def investment_score(row):
        score = 0

        if row["avg_life_expec"] > 70:
            score += 1

        if row["avg_schooling"] > 10:
            score += 1

        if row["avg_mortality"] < 150:
            score += 1

        if row["avg_gdp"] > 3000:
            score += 1

        return score

    score = investment_score(row)

    st.metric(
        "Investment Readiness Score",
        f"{score}/4"
    )


    st.subheader("Investment Decision Factors")

    factors_df = pd.DataFrame({
        "Factor": [
            "Life Expectancy",
            "Schooling",
            "Adult Mortality",
            "GDP"
        ],
        "Country Value": [
            round(row["avg_life_expec"], 2),
            round(row["avg_schooling"], 2),
            round(row["avg_mortality"], 2),
            round(row["avg_gdp"], 2)
        ],
        "Benchmark": [
            "> 70",
            "> 10",
            "< 150",
            "> 3000"
        ],
        "Status": [
            "✅" if row["avg_life_expec"] > 70 else "❌",
            "✅" if row["avg_schooling"] > 10 else "❌",
            "✅" if row["avg_mortality"] < 150 else "❌",
            "✅" if row["avg_gdp"] > 3000 else "❌"
        ]
    })

    st.dataframe(
        factors_df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Investment Recommendation")

    if score >= 3:
        st.success(f"INVEST in {selected_country}")
    elif score == 2:
        st.warning(f"MODERATE OPPORTUNITY in {selected_country}")
    else:
        st.error(f"HIGH RISK investment destination")

    st.markdown("### Why?")

    reasons = []

    if row["avg_life_expec"] > 70:
        reasons.append("Strong public health outcomes")

    if row["avg_schooling"] > 10:
        reasons.append("Educated workforce")

    if row["avg_mortality"] < 150:
        reasons.append("Lower mortality risk")

    if row["avg_gdp"] > 3000:
        reasons.append("Healthy economic indicators")

    if not reasons:
        reasons.append("Multiple socioeconomic indicators are below benchmark levels")

    for reason in reasons:
        st.write(f"• {reason}")


    st.subheader("Recommended Investment Sectors")

    sectors = []

    if row["avg_schooling"] >= 10:
        sectors.append([
            "Education & Human Capital",
            "High schooling levels indicate strong demand for education, training and EdTech."
        ])

    if row["avg_life_expec"] >= 70 and row["avg_mortality"] < 200:
        sectors.append([
            "Healthcare, Pharma & Insurance",
            "Strong health outcomes support advanced healthcare investments."
        ])

    if row["avg_gdp"] >= 3000 and row["avg_life_expec"] >= 65:
        sectors.append([
            "Consumer & Retail",
            "Higher GDP suggests stronger purchasing power and consumer demand."
        ])

    if row["avg_schooling"] >= 11 and row["avg_gdp"] >= 4000:
        sectors.append([
            "IT & Business Services",
            "Skilled workforce suitable for technology and service industries."
        ])

    if row["avg_gdp"] >= 2500 and row["avg_schooling"] >= 8:
        sectors.append([
            "Manufacturing & Industrial Production",
            "Economic and workforce indicators support industrial activity."
        ])

    if row["avg_polio"] >= 80:
        sectors.append([
            "Public Health Infrastructure",
            "Strong vaccination coverage indicates stable healthcare systems."
        ])

    if not sectors:
        sectors.append([
            "No clear sector dominance",
            "Further qualitative analysis is recommended."
        ])

    sectors_df = pd.DataFrame(
        sectors,
        columns=["Sector", "Reason"]
    )

    st.dataframe(
        sectors_df,
        use_container_width=True,
        hide_index=True
    )

    st.caption("Developed by Arti Maibam | Streamlit + MySQL")
