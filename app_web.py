import os
import json
import streamlit as st
from datetime import datetime, date
import calendar

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_DATI = os.path.join(BASE_DIR, "edilizia_dati.txt")

# --- CARICAMENTO DATI ---
def carica_dati():
    if os.path.exists(FILE_DATI):
        try:
            with open(FILE_DATI, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"azienda": {"nome": "Azienda Edile"}, "operai": []}

def salva_dati(dati):
    with open(FILE_DATI, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=4, ensure_ascii=False)

st.set_page_config(page_title="EdilPresenze Mobile", page_icon="📱", layout="centered")

dati = carica_dati()
nome_az = dati.get("azienda", {}).get("nome", "EdilPresenze")

st.title(f"🏢 {nome_az}")
st.subheader("📱 Portale Operaio")

operai = dati.get("operai", [])
if not operai:
    st.warning("Nessun operaio registrato nel sistema.")
    st.stop()

# Selezione Operaio e Login con Password
if "logged_operaio" not in st.session_state:
    st.markdown("### 🔐 Accesso Dipendenti")
    nomi_operai = [op["nome"] for op in operai]
    op_scelto = st.selectbox("Seleziona il tuo nome:", nomi_operai)
    pwd_inserita = st.text_input("Inserisci la tua password personale:", type="password")

    if st.button("🔓 Accedi", use_container_width=True):
        operaio = next((o for o in operai if o["nome"] == op_scelto), None)
        if operaio and pwd_inserita == operaio.get("password", "123"):
            st.session_state["logged_operaio"] = operaio["id"]
            st.success("Accesso riuscito!")
            st.rerun()
        else:
            st.error("Password errata!")
else:
    # Ricarica i dati freschi dell'operaio loggato
    operaio_id = st.session_state["logged_operaio"]
    operaio = next((o for o in operai if o["id"] == operaio_id), None)
    
    if not operaio:
        del st.session_state["logged_operaio"]
        st.rerun()

    st.markdown(f"### Ciao, **{operaio['nome']}** 👋")
    
    # --- CREAZIONE SCHEDE (TABS) PER LO SMARTPHONE ---
    tab_timbra, tab_profilo, tab_storico = st.tabs(["⏱️ Timbratura", "👤 Il mio Profilo", "📅 Storico Presenze"])

    # --- TAB 1: TIMBRATURA ---
    with tab_timbra:
        st.markdown("#### Gestione Turno")
        stato_attuale = operaio.get("stato", "Assente")
        
        if stato_attuale == "In Servizio":
            st.info("🟢 Stato attuale: **IN SERVIZIO**")
        else:
            st.warning("🔴 Stato attuale: **NON IN SERVIZIO**")

        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🟢 INIZIA", use_container_width=True, disabled=(stato_attuale == "In Servizio")):
                ora_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                data_str = date.today().strftime("%Y-%m-%d")
                
                operaio["stato"] = "In Servizio"
                if data_str not in operaio.setdefault("giorni_presenti", []):
                    operaio["giorni_presenti"].append(data_str)
                
                operaio.setdefault("timbrature", []).append({"tipo": "Inizia", "orario": ora_str, "gps": "GPS Web: In Cantiere"})
                salva_dati(dati)
                st.success("Turno iniziato!")
                st.rerun()

        with col2:
            if st.button("🔴 TERMINA", use_container_width=True, disabled=(stato_attuale != "In Servizio")):
                ora_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                operaio["stato"] = "Terminato"
                operaio.setdefault("timbrature", []).append({"tipo": "Termina", "orario": ora_str, "gps": "GPS Web: Uscita"})
                salva_dati(dati)
                st.success("Turno terminato.")
                st.rerun()

        st.divider()
        if st.button("🔒 Esci (Logout)", type="secondary", use_container_width=True):
            del st.session_state["logged_operaio"]
            st.rerun()

    # --- TAB 2: PROFILO ---
    with tab_profilo:
        st.markdown("#### Dati Personali & Aziendali")
        st.markdown(f"**Mansione / Ruolo:** {operaio.get('ruolo', 'N/D')}")
        st.markdown(f"**Telefono:** {operaio.get('telefono', 'N/D')}")
        st.markdown(f"**Paga Oraria:** € {operaio.get('paga_oraria', 20.0):.2f}/h")
        st.markdown(f"**Documenti & Sicurezza:** {operaio.get('documenti', 'Verificati')} 🔒")

    # --- TAB 3: STORICO PRESENZE ---
    with tab_storico:
        st.markdown("#### Riepilogo Mese Corrente")
        
        data_oggi = date.today()
        anno, mese = data_oggi.year, data_oggi.month
        giorni_presenti = operaio.get("giorni_presenti", [])
        
        presenti_mese = 0
        assenti_mese = 0

        st.markdown(f"**Mese di {calendar.month_name[mese]} {anno}**")
        
        # Mostra giorno per giorno fino a oggi
        for g in range(1, data_oggi.day + 1):
            d_check = date(anno, mese, g)
            d_str = d_check.strftime("%Y-%m-%d")
            
            if d_str in giorni_presenti:
                st.markdown(f"🟢 **{d_check.strftime('%d/%m/%Y')}**: Presente in cantiere")
                presenti_mese += 1
            else:
                st.markdown(f"🔴 **{d_check.strftime('%d/%m/%Y')}**: Assente / Nessuna timbratura")
                assenti_mese += 1

        st.divider()
        col_a, col_b = st.columns(2)
        col_a.metric("Giorni Presenti", presenti_mese)
        col_b.metric("Giorni Assenti", assenti_mese)