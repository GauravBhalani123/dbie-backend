import re

def analyze_advanced_lead(product_name: str, lead_data: dict, signals: list):
    product = product_name.lower()
    
    # Extract text from signals
    all_text = " ".join([s.get('value', '').lower() for s in signals])
    if lead_data.get('description'): all_text += " " + lead_data['description'].lower()
    if lead_data.get('industry'): all_text += " " + lead_data['industry'].lower()
    
    # Default outputs
    asset_prob = 0.0
    digital_score = 100.0
    operational_score = 0.0
    upgrade_prob = 0.0
    it_service_prob = 0.0
    hidden_need = False
    
    # ---------------------------------------------------------
    # PHASE 1: ASSET PRESENCE DETECTION
    # ---------------------------------------------------------
    if "weighbridge" in product or "scale" in product:
        if any(k in all_text for k in ['weighbridge', 'dharamkanta', '100 ton', 'truck weighing', 'weight slip', 'truck loading', 'weighing service']):
            asset_prob += 60
        if "operator" in all_text: asset_prob += 20
        if "truck" in all_text: asset_prob += 20
        
    elif "erp" in product or "software" in product:
        if any(k in all_text for k in ['inventory', 'billing', 'excel', 'tally']):
            asset_prob += 70
        if "accountant" in all_text or "executive" in all_text:
            asset_prob += 30
            
    elif "petrol" in product or "pump" in product:
        if any(k in all_text for k in ['fuel station', 'nozzle', 'tank', 'shift']):
            asset_prob += 80
            
    elif "pharma" in product:
        if any(k in all_text for k in ['batch', 'expiry', 'drug', 'schedule h']):
            asset_prob += 80
            
    elif "tap" in product or "plastic" in product:
        if any(k in all_text for k in ['hardware', 'sanitary', 'plumbing', 'bulk']):
            asset_prob += 80
            
    else:
        # Generic
        if "equipment" in all_text or "machinery" in all_text: asset_prob += 50

    asset_prob = min(100.0, asset_prob)

    # ---------------------------------------------------------
    # PHASE 2: DIGITAL MATURITY DETECTION
    # ---------------------------------------------------------
    if not lead_data.get('website'):
        digital_score -= 40
    if not any(k in all_text for k in ['cloud', 'api', 'erp', 'gst automation']):
        digital_score -= 30
    if any(k in all_text for k in ['manual slip', 'excel', 'paper']):
        digital_score -= 20
        
    digital_score = max(0.0, digital_score)
    
    digital_level = "HIGH"
    if digital_score < 75: digital_level = "MEDIUM"
    if digital_score < 50: digital_level = "LOW"
    if digital_score < 25: digital_level = "VERY LOW"

    # ---------------------------------------------------------
    # PHASE 3: OPERATIONAL COMPLEXITY
    # ---------------------------------------------------------
    if any(k in all_text for k in ['24x7', 'multiple branch', 'bulk', 'trucks', 'large yard']):
        operational_score += 40
    try:
        emp = int(re.sub(r'[^0-9]', '', str(lead_data.get('employee_size', '0'))) or 0)
        if emp > 50: operational_score += 30
        elif emp > 10: operational_score += 15
    except:
        pass
        
    operational_score = min(100.0, operational_score + 30) # Base 30
    
    op_volume = "HIGH" if operational_score >= 70 else "MEDIUM" if operational_score >= 40 else "LOW"

    # ---------------------------------------------------------
    # PHASE 4: SOFTWARE UPGRADE PROBABILITY
    # ---------------------------------------------------------
    if asset_prob > 0 and digital_level in ["LOW", "VERY LOW"] and op_volume == "HIGH":
        upgrade_prob = 85.0
    else:
        upgrade_prob = (asset_prob * 0.4) + ((100-digital_score) * 0.3) + (operational_score * 0.3)
        
    upgrade_prob = min(100.0, round(upgrade_prob, 2))

    # ---------------------------------------------------------
    # PHASE 5: HIDDEN NEED DETECTOR
    # ---------------------------------------------------------
    if any(k in all_text for k in ['steel trading', 'bulk supply', 'large loading']):
        if "weighbridge" not in all_text:
            hidden_need = True
            
    # ---------------------------------------------------------
    # PHASE 6: UNIVERSAL IT SERVICE DETECTION
    # ---------------------------------------------------------
    if any(k in all_text for k in ['migration', 'sap', 'tally', 'oracle', 'custom software', 'api']):
        it_service_prob += 50
    if any(k in all_text for k in ['inventory mismatch', 'manual process', 'old software']):
        it_service_prob += 30
        
    it_service_prob = min(100.0, it_service_prob)

    # ---------------------------------------------------------
    # PHASE 7: FINAL INTELLIGENCE OUTPUT
    # ---------------------------------------------------------
    final_score = max(upgrade_prob, it_service_prob)
    if hidden_need and "weighbridge" in product:
        final_score = max(final_score, 75.0)

    if final_score >= 75: category = "HOT"
    elif final_score >= 50: category = "WARM"
    else: category = "COLD"
    
    reasoning = []
    if asset_prob > 50: reasoning.append(f"Strong asset signals for {product_name}.")
    if digital_level in ["LOW", "VERY LOW"]: reasoning.append("Low digital maturity indicates need for upgrade.")
    if op_volume == "HIGH": reasoning.append("High operational volume requires automated systems.")
    if hidden_need: reasoning.append("Hidden need detected based on bulk operations.")
    if it_service_prob > 50: reasoning.append("Strong signals for IT service requirements.")

    return {
        "business_name": lead_data.get('name', 'Unknown'),
        "industry": lead_data.get('industry', 'Unknown'),
        "asset_presence_probability": asset_prob,
        "digital_maturity_score": digital_score,
        "operational_complexity_score": operational_score,
        "software_upgrade_probability": upgrade_prob,
        "it_service_need_probability": it_service_prob,
        "hidden_need_detected": hidden_need,
        "lead_category": category,
        "reasoning_summary": " ".join(reasoning) if reasoning else "Standard evaluation."
    }