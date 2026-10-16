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
            {"id": 1, "nome": "Cantiere Centro Storico", "indirizzo": "Via Roma 12", "stato": "Attivo"}
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

st.set_page_config(page_title="EdilPresenze Pro", page_icon="🏗️", layout="centered")

# --- STYLING CSS PERSONALIZZATO (DESIGN MODERNO SAAS) ---
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    h1, h2, h3 { color: #0F172A; font-family: 'Segoe UI', sans-serif; }
    </style>
""", unsafe_allow_html=True)

dati = carica_dati()
nome_az = dati.get("azienda", {}).get("nome", "EdilPresenze Pro")

if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

# ==========================================
# 1. SCHERMATA DI LOGIN PRINCIPALE
# ==========================================
if st.session_state["user_role"] is None:
    st.markdown(f"<h1 style='text-align: center; color: #1E293B;'>🏗️ {nome_az}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B;'>Portale Cloud Gestione Presenze & Cantieri</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 10, 1])
    with col_l2:
        with st.container():
            st.markdown("### 🔐 Accesso al Sistema")
            tipo_accesso = st.radio("Seleziona profilo:", ["📱 Operaio / Dipendente", "🔑 Amministratore (Admin)"], label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)

            if tipo_accesso == "📱 Operaio / Dipendente":
                operai = dati.get("operai", [])
                if not operai:
                    st.warning("Nessun operaio registrato.")
                else:
                    nomi_operai = [op["nome"] for op in operai]
                    op_scelto = st.selectbox("Seleziona il tuo nome:", nomi_operai)
                    pwd_inserita = st.text_input("Password personale:", type="password")

                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🚀 Accedi come Operaio", use_container_width=True, type="primary"):
                        operaio = next((o for o in operai if o["nome"] == op_scelto), None)
                        if operaio and pwd_inserita == operaio.get("password", "123"):
                            st.session_state["user_role"] = "operaio"
                            st.session_state["logged_operaio_id"] = operaio["id"]
                            st.rerun()
                        else:
                            st.error("Password errata!")

            else:
                pwd_admin = st.text_input("Password Amministratore:", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔑 Accedi alla Dashboard Admin", use_container_width=True, type="primary"):
                    pwd_salvata = dati.get("azienda", {}).get("admin_password", "admin")
                    if pwd_admin == pwd_salvata:
                        st.session_state["user_role"] = "admin"
                        st.rerun()
                    else:
                        st.error("Password Admin errata!")

# ==========================================
# 2. PANNELLO OPERAIO (MOBILE OPTIMIZED)
# ==========================================
elif st.session_state["user_role"] == "operaio":
    operai = dati.get("operai", [])
    operaio_id = st.session_state.get("logged_operaio_id")
    operaio = next((o for o in operai if o["id"] == operaio_id), None)

    if not operaio:
        st.session_state["user_role"] = None
        st.rerun()

    st.markdown(f"### 👋 Ciao, **{operaio['nome']}**")
    
    tab_timbra, tab_profilo, tab_storico = st.tabs(["⏱️ Timbratura", "👤 Profilo", "📅 Storico"])

    with tab_timbra:
        st.markdown("<br>", unsafe_allow_html=True)
        stato_attuale = operaio.get("stato", "Assente")
        
        if stato_attuale == "In Servizio":
            st.markdown("<div style='text-align: center; padding: 15px; background-color: #DCFCE7; border-radius: 10px; color: #166534; font-weight: bold;'>🟢 STATO: IN SERVIZIO IN CANTIERE</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align: center; padding: 15px; background-color: #FEE2E2; border-radius: 10px; color: #991B1B; font-weight: bold;'>🔴 STATO: NON IN SERVIZIO</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🟢 INIZIA TURNO", use_container_width=True, disabled=(stato_attuale == "In Servizio")):
                ora_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                data_str = date.today().strftime("%Y-%m-%d")
                operaio["stato"] = "In Servizio"
                if data_str not in operaio.setdefault("giorni_presenti", []):
                    operaio["giorni_presenti"].append(data_str)
                operaio.setdefault("timbrature", []).append({"tipo": "Inizia", "orario": ora_str, "gps": "GPS Cloud"})
                salva_dati(dati)
                st.success("Turno avviato!")
                st.rerun()

        with col2:
            if st.button("🔴 TERMINA", use_container_width=True, disabled=(stato_attuale != "In Servizio")):
                ora_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                operaio["stato"] = "Terminato"
                operaio.setdefault("timbrature", []).append({"tipo": "Termina", "orario": ora_str, "gps": "GPS Cloud"})
                salva_dati(dati)
                st.success("Turno terminato.")
                st.rerun()

    with tab_profilo:
        st.markdown(f"""
        * **Mansione:** {operaio.get('ruolo', 'N/D')}
        * **Telefono:** {operaio.get('telefono', 'N/D')}
        * **Paga Oraria:** € {operaio.get('paga_oraria', 20.0):.2f}/h
        """)

    with tab_storico:
        st.markdown("#### Riepilogo Mese Corrente")
        data_oggi = date.today()
        anno, mese = data_oggi.year, data_oggi.month
        giorni_presenti = operaio.get("giorni_presenti", [])
        
        for g in range(1, data_oggi.day + 1):
            d_check = date(anno, mese, g)
            d_str = d_check.strftime("%Y-%m-%d")
            if d_str in giorni_presenti:
                st.markdown(f"🟢 **{d_check.strftime('%d/%m/%Y')}** — Presente")
            else:
                st.markdown(f"🔴 **{d_check.strftime('%d/%m/%Y')}** — Assente")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🔒 Disconnetti (Logout)", use_container_width=True):
        st.session_state["user_role"] = None
        st.rerun()

# ==========================================
# 3. PANNELLO ADMIN (DASHBOARD DIREZIONALE)
# ==========================================
elif st.session_state["user_role"] == "admin":
    st.markdown("### 📊 Dashboard Amministratore")

    tab_dash, tab_cantieri, tab_operai, tab_report = st.tabs(["📊 Panoramica", "🏗️ Cantieri", "👥 Operai", "📄 Report & Presenze"])

    with tab_dash:
        operai = dati.get("operai", [])
        cantieri = dati.get("cantieri", [])
        
        presenti = sum(1 for op in operai if op.get("stato") == "In Servizio")
        cantieri_attivi = sum(1 for c in cantieri if c.get("stato", "Attivo") == "Attivo")

        col_a, col_b = st.columns(2)
        col_a.metric("👷‍♂️ Presenti Oggi", presenti)
        col_b.metric("🏗️ Cantieri Attivi", cantieri_attivi)

        st.markdown("#### Stato Dipendenti in Tempo Reale")
        for op in operai:
            badge = "🟢 In Servizio" if op.get("stato") == "In Servizio" else "⚪ Non in Servizio"
            st.markdown(f"* **{op['nome']}** ({op['ruolo']}) — `{badge}`")

    with tab_cantieri:
        st.markdown("#### Gestione Cantieri")
        for c in dati.get("cantieri", []):
            st_col = "🟢 Attivo" if c.get("stato", "Attivo") == "Attivo" else "🔴 Terminato"
            col_1, col_2 = st.columns([3, 1])
            with col_1:
                st.markdown(f"**{c['nome']}**<br><small style='color: #64748B;'>{c['indirizzo']} — {st_col}</small>", unsafe_allow_html=True)
            with col_2:
                if st.button("Cambia Stato", key=f"c_{c['id']}"):
                    c["stato"] = "Terminato" if c.get("stato", "Attivo") == "Attivo" else "Attivo"
                    salva_dati(dati)
                    st.rerun()

        st.divider()
        st.markdown("#### ➕ Aggiungi Cantiere")
        nuovo_nome = st.text_input("Nome Cantiere")
        nuova_via = st.text_input("Indirizzo")
        if st.button("Salva Cantiere", type="primary"):
            if nuovo_nome:
                new_id = max([c["id"] for c in dati.get("cantieri", [])], default=0) + 1
                dati.setdefault("cantieri", []).append({"id": new_id, "nome": nuovo_nome, "indirizzo": nuova_via, "stato": "Attivo"})
                salva_dati(dati)
                st.success("Cantiere aggiunto!")
                st.rerun()

    with tab_operai:
        st.markdown("#### Gestione Dipendenti")
        for op in dati.get("operai", []):
            st.markdown(f"* **{op['nome']}** ({op['ruolo']}) | Password: `{op.get('password','123')}` | Paga: **€{op.get('paga_oraria',20.0):.2f}/h**")

        st.divider()
        st.markdown("#### ➕ Registra Nuovo Operaio")
        n_nome = st.text_input("Nome e Cognome")
        n_ruolo = st.text_input("Ruolo", "Muratore")
        n_pwd = st.text_input("Password Personale Mobile", "123")
        n_paga = st.number_input("Paga Oraria (€/h)", value=20.0)

        if st.button("Salva Operaio", type="primary"):
            if n_nome and n_pwd:
                op_id = max([o["id"] for o in dati.get("operai", [])], default=0) + 1
                dati.setdefault("operai", []).append({
                    "id": op_id, "nome": n_nome, "ruolo": n_ruolo, "password": n_pwd,
                    "paga_oraria": n_paga, "stato": "Assente", "giorni_presenti": [], "timbrature": []
                })
                salva_dati(dati)
                st.success("Operaio registrato con successo!")
                st.rerun()

    with tab_report:
        st.markdown("#### 📄 Report e Storico Presenze Aziendali")
        
        # 1. Report Giornaliero
        st.markdown("##### 📌 Report della Giornata Odierna")
        data_oggi_str = datetime.now().strftime("%Y-%m-%d")
        
        testo_report = f"=== REPORT GIORNATA: {datetime.now().strftime('%d/%m/%Y')} ===\n\n"
        costo_totale_giorno = 0.0

        for op in dati.get("operai", []):
            paga = op.get("paga_oraria", 20.0)
            ore_lavorate = 0.0
            ultimo_inizio = None
            
            for t in op.get("timbrature", []):
                if t["orario"].startswith(data_oggi_str):
                    if t["tipo"] == "Inizia":
                        try:
                            ultimo_inizio = datetime.strptime(t["orario"], "%Y-%m-%d %H:%M")
                        except:
                            pass
                    elif t["tipo"] == "Termina" and ultimo_inizio:
                        try:
                            fine = datetime.strptime(t["orario"], "%Y-%m-%d %H:%M")
                            delta = fine - ultimo_inizio
                            ore_lavorate += delta.total_seconds() / 3600.0
                            ultimo_inizio = None
                        except:
                            pass

            if ore_lavorate == 0.0 and data_oggi_str in op.get("giorni_presenti", []):
                ore_lavorate = 8.0  # stima standard giornaliera se in servizio

            costo_op = ore_lavorate * paga
            costo_totale_giorno += costo_op

            testo_report += f"• {op['nome']} ({op['ruolo']})\n"
            testo_report += f"  Stato: {op.get('stato')} | Ore: {ore_lavorate:.1f}h | Costo: €{costo_op:.2f}\n\n"

        testo_report += f"COSTO TOTALE GIORNATA: €{costo_totale_giorno:.2f}"
        
        st.text_area("Anteprima Testo Report Giornaliero:", value=testo_report, height=180)
        
        # 2. Storico presenze operai per il mese
        st.markdown("---")
        st.markdown("##### 📅 Dettaglio Presenze Mensili per Operaio")
        
        data_corrente = date.today()
        anno, mese = data_corrente.year, data_corrente.month
        
        for op in dati.get("operai", []):
            giorni_presenti = op.get("giorni_presenti", [])
            presenti_mese = sum(1 for d in giorni_presenti if d.startswith(f"{anno}-{mese:02d}"))
            
            with st.expander(f"👷‍♂️ {op['nome']} — {presenti_mese} giorni presenti nel mese di {calendar.month_name[mese]}"):
                for g in range(1, data_corrente.day + 1):
                    d_chk = date(anno, mese, g)
                    d_str = d_chk.strftime("%Y-%m-%d")
                    if d_str in giorni_presenti:
                        st.markdown(f"🟢 **{d_chk.strftime('%d/%m/%Y')}**: Presente")
                    else:
                        st.markdown(f"🔴 **{d_chk.strftime('%d/%m/%Y')}**: Assente")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🔒 Logout Admin", use_container_width=True):
        st.session_state["user_role"] = None
        st.rerun()
