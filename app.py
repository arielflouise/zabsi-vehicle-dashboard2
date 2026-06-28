import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(page_title="Zabsi Vehicle Control", page_icon="🛻", layout="wide")

st.title("📊 ZABSI Fleet, Booking & Compliance System")
st.markdown("Sistem Log Penggunaan Kenderaan, Lokasi Projek, dan Pemantauan Tarikh Dokumen Syarikat.")

csv_file = "vehicle_data.csv"

if not os.path.exists(csv_file):
    st.error(f"Fail '{csv_file}' tidak dijumpai. Sila pastikan fail CSV berada di dalam folder project PyCharm.")
else:
    df = pd.read_csv(csv_file)

    # Tukar format lajur tarikh kepada datetime objek
    df["Tarikh Mula"] = pd.to_datetime(df["Tarikh Mula"], errors='coerce')
    df["Tarikh Tamat"] = pd.to_datetime(df["Tarikh Tamat"], errors='coerce')
    df["Road Tax Expiry"] = pd.to_datetime(df["Road Tax Expiry"], errors='coerce')
    df["Insurance Expiry"] = pd.to_datetime(df["Insurance Expiry"], errors='coerce')
    df["Puspakom Expiry"] = pd.to_datetime(df["Puspakom Expiry"], errors='coerce')

    today = datetime.datetime.now()

    # --- SECTION 1: MASTER DATA ENGINE ---
    st.subheader("📋 Log Induk Fleet Kenderaan")
    st.dataframe(df, width="stretch")

    st.markdown("---")

    # --- SECTION 2: CRITICAL COMPLIANCE ALERTS ---
    st.subheader("🚨 Amaran Pematuhan Dokumen (Compliance Alerts)")

    # Buat senarai armada unik berdasarkan no pendaftaran unik sahaja
    master_fleet = df[
        ["Kenderaan", "No. Pendaftaran", "Road Tax Expiry", "Insurance Expiry", "Puspakom Expiry"]].drop_duplicates(
        subset=["No. Pendaftaran"])

    comp_col1, comp_col2, comp_col3 = st.columns(3)

    with comp_col1:
        st.markdown("#### 🚗 Road Tax Status")
        for _, row in master_fleet.iterrows():
            if pd.notnull(row["Road Tax Expiry"]):
                days_left = (row["Road Tax Expiry"] - today).days
                plate = row["No. Pendaftaran"]
                name = row["Kenderaan"]

                if days_left < 0:
                    st.error(
                        f"🔴 **{plate}** ({name}) \n\n **EXPIRED** ({abs(days_left)} hari lalu) — Tamat: {row['Road Tax Expiry'].strftime('%d/%m/%Y')}")
                elif days_left <= 30:
                    st.warning(
                        f"🟡 **{plate}** ({name}) \n\n **Amaran:** Tinggal {days_left} hari! (Tamat: {row['Road Tax Expiry'].strftime('%d/%m/%Y')})")
                else:
                    st.success(f"🟢 **{plate}** — Aktif ({days_left} hari baki)")

    with comp_col2:
        st.markdown("#### 🛡️ Insurance Status")
        for _, row in master_fleet.iterrows():
            if pd.notnull(row["Insurance Expiry"]):
                days_left = (row["Insurance Expiry"] - today).days
                plate = row["No. Pendaftaran"]

                if days_left < 0:
                    st.error(f"🔴 **{plate}** \n\n **INSURANS MATI!** (Overdue {abs(days_left)} hari)")
                elif days_left <= 30:
                    st.warning(f"🟡 **{plate}** \n\n Renew segera ({days_left} hari baki)")
                else:
                    st.success(f"🟢 **{plate}** — Selamat")

    with comp_col3:
        st.markdown("#### 🚛 Puspakom (PPKM) Status")
        for _, row in master_fleet.iterrows():
            if pd.notnull(row["Puspakom Expiry"]):
                days_left = (row["Puspakom Expiry"] - today).days
                plate = row["No. Pendaftaran"]
                name = row["Kenderaan"]

                if days_left < 0:
                    st.error(f"🔴 **{plate}** ({name}) \n\n **PUSPAKOM OVERDUE** ({abs(days_left)} hari)")
                elif days_left <= 30:
                    st.warning(f"🟡 **{plate}** ({name}) \n\n Puspakom dalam {days_left} hari!")
                else:
                    st.success(f"🟢 **{plate}** — Sah")

    st.markdown("---")

    # --- SECTION 3: DAILY OPERATIONS TIMELINE ---
    st.subheader("⚡ Status Lokasi Pergerakan Projek (Hari Ini)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏃‍♂️ Kenderaan Aktif di Tapak Projek")
        active_count = 0
        for index, row in df.iterrows():
            if pd.notnull(row["Tarikh Mula"]) and pd.notnull(row["Tarikh Tamat"]):
                if row["Tarikh Mula"] <= today <= row["Tarikh Tamat"]:
                    st.info(f"🛻 **{row['Kenderaan']} ({row['No. Pendaftaran']})**\n\n"
                            f"📍 **Site Lokasi:** {row['Lokasi']} | 👤 **PIC:** {row['PIC']}\n\n"
                            f"⛽ **Bahan Bakar:** `{row['Jenis Minyak']}`")
                    active_count += 1
        if active_count == 0:
            st.write("Tiada pergerakan aktif dikesan untuk hari ini.")

    with col2:
        st.markdown("### ⚠️ Polisi Pengisian Minyak")
        st.warning("Sila pastikan pemandu melihat status jenis minyak sebelum mengisi.")
        st.info(
            "💡 **Tip:** Lori dan armada Navara menggunakan **DIESEL**. Kereta Saga, Bezza, Almera, BMW, serta Van menggunakan **PETROL**.")