import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Prekių palyginimo įrankis")

csv_file = st.file_uploader("Įkelkite CSV failą", type=["csv"])
xlsx_file = st.file_uploader("Įkelkite Excel failą", type=["xlsx"])

if csv_file and xlsx_file:
    try:
        df_csv = pd.read_csv(csv_file, encoding='utf-8')
    except UnicodeDecodeError:
        df_csv = pd.read_csv(csv_file, encoding='windows-1257')  # arba 'latin1'

    df_xlsx = pd.read_excel(xlsx_file)

    df_csv = df_csv[[
        'Prekės kodas',
        'Partija',
        'Galiojimo data',
        'Nerezervuotas kiekis',
        'Buhalterinis sandėlis'
    ]].copy()

    df_xlsx['Prekės kodas'] = df_xlsx['Prekė'].astype(str).str.split().str[0]

    df_xlsx = df_xlsx[[
        'Prekės kodas',
        'Objektas',
        'Serija',
        'Kiekis alt.matu',
        'Padalinys'
    ]].copy()

    df_csv['Galiojimo data'] = pd.to_datetime(df_csv['Galiojimo data'], errors='coerce').dt.date
    df_xlsx['Serija'] = pd.to_datetime(df_xlsx['Serija'], errors='coerce').dt.date

    df_merged = pd.merge(
        df_csv,
        df_xlsx,
        how='inner',
        left_on=['Prekės kodas', 'Partija', 'Galiojimo data', 'Buhalterinis sandėlis'],
        right_on=['Prekės kodas', 'Objektas', 'Serija', 'Padalinys']
    )

    df_merged['Kiekio skirtumas'] = df_merged['Nerezervuotas kiekis'] - df_merged['Kiekis alt.matu']

    st.success(f"Rasta atitikmenų: {len(df_merged)}")
    st.dataframe(df_merged)

    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Rezultatai')
        return output.getvalue()

    excel_data = to_excel(df_merged)
    st.download_button(
        label="📥 Atsisiųsti rezultatą (Excel)",
        data=excel_data,
        file_name='prekiu_palyginimas.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
