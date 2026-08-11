import streamlit as st
import requests
import time

st.set_page_config(page_title="Arbitrage P2P Pro - USDT (XOF / XAF / EUR)", page_icon="⚡", layout="wide")

st.title("⚡ Moniteur d'Arbitrage P2P Professionnel (USDT)")
st.subheader("Bénin (XOF) ➔ Cameroun, Gabon et Europe (EUR)")

# Paramètres dans la barre latérale (Sidebar)
st.sidebar.header("⚙️ Configuration des Paramètres")
capital_depart = st.sidebar.number_input("Capital de départ (XOF)", value=100000, step=10000)

st.sidebar.subheader("💸 Frais de retour")
frais_retour_afrique = st.sidebar.slider("Frais retour Afrique (Cameroun/Gabon) (%)", min_value=0.0, max_value=10.0, value=6.0, step=0.5)
frais_retour_europe = st.sidebar.slider("Frais retour Europe (%)", min_value=0.0, max_value=10.0, value=4.0, step=0.5)

seuil_alerte = st.sidebar.slider("Seuil de rentabilité nette cible (%)", min_value=0.0, max_value=5.0, value=1.0, step=0.2)

auto_refresh = st.sidebar.checkbox("Activer l'auto-rafraîchissement (toutes les 60s)")
if auto_refresh:
    time.sleep(60)
    st.rerun()

def get_p2p_market_data(asset, fiat, trade_type, country_code=None):
    """Interroge l'API Binance P2P et retourne une liste de dictionnaires avec prix et stock"""
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    
    payload = {
        "asset": asset,
        "fiat": fiat,
        "merchantCheck": False,
        "page": 1,
        "payTypes": [],
        "rows": 5,
        "tradeType": trade_type
    }
    
    if country_code:
        payload["countries"] = [country_code]
        
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if data.get("success") and data.get("data"):
            results = []
            for item in data["data"]:
                price = float(item["adv"]["price"])
                surplus = float(item["adv"].get("surplusAmount", 0))
                results.append({"price": price, "stock": surplus})
            return results
    except Exception as e:
        pass
    return []

if st.button("Lancer l'analyse du marché USDT en direct", type="primary"):
    with st.spinner("Analyse des prix et des stocks USDT (XOF, XAF, EUR) en cours..."):
        
        # Données Bénin (XOF)
        benin_buy_data = get_p2p_market_data("USDT", "XOF", "BUY")
        
        # Données Cameroun (XAF - CM)
        cam_sell_data = get_p2p_market_data("USDT", "XAF", "SELL", country_code="CM")
        
        # Données Gabon (XAF - GA)
        gabon_sell_data = get_p2p_market_data("USDT", "XAF", "SELL", country_code="GA")
        
        # Données Europe (EUR)
        eur_sell_data = get_p2p_market_data("USDT", "EUR", "SELL")
        
        # Extractions sécurisées
        benin_buy_price = benin_buy_data[0]["price"] if benin_buy_data else 0
        benin_buy_stock = benin_buy_data[0]["stock"] if benin_buy_data else 0
        
        cam_sell_price = cam_sell_data[0]["price"] if cam_sell_data else 0
        cam_sell_stock = cam_sell_data[0]["stock"] if cam_sell_data else 0
        
        gabon_sell_price = gabon_sell_data[0]["price"] if gabon_sell_data else 0
        gabon_sell_stock = gabon_sell_data[0]["stock"] if gabon_sell_data else 0
        
        eur_sell_price = eur_sell_data[0]["price"] if eur_sell_data else 0
        eur_sell_stock = eur_sell_data[0]["stock"] if eur_sell_data else 0
        
        TAUX_EUR_XOF = 655.957

    st.success("Données actualisées avec succès pour toutes les zones !")
    
    # --- SECTION 1 : BÉNIN vers CAMEROUN ---
    st.markdown("### 🇨🇲 Simulation : Bénin (XOF) ➔ Cameroun (XAF)")
    if benin_buy_price > 0 and cam_sell_price > 0:
        quantite = capital_depart / benin_buy_price
        frais_reseau = 1.0
        quantite_nette = max(0, quantite - frais_reseau)
        total_cameroun = quantite_nette * cam_sell_price
        
        montant_apres_frais = total_cameroun * (1 - (frais_retour_afrique / 100))
        benefice_net = montant_apres_frais - capital_depart
        marge_nette_pct = (benefice_net / capital_depart) * 100
        
        col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
        with col1:
            st.text(f"Achat Bénin : {benin_buy_price:,.2f} XOF (Stock: {benin_buy_stock:,.2f})")
            st.text(f"Vente Cameroun : {cam_sell_price:,.2f} XAF (Stock: {cam_sell_stock:,.2f})")
        with col2:
            st.metric(label="Capital Final", value=f"{montant_apres_frais:,.0f} XOF")
        with col3:
            if benefice_net > 0:
                st.metric(label="Bénéfice Net", value=f"+{benefice_net:,.0f} XOF", delta=f"+{marge_nette_pct:.2f}%")
            else:
                st.metric(label="Bénéfice Net", value=f"{benefice_net:,.0f} XOF", delta=f"{marge_nette_pct:.2f}%", delta_color="inverse")
        with col4:
            if marge_nette_pct >= seuil_alerte:
                st.success("🔥 **CAMEROUN : Rentable !**")
            else:
                st.warning("⏳ Marge trop faible.")
    st.divider()

    # --- SECTION 2 : BÉNIN vers GABON ---
    st.markdown("### 🇬🇦 Simulation : Bénin (XOF) ➔ Gabon (XAF)")
    if benin_buy_price > 0 and gabon_sell_price > 0:
        quantite = capital_depart / benin_buy_price
        frais_reseau = 1.0
        quantite_nette = max(0, quantite - frais_reseau)
        total_gabon = quantite_nette * gabon_sell_price
        
        montant_apres_frais = total_gabon * (1 - (frais_retour_afrique / 100))
        benefice_net = montant_apres_frais - capital_depart
        marge_nette_pct = (benefice_net / capital_depart) * 100
        
        col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
        with col1:
            st.text(f"Achat Bénin : {benin_buy_price:,.2f} XOF (Stock: {benin_buy_stock:,.2f})")
            st.text(f"Vente Gabon : {gabon_sell_price:,.2f} XAF (Stock: {gabon_sell_stock:,.2f})")
        with col2:
            st.metric(label="Capital Final", value=f"{montant_apres_frais:,.0f} XOF")
        with col3:
            if benefice_net > 0:
                st.metric(label="Bénéfice Net", value=f"+{benefice_net:,.0f} XOF", delta=f"+{marge_nette_pct:.2f}%")
            else:
                st.metric(label="Bénéfice Net", value=f"{benefice_net:,.0f} XOF", delta=f"{marge_nette_pct:.2f}%", delta_color="inverse")
        with col4:
            if marge_nette_pct >= seuil_alerte:
                st.success("🔥 **GABON : Rentable !**")
            else:
                st.warning("⏳ Marge trop faible.")
    st.divider()

    # --- SECTION 3 : BÉNIN vers EUROPE (EUR) ---
    st.markdown("### 🇪🇺 Simulation : Bénin (XOF) ➔ Europe (EUR)")
    if benin_buy_price > 0 and eur_sell_price > 0:
        quantite = capital_depart / benin_buy_price
        frais_reseau = 1.0
        quantite_nette = max(0, quantite - frais_reseau)
        
        total_eur = quantite_nette * eur_sell_price
        total_xof_equivalent = total_eur * TAUX_EUR_XOF
        
        montant_apres_frais = total_xof_equivalent * (1 - (frais_retour_europe / 100))
        benefice_net = montant_apres_frais - capital_depart
        marge_nette_pct = (benefice_net / capital_depart) * 100
        
        col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
        with col1:
            st.text(f"Achat Bénin : {benin_buy_price:,.2f} XOF (Stock: {benin_buy_stock:,.2f})")
            st.text(f"Vente Europe : {eur_sell_price:,.2f} EUR (Stock: {eur_sell_stock:,.2f})")
        with col2:
            st.metric(label="Capital Final", value=f"{montant_apres_frais:,.0f} XOF")
        with col3:
            if benefice_net > 0:
                st.metric(label="Bénéfice Net", value=f"+{benefice_net:,.0f} XOF", delta=f"+{marge_nette_pct:.2f}%")
            else:
                st.metric(label="Bénéfice Net", value=f"{benefice_net:,.0f} XOF", delta=f"{marge_nette_pct:.2f}%", delta_color="inverse")
        with col4:
            if marge_nette_pct >= seuil_alerte:
                st.success("🔥 **EUROPE : Rentable !**")
            else:
                st.warning("⏳ Marge trop faible.")