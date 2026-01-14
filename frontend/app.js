
const API = "http://127.0.0.1:8000";
let currentSymbol = "";
let currentRange = "1M";
let chartInstance = null;
let cachedReturns = {}; // Store so return instantly

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
                document.querySelectorAll("#list li").forEach(el => el.classList.remove("active"));
                li.classList.add("active");
                show(c.symbol);
            };
            list.appendChild(li);
        });
    } catch (e) { console.error(e); }
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

async function show(symbol) {
    currentSymbol = symbol;
    const loader = document.getElementById("loadingOverlay");
    loader.style.visibility = "visible"; loader.style.opacity = "1";

    try {
        const [summaryRes, aiRes] = await Promise.all([
            fetch(`${API}/summary/${symbol}`),
            fetch(`${API}/predict/${symbol}`)
        ]);

        if (!summaryRes.ok) throw new Error("Fetch failed");
        const summary = await summaryRes.json();
        const ai = await aiRes.json();

        // STORE RETURNS GLOBALLY
        cachedReturns = summary.returns;

        document.getElementById("title").innerText = summary.symbol;
        document.getElementById("price").innerText = "₹" + summary.current_price;
        document.getElementById("analystInsight").innerHTML = summary.insight;

        // Update Volatility Card
        const volCard = document.getElementById("volatility");
        volCard.innerHTML = `<div style="color:${summary.risk_color}; font-size:20px; font-weight:bold;">${summary.risk_label}</div><div style="font-size:11px; color:#888;">Score: ${summary.volatility}</div>`;

        // Update Returns Card (Default to 1M)
        updateReturnCard("1M");

        const aiCard = document.getElementById("ai");
        if (ai.random_forest) {
            aiCard.innerHTML = `<div style="font-size:20px; font-weight:bold;">₹${ai.random_forest}</div><div style="font-size:11px; color:#888; font-weight:normal;">Linear Model: ₹${ai.linear}</div>`;
        } else { aiCard.innerText = "₹" + ai.prediction; }

        document.getElementById("high52").innerText = "₹" + summary.high_52;
        document.getElementById("low52").innerText = "₹" + (summary.low_52 || "-");

        const dRet = document.getElementById("dailyReturn");
        dRet.innerText = (summary.returns["1D"] || 0) + "%"; // Use 1D return if available or calc manually

        document.getElementById("comp1").value = symbol;

        await Promise.all([renderApexChart(symbol, currentRange), loadTable(symbol, currentRange)]);
    } catch (e) {
        console.error(e);
    } finally {
        loader.style.opacity = "0";
        setTimeout(() => loader.style.visibility = "hidden", 250);
    }
}

// --- Updates Return Card based on Range ---
// --- Shows % and ₹ ---
function updateReturnCard(range) {
    if (!cachedReturns) return;

    // Get data for the selected range
    let data = cachedReturns[range];

    // Fallback for missing data
    if (!data) {
        // Try to fallback to 1W if a specific range is missing
        data = cachedReturns['1W'] || { percent: 0, value: 0 };
    }

    const label = document.getElementById("returnLabel");
    const valueElem = document.getElementById("periodReturn");

    label.innerText = `${range} Return`;

    const pct = data.percent;
    const val = data.value;

    // Format: +5.20% (+₹120.50)
    const sign = pct >= 0 ? "+" : "";
    const color = pct >= 0 ? "#00d09c" : "#ff4444"; // Green or Red

    valueElem.innerHTML = `
                <span style="color:${color}">${sign}${pct.toFixed(2)}%</span>
                <span style="font-size:14px; color:#888; font-weight:normal; margin-left:5px;">
                    (${sign}₹${val.toFixed(2)})
                </span>
            `;
}

async function renderApexChart(symbol, range) {
    try {
        let seriesData = [];
        let rawData = [];
        let isIntraday = (range === '1D');

        if (isIntraday) {
            const res = await fetch(`${API}/live-data/${symbol}`);
            const liveData = await res.json();
            seriesData = liveData.labels.map((time, i) => ({ x: time, y: liveData.prices[i] }));
        } else {
            const res = await fetch(`${API}/chart-data/${symbol}?time_range=${range}`);
            rawData = await res.json();
            if (!rawData || rawData.length === 0) return;

            const chartType = document.getElementById("chartTypeSelector").value;
            if (chartType === 'candlestick') {
                seriesData = rawData.map(d => ({ x: d.x, y: d.y }));
            } else {
                seriesData = rawData.map(d => ({ x: d.x, y: d.y[3] }));
            }
        }

        if (chartInstance) { chartInstance.destroy(); }

        const startPrice = isIntraday ? seriesData[0].y : (seriesData[0].y.length ? seriesData[0].y[3] : seriesData[0].y);
        const endPrice = isIntraday ? seriesData[seriesData.length - 1].y : (seriesData[seriesData.length - 1].y.length ? seriesData[seriesData.length - 1].y[3] : seriesData[seriesData.length - 1].y);
        const chartColor = endPrice >= startPrice ? '#00d09c' : '#ff4444';

        let tickCount = 8;
        if (range === '1D' || range === '1W' || range === '1M') tickCount = 15;

        const options = {
            series: [{ name: symbol, data: seriesData }],
            chart: {
                type: isIntraday ? 'area' : document.getElementById("chartTypeSelector").value,
                height: 420,
                fontFamily: 'Segoe UI, sans-serif',
                toolbar: { show: true, tools: { download: false } },
                animations: { enabled: true }
            },
            colors: [chartColor],
            title: { text: undefined },
            xaxis: {
                type: 'category',
                tickAmount: tickCount,
                labels: {
                    rotate: -45,
                    style: { fontSize: '11px', colors: '#888' },
                    formatter: function (val) {
                        if (isIntraday) return val;
                        if (!val) return "";
                        const d = new Date(val);
                        if (isNaN(d.getTime())) return val;
                        return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }) + " '" + d.getFullYear().toString().substr(-2);
                    }
                },
                axisBorder: { show: false },
                axisTicks: { show: false }
            },
            yaxis: {
                opposite: true,
                labels: { formatter: (val) => val.toFixed(2), style: { colors: '#888' } },
                tooltip: { enabled: true }
            },
            grid: { borderColor: '#f1f1f1', strokeDashArray: 4 },
            stroke: { curve: 'smooth', width: 2 },
            fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.5, opacityTo: 0.05, stops: [0, 100] } },
            plotOptions: { candlestick: { colors: { upward: '#00d09c', downward: '#ff4444' } } },
            dataLabels: { enabled: false },
            tooltip: { y: { formatter: (val) => "₹" + val.toFixed(2) } }
        };

        chartInstance = new ApexCharts(document.querySelector("#chartBox"), options);
        chartInstance.render();
    } catch (err) { console.error("Chart Error", err); }
}

function changeChartType() {
    if (currentSymbol) renderApexChart(currentSymbol, currentRange);
}

async function loadTable(symbol, range) {
    if (range === '1D') return;
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
                        <td style="color:${retVal >= 0 ? '#00d09c' : '#ff4444'}; font-weight:600;">${retVal.toFixed(2)}%</td>
                    `;
            tbody.appendChild(tr);
        });
    } catch (e) { console.error(e); }
}

async function updateChart(range, btn) {
    if (!currentSymbol) return;
    currentRange = range;

    // UPDATE THE BUTTONS
    document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');

    // UPDATE THE RETURNS CARD
    updateReturnCard(range);

    document.getElementById("chartBox").style.opacity = "0.5";
    if (range === '1D') {
        await renderApexChart(currentSymbol, range);
    } else {
        await Promise.all([renderApexChart(currentSymbol, range), loadTable(currentSymbol, range)]);
    }
    document.getElementById("chartBox").style.opacity = "1";
}

async function compareStocks() {
    const s1 = document.getElementById('comp1').value.toUpperCase();
    const s2 = document.getElementById('comp2').value.toUpperCase();
    if (!s1 || !s2) return alert("Enter two symbols!");
    try {
        const res = await fetch(`${API}/compare?symbol1=${s1}&symbol2=${s2}`);
        const data = await res.json();
        alert(`🏆 WINNER: ${data.winner}\n\n${s1}: ${data.comparison[s1].average_return_30d}%\n${s2}: ${data.comparison[s2].average_return_30d}%`);
    } catch (e) { alert("Comparison failed."); }
}

load();