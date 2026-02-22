def analyze_universal_need(product_name: str, business: dict, signals: list):
    product_name_lower = product_name.lower()
    
    # Defaults
    industry_score = 50.0
    asset_score = 0.0
    digital_score = 100.0
    operational_score = 30.0

    keywords = []
    infrastructures = []
    hirings = []
    reviews = []
    
    # Process inputs
    for s in signals:
        val = s['value'].lower()
        if s['signal_type'] == "keyword": keywords.append(val)
        elif s['signal_type'] == "infrastructure": infrastructures.append(val)
        elif s['signal_type'] == "hiring": hirings.append(val)
        elif s['signal_type'] == "review": reviews.append(val)

    # 1. LAYER 1: Asset Presence Detection (Dynamic Logic depending on Product)
    if "weighbridge" in product_name_lower or "scale" in product_name_lower:
        asset_keywords = ['weighbridge', 'dharamkanta', 'truck scale', 'ton', 'weighing', 'kanta']
        infra_keywords = ['warehouse', 'yard', 'storage', 'depot', 'factory', 'plant']
        hiring_keywords = ['operator', 'weighbridge', 'kanta wala']
    elif "pvc" in product_name_lower or "taps" in product_name_lower or "pipe" in product_name_lower:
        asset_keywords = ['hardware', 'sanitary', 'plumbing', 'construction', 'building material', 'wholesale']
        infra_keywords = ['godown', 'store room', 'warehouse', 'yard']
        hiring_keywords = ['salesman', 'loader', 'delivery']
    elif "erp" in product_name_lower or "software" in product_name_lower:
        asset_keywords = ['billing', 'invoice', 'gst', 'accounts', 'inventory', 'multi-branch', 'tally']
        infra_keywords = ['office', 'branches', 'headquarters']
        hiring_keywords = ['accountant', 'data entry', 'clerk', 'computer operator']
    else:
        # Generic asset detection
        asset_keywords = ['machinery', 'equipment', 'manufacturing', 'plant']
        infra_keywords = ['building', 'factory', 'warehouse']
        hiring_keywords = ['operator', 'technician', 'supervisor']

    # Apply weighted Asset match
    for k in keywords + reviews:
        if any(x in k for x in asset_keywords):
            asset_score += 25
    for i in infrastructures + reviews:
        if any(x in i for x in infra_keywords):
            asset_score += 20
    for h in hirings:
        if any(x in h for x in hiring_keywords):
            asset_score += 15

    asset_score = min(100.0, asset_score)

    # 2. LAYER 2: Digital Maturity Detection
    has_erp_or_cloud = any('erp' in k or 'cloud' in k or 'software' in k for k in keywords + reviews)
    has_api = any('api' in k or 'auto' in k for k in keywords)
    
    if business.get('website'):
        if not has_erp_or_cloud and not has_api:
            digital_score -= 30  # Website is just a brochure, likely outdated ops
    else:
        digital_score -= 50  # No digital footprint at all
        
    for h in hirings:
        if any(x in h for x in ['billing', 'accounting', 'data entry', 'manual', 'tally']):
            digital_score -= 20  # Relies heavily on manual data entries

    for r in reviews:
        if any(x in r for x in ['slip', 'manual', 'delay', 'wait', 'paper']):
            digital_score -= 25  # Reviews mention manual delays

    digital_score = max(0.0, digital_score)
    digital_gap = 100.0 - digital_score

    # 3. LAYER 3: Operational Complexity
    for i in infrastructures + remarks_list(business, reviews):
        if any(x in i for x in ['large', 'multiple', 'yard space', 'branches', 'godowns']):
            operational_score += 25
    
    for k in keywords + reviews:
        if any(x in k for x in ['bulk', 'wholesale', '24x7', 'trucks', 'heavy loading']):
            operational_score += 30

    try:
        emp_size = int(''.join(filter(str.isdigit, business.get('employee_size', '0'))))
        if emp_size > 50: operational_score += 20
        elif emp_size > 10: operational_score += 10
    except:
        pass

    operational_score = min(100.0, operational_score)

    # Industry specific boost (simplified for dynamic approach)
    industry_match = 50.0
    if product_name_lower[:3] in business.get('industry', '').lower():
        industry_match += 30

    # 4. LAYER 4: Need Probability Formula
    need_score = (
        (industry_match * 0.25) +
        (asset_score * 0.30) +
        (digital_gap * 0.25) +
        (operational_score * 0.20)
    )
    need_score = min(100.0, round(need_score, 2))

    # Close Probability considering digital gap scaling
    close_probability = round(need_score * 0.85, 2)

    if need_score >= 75: 
        category = "Hot"
    elif need_score >= 50: 
        category = "Warm"
    else: 
        category = "Cold"

    # AI Reasoning Logic
    inference_reason = []
    if asset_score > 50: inference_reason.append(f"Strong asset signals found relevant to {product_name}.")
    if digital_gap > 50: inference_reason.append("High digital gap indicates severe need for modern system.")
    if operational_score > 50: inference_reason.append("Complex operations require automated solutions.")
    
    reason = " ".join(inference_reason) if inference_reason else "Generic matching found."

    action = "Nurture with introductory emails."
    if category == "Hot":
        if digital_gap > 70:
            action = f"Call immediately. High chance of using manual systems. Pitch {product_name} as digital upgrade."
        else:
            action = f"Call and ask about current {product_name} efficiency & integration. Focus on operational scale."
    elif category == "Warm":
        action = "Send case studies regarding their specific industry pain points."

    return {
        "business_name": business.get('name', 'Unknown'),
        "asset_presence": asset_score,
        "digital_maturity": digital_score,
        "operational_complexity": operational_score,
        "product_need_probability": need_score,
        "close_probability": close_probability,
        "lead_category": category,
        "inference_reason": reason,
        "recommended_sales_action": action
    }

def remarks_list(business, reviews):
    l = list(reviews)
    if business.get('description'): l.append(business['description'].lower())
    if business.get('industry'): l.append(business['industry'].lower())
    return l