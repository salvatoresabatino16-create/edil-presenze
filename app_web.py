import os
import json
import streamlit as st
from datetime import datetime, date
import calendar

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_DATI = os.path.join(BASE_DIR, "edilizia_dati.txt")

# --- CARICAMENTO E SALVATAGGIO DATI ---
def carica_dati():
    if os.path.exists(FILE_DATI):
        try:
            with open(FILE_DATI, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "azienda": {"nome": "Edilizia Costruzioni S.R.L.", "admin_password": "admin"},
        "cantieri": [
            {"id": 1, "nome": "Cantiere Centro", "indirizzo": "Via Roma 12", "materiali_costo": 12500.0, "stato": "Attivo"}
        ],
        "operai": [
            {
                "id": 1, "nome": "Mario Rossi", "ruolo": "Capomastro", "cantiere_id": 1,
                "stato": "Assente", "telefono": "333-1234567", "paga_oraria": 25.0,
                "password": "123", "giorni_presenti": [], "timbrature": []
            }
        ]
    }

def salva_dati(dati):
    with open(FILE_DATI, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=4, ensure_ascii=False)

st.set_page_config(page_title="EdilPresenze Pro Cloud", page_icon="🏢", layout="centered")

dati = carica_dati()
nome_az = dati.get("azienda", {}).get("nome", "EdilPresenze Pro")

# --- HEADER PRINCIPALE ---
st.title(f"🏢 {nome_az}")

# --- GESTIONE SESSIONI DI LOGIN ---
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None  # Può essere 'admin' o 'operaio'

# ==========================================
# 1. SCHERMATA DI LOGIN
# ==========================================
if st.session_state["user_role"] is None:
    st.subheader("🔐 Portale di Accesso")
    
    tipo_accesso = st.radio("Seleziona il tuo profilo:", ["📱 Operaio / Dipendente", "🔑 Amministratore (Admin)"], horizontal=True)

    if tipo_accesso == "📱 Operaio / Dipendente":
        st.markdown("---")
        operai = dati.get("operai", [])
        if not operai:
            st.warning("Nessun operaio registrato nel sistema.")
        else:
            nomi_operai = [op["nome"] for op in operai]
            op_scelto = st.selectbox("Seleziona il tuo nome:", nomi_operai)
            pwd_inserita = st.text_input("Inserisci la tua password personale:", type="password")

            if st.button("🔓 Accedi Operaio", use_container_width=True):
                operaio = next((o for o in operai if o["nome"] == op_scelto), None)
                if operaio and pwd_inserita == operaio.get("password", "123"):
                    st.session_state["user_role"] = "operaio"
                    st.session_state["logged_operaio_id"] = operaio["id"]
                    st.success("Accesso riuscito!")
                    st.rerun()
                else:
                    st.error("Password errata!")

    else:
        st.markdown("---")
        pwd_admin = st.text_input("Inserisci Password Amministratore:", type="password")
        if st.button("🔑 Accedi alla Dashboard Admin", use_container_width=True):
            pwd_salvata = dati.get("azienda", {}).get("admin_password", "admin")
            if pwd_admin == pwd_salvata:
                st.session_state["user_role"] = "admin"
                st.success("Accesso Amministratore autorizzato!")
                st.rerun()
            else:
                st.error("Password Amministratore errata!")

# ==========================================
# 2. PANNELLO OPERAIO
# ==========================================
elif st.session_state["user_role"] == "operaio":
    operai = dati.get("operai", [])
    operaio_id = st.session_state.get("logged_operaio_id")
    operaio = next((o for o in operai if o["id"] == operaio_id), None)

    if not operaio:
        st.session_state["user_role"] = None
        st.rerun()

    st.markdown(f"### Ciao, **{operaio['nome']}** 👋")
    
    tab_timbra, tab_profilo, tab_storico = st.tabs(["⏱️ Timbratura", "👤 Il mio Profilo", "📅 Storico Presenze"])

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

    with tab_profilo:
        st.markdown(f"**Mansione:** {operaio.get('ruolo', 'N/D')}")
        st.markdown(f"**Telefono:** {operaio.get('telefono', 'N/D')}")
        st.markdown(f"**Paga Oraria:** € {operaio.get('paga_oraria', 20.0):.2f}/h")

    with tab_storico:
        st.markdown("#### Riepilogo Mese Corrente")
        data_oggi = date.today()
        anno, mese = data_oggi.year, data_oggi.month
        giorni_presenti = operaio.get("giorni_presenti", [])
        for g in range(1, data_oggi.day + 1):
            d_check = date(anno, mese, g)
            d_str = d_check.strftime("%Y-%m-%d")
            if d_str in giorni_presenti:
                st.markdown(f"🟢 **{d_check.strftime('%d/%m/%Y')}**: Presente in cantiere")
            else:
                st.markdown(f"🔴 **{d_check.strftime('%d/%m/%Y')}**: Assente / Nessuna timbratura")

    st.divider()
    if st.button("🔒 Logout Operaio", type="secondary"):
        st.session_state["user_role"] = None
        st.rerun()

# ==========================================
# 3. PANNELLO AMMINISTRATORE (ADMIN DASHBOARD)
# ==========================================
elif st.session_state["user_role"] == "admin":
    st.subheader("📊 Dashboard Amministratore")

    tab_dash, tab_cantieri, tab_operai = st.tabs(["📊 Panoramica", "🏗️ Gestione Cantieri", "👥 Gestione Operai"])

    # --- TAB 1: PANORAMICA ---
    with tab_dash:
        operai = dati.get("operai", [])
        cantieri = dati.get("cantieri", [])
        
        presenti = sum(1 for op in operai if op.get("stato") == "In Servizio")
        cantieri_attivi = sum(1 for c in cantieri if c.get("stato", "Attivo") == "Attivo")

        col_a, col_b = st.columns(2)
        col_a.metric("Presenti in Cantiere", presenti)
        col_b.metric("Cantieri Attivi", cantieri_attivi)

        st.markdown("#### Status Operai in Tempo Reale")
        for op in operai:
            st_text = "🟢 In Servizio" if op.get("stato") == "In Servizio" else "🔴 Non in Servizio"
            st.markdown(f"• **{op['nome']}** ({op['ruolo']}) — {st_text}")

    # --- TAB 2: CANTIERI ---
    with tab_cantieri:
        st.markdown("#### Lista Cantieri")
        for c in dati.get("cantieri", []):
            st_col = "🟢 Attivo" if c.get("stato", "Attivo") == "Attivo" else "🔴 Terminato"
            col_1, col_2 = st.columns([3, 1])
            with col_1:
                st.markdown(f"**{c['nome']}** - {c['indirizzo']} ({st_col})")
            with col_2:
                if st.button("Termina/Riattiva", key=f"cantiere_{c['id']}"):
                    c["stato"] = "Terminato" if c.get("stato", "Attivo") == "Attivo" else "Attivo"
                    salva_dati(dati)
                    st.rerun()

        st.divider()
        st.markdown("#### ➕ Aggiungi Nuovo Cantiere")
        nuovo_nome = st.text_input("Nome Cantiere:")
        nuova_via = st.text_input("Indirizzo:")
        if st.button("Salva Nuovo Cantiere"):
            if nuovo_nome:
                new_id = max([c["id"] for c in dati.get("cantieri", [])], default=0) + 1
                dati.setdefault("cantieri", []).append({
                    "id": new_id, "nome": nuovo_nome, "indirizzo": nuova_via, "stato": "Attivo", "materiali_costo": 0.0
                })
                salva_dati(dati)
                st.success(f"Cantiere '{nuovo_nome}' creato!")
                st.rerun()

    # --- TAB 3: OPERAI ---
    with tab_operai:
        st.markdown("#### Operai Registrati & Credenziali")
        for op in dati.get("operai", []):
            st.markdown(f"👷‍♂️ **{op['nome']}** | Password: `{op.get('password','123')}` | Paga: €{op.get('paga_oraria',20.0):.2f}/h")

        st.divider()
        st.markdown("#### ➕ Registra Nuovo Operaio")
        n_nome = st.text_input("Nome e Cognome Operaio:")
        n_ruolo = st.text_input("Ruolo / Mansione:", "Muratore Specializzato")
        n_pwd = st.text_input("Password Personale (per Login Mobile):", "123")
        n_paga = st.number_input("Paga Oraria (€/h):", value=20.0)

        if st.button("Salva Nuovo Operaio"):
            if n_nome and n_pwd:
                op_id = max([o["id"] for o in dati.get("operai", [])], default=0) + 1
                dati.setdefault("operai", []).append({
                    "id": op_id, "nome": n_nome, "ruolo": n_ruolo, "password": n_pwd,
                    "paga_oraria": n_paga, "stato": "Assente", "giorni_presenti": [], "timbrature": []
                })
                salva_dati(dati)
                st.success(f"Operaio {n_nome} registrato!")
                st.rerun()

    st.divider()
    if st.button("🔒 Logout Admin", type="secondary"):
        st.session_state["user_role"] = None
        st.rerun()
