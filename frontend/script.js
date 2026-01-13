const API = "http://127.0.0.1:8000";
let currentSymbol = "";
let currentRange = "1M";
let chartInstance = null;

function toggleView() {
    const isChecked = document.getElementById("viewToggle").checked;
    document.getElementById("chartSection").style.display = isChecked ? "none" : "block";
    document.getElementById("tableSection").style.display = isChecked ? "block" : "none";
}

async function load() {
    try {
        const res = await fetch(API + "/companies");
        const companies = await res.json();
        const list = document.getElementById("list");
        list.innerHTML = "";
        companies.forEach(c => {
            const li = document.createElement("li");
            li.innerText = c.symbol;
            li.onclick = () => {
                // UI Feedback immediately
                document.querySelectorAll("#list li").forEach(el => el.classList.remove("active"));
                li.classList.add("active");
                show(c.symbol);
            };
            list.appendChild(li);
        });
    } catch (e) { console.error("Failed to load list", e); }
}

function handleSearchKey(event) {
    const filter = document.getElementById("searchInput").value.toUpperCase();
    const li = document.getElementById("list").getElementsByTagName("li");
    for (let i = 0; i < li.length; i++) {
        li[i].style.display = li[i].innerText.toUpperCase().indexOf(filter) > -1 ? "" : "none";
    }
    if (event.key === "Enter") {
        const visible = document.querySelector("#list li:not([style*='display: none'])");
        if (visible) visible.click();
    }
}

// --- ROBUST SHOW FUNCTION ---
async function show(symbol) {
    currentSymbol = symbol;
    const loader = document.getElementById("loadingOverlay");

    // 1. Force Loader ON
    loader.style.visibility = "visible";
    loader.style.opacity = "1";

    try {
        // 2. Fetch Data (Wait for BOTH to finish)
        // We use Promise.allSettled so if one fails, the other still loads
        const [summaryRes, aiRes] = await Promise.all([
            fetch(`${API}/summary/${symbol}`),
            fetch(`${API}/predict/${symbol}`)
        ]);

        if (!summaryRes.ok) throw new Error("Could not fetch summary");

        const summary = await summaryRes.json();
        const ai = await aiRes.json();

        // 3. Update UI Text
        document.getElementById("title").innerText = summary.symbol;
        document.getElementById("price").innerText = "₹" + summary.current_price;
        document.getElementById("volatility").innerText = summary.volatility;

        const aiCard = document.getElementById("ai");
        if (ai.random_forest) {
            aiCard.innerHTML = `<div style="font-size:18px;">RF: ₹${ai.random_forest}</div><div style="font-size:12px; color:#888;">Linear: ₹${ai.linear}</div>`;
        } else { aiCard.innerText = "₹" + ai.prediction; }

        document.getElementById("high52").innerText = "₹" + summary.high_52;
        document.getElementById("low52").innerText = "₹" + (summary.low_52 || "-");

        const dRet = document.getElementById("dailyReturn");
        dRet.innerText = summary.daily_return + "%";
        dRet.style.color = summary.daily_return >= 0 ? "#00d09c" : "#eb5b3c";

        // 4. Render Chart & Table
        await Promise.all([
            renderApexChart(symbol, currentRange),
            loadTable(symbol, currentRange)
        ]);

    } catch (e) {
        console.error("Error showing data:", e);
        alert("First load delay. Please wait 3 seconds and click again.");
    } finally {
        // 5. Hide Loader ONLY when everything is done
        loader.style.opacity = "0";
        setTimeout(() => loader.style.visibility = "hidden", 300);
    }
}

async function renderApexChart(symbol, range) {
    try {
        const res = await fetch(`${API}/chart-data/${symbol}?time_range=${range}`);
        const rawData = await res.json();
        const chartType = document.getElementById("chartTypeSelector").value;

        if (chartInstance) { chartInstance.destroy(); }

        // Safe check for empty data
        if (!rawData || rawData.length === 0) return;

        const startPrice = rawData[0].y[3] || rawData[0].y;
        const endPrice = rawData[rawData.length - 1].y[3] || rawData[rawData.length - 1].y;
        const chartColor = endPrice >= startPrice ? '#00d09c' : '#eb5b3c';

        let seriesData = [];
        if (chartType === 'candlestick') {
            seriesData = rawData.map(d => ({ x: d.x, y: d.y }));
        } else {
            seriesData = rawData.map(d => ({ x: d.x, y: d.y[3] }));
        }

        const options = {
            series: [{ name: symbol, data: seriesData }],
            chart: { type: chartType, height: 400, toolbar: { show: true }, zoom: { enabled: true } },
            title: { text: undefined },
            xaxis: { type: 'category', tickAmount: 6, labels: { rotate: -45, formatter: (val) => val ? new Date(val).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }) : "" } },
            yaxis: { opposite: true, tooltip: { enabled: true } },
            stroke: { curve: 'smooth', width: 2, colors: [chartColor] },
            fill: { type: chartType === 'area' ? 'gradient' : 'solid', gradient: { opacityFrom: 0.5, opacityTo: 0.0 }, colors: [chartColor] },
            plotOptions: { candlestick: { colors: { upward: '#00d09c', downward: '#eb5b3c' } } }
        };

        chartInstance = new ApexCharts(document.querySelector("#chartBox"), options);
        chartInstance.render();
    } catch (err) { console.error("Chart Render Error", err); }
}

function changeChartType() {
    if (currentSymbol) renderApexChart(currentSymbol, currentRange);
}

async function loadTable(symbol, range) {
    const tbody = document.getElementById("tableBody");
    try {
        const res = await fetch(`${API}/data/${symbol}?time_range=${range}`);
        const data = await res.json();
        tbody.innerHTML = "";
        data.slice().reverse().forEach(row => {
            const tr = document.createElement("tr");
            const retVal = row.Daily_Return * 100;
            const turnover = (parseFloat(row.Close) * parseInt(row.Volume)) / 10000000;
            tr.innerHTML = `
                        <td>${row.Date}</td>
                        <td>${parseFloat(row.Open).toFixed(2)}</td>
                        <td>${parseFloat(row.High).toFixed(2)}</td>
                        <td>${parseFloat(row.Low).toFixed(2)}</td>
                        <td><strong>${parseFloat(row.Close).toFixed(2)}</strong></td>
                        <td>${parseInt(row.Volume).toLocaleString()}</td>
                        <td><span class="blur-value" title="Show">₹${turnover.toFixed(2)} Cr</span></td>
                        <td style="color:${retVal >= 0 ? '#00d09c' : '#eb5b3c'}">${retVal.toFixed(2)}%</td>
                    `;
            tbody.appendChild(tr);
        });
    } catch (e) { console.error("Table Error", e); }
}

async function updateChart(range, btn) {
    if (!currentSymbol) return;
    currentRange = range;
    document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');

    // Show loader slightly for feedback
    const loader = document.getElementById("loadingOverlay");
    loader.style.visibility = "visible"; loader.style.opacity = "0.5";

    await Promise.all([renderApexChart(currentSymbol, range), loadTable(currentSymbol, range)]);

    loader.style.opacity = "0";
    setTimeout(() => loader.style.visibility = "hidden", 200);
}

async function compareStocks() {
    const s1 = document.getElementById('comp1').value.toUpperCase();
    const s2 = document.getElementById('comp2').value.toUpperCase();
    if (!s1 || !s2) return alert("Please enter two symbols!");
    try {
        const res = await fetch(`${API}/compare?symbol1=${s1}&symbol2=${s2}`);
        const data = await res.json();
        alert(`🏆 WINNER: ${data.winner}\n${s1}: ${data.comparison[s1].average_return_30d}%\n${s2}: ${data.comparison[s2].average_return_30d}%`);
    } catch (e) { alert("Could not compare."); }
}

load();