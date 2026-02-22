const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const DATA_FILE = path.join(__dirname, 'data', 'leads.json');

// Ensure data directory exists
if (!fs.existsSync(path.join(__dirname, 'data'))) {
    fs.mkdirSync(path.join(__dirname, 'data'));
}

// Initial DB setup
if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, JSON.stringify([]));
}

// Intelligence Logic
function analyzeBusiness(data) {
    let { 
        keywords = '', 
        infrastructure = '', 
        website = '', 
        cloudMention = false, 
        erpMention = false, 
        hiring = '', 
        size = '', 
        reviews = '' 
    } = data;
    
    keywords = keywords.toLowerCase();
    infrastructure = infrastructure.toLowerCase();
    website = website.toLowerCase();
    hiring = hiring.toLowerCase();
    reviews = reviews.toLowerCase();
    size = size.toLowerCase();

    // 1. Asset Presence Probability
    let assetScore = 20; // base score
    if (keywords.includes('weighbridge') || keywords.includes('dharamkanta') || keywords.includes('100 ton') || keywords.includes('wholesale')) assetScore += 30;
    if (reviews.includes('weighbridge') || reviews.includes('weighing') || reviews.includes('truck')) assetScore += 20;
    if (infrastructure.includes('yard') || infrastructure.includes('scale') || infrastructure.includes('warehouse')) assetScore += 20;
    if (hiring.includes('operator')) assetScore += 10;
    assetScore = Math.min(100, assetScore);

    // 2. Digital Maturity Level
    let digitalScore = 100; // Assume 100% digital gap originally, lower means more mature
    if (website.includes('modern') || cloudMention || erpMention) digitalScore -= 50;
    if (website && !website.includes('modern')) digitalScore -= 20; 
    if (hiring.includes('billing') || hiring.includes('software') || hiring.includes('accounting')) digitalScore -= 10;
    
    let digitalMaturity = 'Low';
    if (digitalScore < 40) digitalMaturity = 'High';
    else if (digitalScore < 80) digitalMaturity = 'Medium';

    // 3. Operational Complexity
    let complexityScore = 30; // base
    if (size.includes('large') || size.includes('multi')) complexityScore += 30;
    if (reviews.includes('trucks') || reviews.includes('volume') || keywords.includes('bulk') || keywords.includes('wholesale')) complexityScore += 20;
    if (infrastructure.includes('24x7') || infrastructure.includes('multiple branch')) complexityScore += 20;
    complexityScore = Math.min(100, complexityScore);

    // 4. Product Need Probability
    let needProbability = (assetScore * 0.4) + (digitalScore * 0.3) + (complexityScore * 0.3);
    needProbability = Math.round(Math.min(100, needProbability));

    // 5. Final Close Probability
    let closeProbability = Math.round(needProbability * 0.85); // Realistic dampening
    if (digitalMaturity === 'High') closeProbability -= 20; // Harder to sell to system that already exists

    // 6. Lead Category
    let category = 'Cold';
    if (needProbability > 75) category = 'Hot 🔥';
    else if (needProbability > 50) category = 'Warm 🌡️';

    // 7. Recommended Action
    let action = "Standard follow-up.";
    if (assetScore > 70 && digitalMaturity === 'Low') {
        action = "High chance manual system → pitch cloud solution. Ask: 'Tamari weighbridge / system ma remote access che ke manual slip print system che?'";
    } else if (complexityScore > 75) {
        action = "High transaction volume detected. Pitch multi-branch/ERP integration. Frame: 'Are you tracking bulk entries manually?'";
    }

    return {
        "Industry Match Score": Math.round((assetScore + complexityScore) / 2),
        "Asset Presence Probability": assetScore,
        "Digital Maturity Level": digitalMaturity,
        "Operational Complexity Score": complexityScore,
        "Product Need Probability": needProbability,
        "Final Close Probability": closeProbability,
        "Lead Category": category,
        "Recommended Sales Action": action
    };
}


// --- API Endpoints ---
app.post('/api/analyze', (req, res) => {
    try {
        const analysis = analyzeBusiness(req.body);
        
        const db = JSON.parse(fs.readFileSync(DATA_FILE));
        const newLead = { 
            id: Date.now().toString(),
            businessData: req.body, 
            analysis: analysis,
            createdAt: new Date().toISOString()
        };
        db.push(newLead);
        fs.writeFileSync(DATA_FILE, JSON.stringify(db, null, 2));

        res.json(newLead);
    } catch (error) {
        console.error("Error processing analysis:", error);
        res.status(500).json({ error: "Internal Server Error" });
    }
});

app.get('/api/leads', (req, res) => {
    try {
        const db = JSON.parse(fs.readFileSync(DATA_FILE));
        res.json(db.sort((a,b) => b.id - a.id));
    } catch (error) {
        res.status(500).json({ error: "Failed to read database" });
    }
});

app.listen(PORT, () => {
    console.log(`Deep Business Intelligence Engine running on http://localhost:${PORT}`);
});

// For Vercel Serverless Function export 
module.exports = app;
