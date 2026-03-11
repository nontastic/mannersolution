# app.py

from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from src.cn_loader import load_cn_data
from src.pipeline import process_erp_dataframe


st.set_page_config(page_title="Zolltarif Matcher", layout="wide")

st.title("Zolltarif Matcher auf Basis der CN-Liste")
st.write(
    "Dieses Tool matched eure ERP-Artikeltexte gegen die deutsche CN-Beschreibung "
    "und liefert die besten Zolltarif-Kandidaten zurück."
)

st.markdown("""
### Erwartete Dateien
**ERP-Datei** mit:
- `Materialnummer`
- `Kurztext`
- `Einkaufsbestelltext`

**CN-Datei** mit:
- `CN_CODE`
- `SelfText_DE`
""")

use_default_files = st.checkbox("Dateien aus dem /data-Ordner verwenden", value=True)

erp_file = None
cn_file = None

if not use_default_files:
    erp_file = st.file_uploader("ERP-Datei hochladen", type=["xlsx"], key="erp")
    cn_file = st.file_uploader("CN-Datei hochladen", type=["xlsx"], key="cn")

if st.button("Matching starten"):
    try:
        if use_default_files:
            erp_path = Path("data/Export_SAP_200MM.XLSX")
            cn_path = Path("data/CN2026_SelfText_EN_DE_FR.xlsx")

            if not erp_path.exists():
                st.error(f"ERP-Datei nicht gefunden: {erp_path}")
                st.stop()

            if not cn_path.exists():
                st.error(f"CN-Datei nicht gefunden: {cn_path}")
                st.stop()

            erp_df = pd.read_excel(erp_path)
            cn_df = load_cn_data(cn_path)

        else:
            if erp_file is None or cn_file is None:
                st.error("Bitte beide Dateien hochladen.")
                st.stop()

            erp_df = pd.read_excel(erp_file)
            cn_df = load_cn_data(cn_file)

        with st.spinner("Verarbeite Daten und berechne Matches..."):
            result_df = process_erp_dataframe(erp_df, cn_df)

        st.success("Matching abgeschlossen.")

        c1, c2, c3 = st.columns(3)
        c1.metric("ERP-Artikel", len(result_df))
        c2.metric("CN-Einträge", len(cn_df))
        c3.metric("Durchschnittlicher Best Score", round(result_df["Best_Score"].mean(), 3))

        st.subheader("Ergebnis")
        st.dataframe(result_df, use_container_width=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            result_df.to_excel(writer, index=False, sheet_name="Matches")
        output.seek(0)

        st.download_button(
            label="Ergebnis als Excel herunterladen",
            data=output.getvalue(),
            file_name="zolltarif_matches.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception as e:
        st.error(f"Fehler: {e}")