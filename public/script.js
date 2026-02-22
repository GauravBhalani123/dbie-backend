document.addEventListener('DOMContentLoaded', () => {
    fetchLeads();

    document.getElementById('intelligenceForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const btnSpinner = document.getElementById('btnSpinner');
        const btnText = document.querySelector('.primary-btn span');
        btnSpinner.style.display = 'block';
        btnText.style.display = 'none';

        const data = {
            businessName: document.getElementById('businessName').value,
            keywords: document.getElementById('keywords').value,
            infrastructure: document.getElementById('infrastructure').value,
            website: document.getElementById('website').value,
            hiring: document.getElementById('hiring').value,
            size: document.getElementById('size').value,
            reviews: document.getElementById('reviews').value,
            cloudMention: document.getElementById('cloudMention').checked,
            erpMention: document.getElementById('erpMention').checked
        };

        try {
            const res = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await res.json();

            displayResults(result.analysis);
            document.getElementById('resultsSection').style.display = 'block';

            // Re-fetch leads
            fetchLeads();

            // Scroll to results
            document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
        } catch (error) {
            console.error("Error analyzing:", error);
            alert("Error analyzing the business. Check console.");
        } finally {
            btnSpinner.style.display = 'none';
            btnText.style.display = 'block';
        }
    });
});

function displayResults(analysis) {
    // Basic fields
    document.getElementById('assetScore').innerText = analysis["Asset Presence Probability"] + "%";
    document.getElementById('digitalScore').innerText = analysis["Digital Maturity Level"];
    document.getElementById('complexityScore').innerText = analysis["Operational Complexity Score"] + "%";
    document.getElementById('upgradeScore').innerText = analysis["Product Need Probability"] + "%";
    document.getElementById('recommendedAction').innerText = analysis["Recommended Sales Action"];

    // Category Badge
    const badge = document.getElementById('leadCategoryBadge');
    badge.innerText = analysis["Lead Category"];
    badge.className = 'badge'; // reset
    if (analysis["Lead Category"].includes('Hot')) {
        badge.classList.add('hot');
    } else if (analysis["Lead Category"].includes('Warm')) {
        badge.classList.add('warm');
    } else {
        badge.classList.add('cold');
    }

    // Progressbars (delay for animation effect)
    setTimeout(() => {
        document.getElementById('assetBar').style.width = analysis["Asset Presence Probability"] + "%";
        document.getElementById('complexityBar').style.width = analysis["Operational Complexity Score"] + "%";
    }, 100);
}

async function fetchLeads() {
    try {
        const res = await fetch('/api/leads');
        const leads = await res.json();

        const tbody = document.getElementById('leadsBody');
        tbody.innerHTML = '';

        if (leads.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">No leads evaluated yet. Start analyzing!</td></tr>';
            return;
        }

        leads.forEach(lead => {
            const tr = document.createElement('tr');

            let categoryClass = 'cold';
            if (lead.analysis["Lead Category"].includes('Hot')) categoryClass = 'hot';
            else if (lead.analysis["Lead Category"].includes('Warm')) categoryClass = 'warm';

            tr.innerHTML = `
                <td><strong>${lead.businessData.businessName}</strong></td>
                <td>${lead.analysis["Product Need Probability"]}%</td>
                <td><span class="badge ${categoryClass}">${lead.analysis["Lead Category"]}</span></td>
                <td style="color: #8b949e; font-size: 0.85rem">${new Date(lead.createdAt).toLocaleString()}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Failed to fetch leads:", error);
    }
}
