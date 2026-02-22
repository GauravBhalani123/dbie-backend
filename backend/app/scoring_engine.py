def analyze_business(business, signals):
    industry_score = 50.0  # Base score
    asset_score = 0.0
    digital_score = 100.0  # Assumes High digital capability, subtract based on gaps
    operational_score = 30.0

    keywords = []
    infrastructures = []
    hirings = []
    
    for s in signals:
        val = s.value.lower()
        if s.signal_type == "keyword": keywords.append(val)
        elif s.signal_type == "infrastructure": infrastructures.append(val)
        elif s.signal_type == "hiring": hirings.append(val)
    
    # Asset Detection Logic
    for k in keywords:
        if any(x in k for x in ['weighbridge', 'dharamkanta', 'truck scale', 'ton']):
            asset_score += 30
    for i in infrastructures:
        if any(x in i for x in ['warehouse', 'yard', 'storage']):
            asset_score += 20
    for h in hirings:
        if 'operator' in h:
            asset_score += 15
            
    asset_score = min(100.0, asset_score)

    # Digital Gap Detection
    has_erp = any('erp' in k for k in keywords)
    if business.website and not has_erp:
        digital_score -= 30
    if not business.website:
        digital_score -= 50
        
    for h in hirings:
        if any(x in h for x in ['billing', 'accounting', 'data entry']):
            operational_score += 30
    
    digital_score = max(0.0, digital_score)
    operational_score = min(100.0, operational_score)

    # Need Probability
    need_score = (industry_score * 0.3) + (asset_score * 0.25) + (operational_score * 0.25) + ((100 - digital_score) * 0.2)
    need_score = min(100.0, round(need_score, 2))
    
    close_probability = round(need_score * 0.85, 2)
    
    if need_score >= 75: category = "Hot"
    elif need_score >= 50: category = "Warm"
    else: category = "Cold"
    
    recommendation = "Standard Follow up."
    if category == "Hot":
        recommendation = "High value target. Pitch direct system upgrade."

    return {
        "industry_score": industry_score,
        "asset_score": asset_score,
        "digital_score": digital_score,
        "operational_score": operational_score,
        "need_score": need_score,
        "close_probability": close_probability,
        "category": category,
        "recommendation": recommendation
    }