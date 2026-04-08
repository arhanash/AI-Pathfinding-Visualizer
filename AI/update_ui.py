import sys

def modify_html():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    start_idx = content.find("    <script>")
    end_idx = content.find("    </script>", start_idx) + len("    </script>")

    if start_idx == -1 or end_idx == -1:
        print("Script tags not found")
        sys.exit(1)

    new_script = """    <script>
        // DOM Elements
        const elements = {
            tputChart: document.getElementById('throughputChart'),
            lights: {
                A: { r: document.getElementById('light-A-r'), y: document.getElementById('light-A-y'), g: document.getElementById('light-A-g') },
                B: { r: document.getElementById('light-B-r'), y: document.getElementById('light-B-y'), g: document.getElementById('light-B-g') },
                C: { r: document.getElementById('light-C-r'), y: document.getElementById('light-C-y'), g: document.getElementById('light-C-g') },
                D: { r: document.getElementById('light-D-r'), y: document.getElementById('light-D-y'), g: document.getElementById('light-D-g') }
            },
            badges: {
                A: document.getElementById('badge-A'), B: document.getElementById('badge-B'), C: document.getElementById('badge-C'), D: document.getElementById('badge-D')
            },
            queues: {
                A: document.getElementById('q-A'), B: document.getElementById('q-B'), C: document.getElementById('q-C'), D: document.getElementById('q-D')
            },
            qbars: {
                A: document.getElementById('qbar-A'), B: document.getElementById('qbar-B'), C: document.getElementById('qbar-C'), D: document.getElementById('qbar-D')
            },
            veh: {
                A: document.getElementById('veh-A'), B: document.getElementById('veh-B'), C: document.getElementById('veh-C'), D: document.getElementById('veh-D')
            },
            cams: {
                A: document.getElementById('cam-A'), B: document.getElementById('cam-B'), C: document.getElementById('cam-C'), D: document.getElementById('cam-D')
            },
            stats: {
                total: document.getElementById('stat-total'),
                wait: document.getElementById('stat-wait'),
                tput: document.getElementById('stat-tput'),
                eff: document.getElementById('stat-eff'),
                totala: document.getElementById('stat-total-a'),
                waita: document.getElementById('stat-wait-a'),
                tputa: document.getElementById('stat-tput-a'),
                effa: document.getElementById('stat-eff-a')
            }
        };

        // State populated by WebSocket
        let state = null;
        let ws = null;
        let chartInstance = null;
        let carSims = {}; // Store car tracking

        // --- WebSocket Connection ---
        function initWebSocket() {
            ws = new WebSocket("ws://localhost:8000/ws");
            
            ws.onmessage = (event) => {
                const msg = JSON.parse(event.data);
                if (msg.type === "SIM_STATE") {
                    state = msg.data;
                    syncUIReflectingState();
                }
            };
            
            ws.onclose = () => {
                console.log("WebSocket connection closed. Retrying in 2s...");
                document.getElementById('status-label').innerText = 'Disconnected! Reconnecting...';
                document.getElementById('status-label').style.color = 'var(--danger)';
                setTimeout(initWebSocket, 2000);
            };
            
            ws.onopen = () => {
                console.log("Connected to AI Backend");
            };
        }

        function wsSend(action, payload={}) {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ action: action, payload: payload }));
            }
        }

        // --- Page Routing & Theme ---
        function switchPage(pageStr) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-right .btn:not(.btn-icon)').forEach(b => b.classList.remove('active'));
            document.getElementById(`page-${pageStr}`).classList.add('active');
            if(pageStr === 'dashboard') document.getElementById('btn-nav-dash').classList.add('active');
            else document.getElementById('btn-nav-ana').classList.add('active');
        }

        function toggleTheme() {
            document.body.classList.toggle('dark-mode');
            const btn = document.getElementById('btn-theme');
            btn.innerText = document.body.classList.contains('dark-mode') ? '☀️' : '🌙';
            Chart.defaults.color = document.body.classList.contains('dark-mode') ? '#94a3b8' : '#6b7280';
            Chart.defaults.borderColor = document.body.classList.contains('dark-mode') ? '#334155' : '#e5e7eb';
            if(chartInstance) chartInstance.update();
        }

        // --- Commands sent to Backend ---
        function toggleAI() { wsSend("TOGGLE_AI"); }
        function togglePause() { wsSend("TOGGLE_PAUSE"); }
        function resetSim() { wsSend("RESET_SIM"); }
        function setSpeed(sp, btnElement) { 
            document.querySelectorAll('.speed-group .btn').forEach(b => b.classList.remove('active'));
            if(btnElement) btnElement.classList.add('active');
            wsSend("SET_SPEED", { speed: sp }); 
        }

        // Emergency Override Commands
        let selectedEmRoad = null;
        let selectedEmType = null;
        
        // Expose functions globally for element interaction
        window.switchPage = switchPage;
        window.toggleTheme = toggleTheme;
        window.toggleAI = toggleAI;
        window.togglePause = togglePause;
        window.resetSim = resetSim;
        window.setSpeed = setSpeed;
        
        window.selectEmRoad = function(rd) {
            selectedEmRoad = rd;
            document.querySelectorAll('#em-roads .emerg-card').forEach(c => c.classList.remove('selected'));
            event.target.classList.add('selected');
            checkEmReady();
        }
        window.selectEmType = function(type) {
            selectedEmType = type;
            document.querySelectorAll('#em-types .emerg-card').forEach(c => c.classList.remove('selected'));
            event.target.classList.add('selected');
            checkEmReady();
        }
        function checkEmReady() {
            if(!state) return;
            const btn = document.getElementById('btn-em-trigger');
            if(selectedEmRoad && selectedEmType && !state.emergencyActive) {
                btn.disabled = false;
            }
        }
        window.triggerEmergency = function() {
            if(state && state.emergencyActive) { wsSend("CANCEL_EMERGENCY"); return; }
            wsSend("TRIGGER_EMERGENCY", { road: selectedEmRoad });
        }


        // --- Core Visual Updates Driven by Backend State ---
        function setLight(road, colorStr) {
            const l = elements.lights[road];
            l.r.classList.remove('active'); l.y.classList.remove('active'); l.g.classList.remove('active');
            l[colorStr].classList.add('active');
            
            const b = elements.badges[road];
            b.classList.remove('badge-red', 'badge-yellow', 'badge-green');
            if(colorStr==='r') { b.innerText = 'RED'; b.classList.add('badge-red'); }
            if(colorStr==='y') { b.innerText = 'YELLOW'; b.classList.add('badge-yellow'); }
            if(colorStr==='g') { b.innerText = 'GREEN'; b.classList.add('badge-green'); }
        }

        function simulateCars(roadId) {
            if(!state) return;
            const cam = elements.cams[roadId];
            if(Math.random() > 0.4 && state.aiActive && !state.isPaused) {
                const car = document.createElement('div');
                car.className = 'car';
                car.style.background = `hsl(${Math.random()*360}, 70%, 50%)`;
                
                if(roadId==='A' || roadId==='C') {
                    car.classList.add('ns');
                    car.style.left = (Math.random()*80 + 10) + '%';
                    car.style.top = '-20px';
                    cam.appendChild(car);
                    let pos = -20;
                    let inter = setInterval(() => {
                        if(!state || state.isPaused) return;
                        pos += 2 * state.speed;
                        car.style.top = pos + 'px';
                        if(pos > 60) { clearInterval(inter); car.remove(); }
                    }, 50);
                } else {
                    car.classList.add('ew');
                    car.style.top = (Math.random()*40 + 10) + 'px';
                    car.style.left = '-20px';
                    cam.appendChild(car);
                    let pos = -20;
                    let inter = setInterval(() => {
                        if(!state || state.isPaused) return;
                        pos += 2 * state.speed;
                        car.style.left = pos + 'px';
                        if(pos > cam.clientWidth) { clearInterval(inter); car.remove(); }
                    }, 50);
                }
            }
        }

        // Sync entirely from Backend State
        function syncUIReflectingState() {
            if(!state) return;

            // 1. Controls Sync
            const btnAi = document.getElementById('btn-ai-toggle');
            if(state.aiActive) {
                btnAi.classList.remove('off'); btnAi.innerHTML = '🎥 AI Detection ON';
            } else {
                btnAi.classList.add('off'); btnAi.innerHTML = '🎥 AI Detection OFF';
            }

            const btnPause = document.getElementById('btn-pause');
            const lblStatus = document.getElementById('status-label');
            if(state.isPaused) {
                btnPause.innerHTML = 'Resume ▶'; btnPause.style.background = 'var(--primary-light)'; btnPause.style.color = 'var(--primary)';
                lblStatus.innerText = 'Paused'; lblStatus.style.color = 'var(--warning)';
            } else {
                btnPause.innerHTML = 'Pause ⏸'; btnPause.style.background = 'var(--secondary-light)'; btnPause.style.color = 'var(--secondary)';
                lblStatus.innerText = 'Running'; lblStatus.style.color = 'var(--primary)';
            }

            document.getElementById('speed-label').innerText = `Speed: ${state.speed}x`;
            document.getElementById('cycles-label').innerText = `Cycles: ${state.cycles}`;

            // 2. Emergency Override Sync
            const btnEm = document.getElementById('btn-em-trigger');
            const emBanner = document.getElementById('em-banner');
            if(state.emergencyActive) {
                btnEm.innerHTML = `🔴 Emergency Active (${state.emergencyRoad}) — Cancel`;
                btnEm.style.animation = 'pulse 1s infinite alternate';
                btnEm.disabled = false;
                emBanner.style.display = 'block';
            } else {
                btnEm.innerHTML = 'Activate Emergency Override';
                btnEm.style.animation = 'none';
                btnEm.disabled = !(selectedEmRoad && selectedEmType);
                emBanner.style.display = 'none';
            }

            // 3. Traffic Lights Sync
            const activeR = state.emergencyActive ? state.emergencyRoad : state.roads[state.activeRoadIdx];
            for (let r of state.roads) {
                if (state.emergencyActive) {
                    setLight(r, r === state.emergencyRoad ? 'g' : 'r');
                } else {
                    setLight(r, r === activeR ? 'g' : 'r');
                }
            }

            // 4. Queues & Badges
            for(let r of state.roads) {
                elements.queues[r].innerText = state.queues[r];
                elements.veh[r].innerText = state.queues[r] + Math.floor(Math.random()*(r===activeR?10:2));
                
                let pct = (state.queues[r] / 50) * 100;
                if(pct>100) pct=100;
                elements.qbars[r].style.width = pct + '%';
                if(pct < 30) elements.qbars[r].style.background = 'var(--primary)';
                else if(pct < 70) elements.qbars[r].style.background = 'var(--warning)';
                else elements.qbars[r].style.background = 'var(--danger)';

                let spd = 20 + Math.random()*20;
                if(r === activeR) spd += 20; 
                if(state.queues[r] > 30 && r !== activeR) spd = 0;
                if(document.getElementById(`spd-${r}`)) document.getElementById(`spd-${r}`).innerText = spd.toFixed(1);
                if(document.getElementById(`t-q-${r}`)) document.getElementById(`t-q-${r}`).innerText = state.queues[r];
                
                // Add cars every tick
                simulateCars(r);
            }

            // 5. Global Stats
            let waitTime = 60 + Math.floor(Math.random()*20); // Dummy for UX
            let efficiency = 75 + Math.floor(Math.random()*15); // Dummy for UX

            let sTotStr = state.totalProcessed.toLocaleString();
            elements.stats.total.innerText = sTotStr; elements.stats.totala.innerText = sTotStr;
            elements.stats.wait.innerText = waitTime + 's'; elements.stats.waita.innerText = waitTime + 's';
            elements.stats.tput.innerText = state.throughput; elements.stats.tputa.innerText = state.throughput;
            elements.stats.eff.innerText = efficiency + '%'; elements.stats.effa.innerText = efficiency + '%';

            document.getElementById('tbl-wait').innerText = waitTime + 's';
            document.getElementById('tbl-eff').innerText = efficiency + '%';
            document.getElementById('tbl-tot').innerText = sTotStr;
            document.getElementById('chart-tot').innerText = sTotStr;
            document.getElementById('chart-eff').innerText = efficiency + '%';

            const timeStr = new Date().toLocaleTimeString();
            document.getElementById('last-updated').innerText = `● Stop ● Caution ● Go | From Backend: ${timeStr}`;
            document.getElementById('footer-time').innerText = `Updated at ${timeStr} (Server Ticks: ${state.simTime})`;

            // 6. Chart update
            updateChartFromServer();
        }

        // --- Chart.js ---
        function initChart() {
            const ctx = elements.tputChart.getContext('2d');
            chartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: Array.from({length: 12}, (_, i) => `T-${12-i}`),
                    datasets: [
                        { label: 'Road A', data: [], borderColor: '#60a5fa', tension: 0.4, borderWidth: 2, pointRadius: 0 },
                        { label: 'Road B', data: [], borderColor: '#facc15', tension: 0.4, borderWidth: 2, pointRadius: 0 },
                        { label: 'Road C', data: [], borderColor: '#f87171', tension: 0.4, borderWidth: 2, pointRadius: 0 },
                        { label: 'Road D', data: [], borderColor: '#c084fc', tension: 0.4, borderWidth: 2, pointRadius: 0 }
                    ]
                },
                options: {
                    responsive: true, maintainAspectRatio: false, animation: { duration: 0 },
                    scales: { y: { min: 0, max: 60, grid: { color: 'rgba(150, 150, 150, 0.1)' } }, x: { grid: { display: false } } },
                    plugins: { legend: { labels: { color: '#94a3b8' } }, tooltip: { mode: 'index', intersect: false } },
                    interaction: { mode: 'nearest', axis: 'x', intersect: false }
                }
            });
            Chart.defaults.color = document.body.classList.contains('dark-mode') ? '#94a3b8' : '#6b7280';
            Chart.defaults.borderColor = document.body.classList.contains('dark-mode') ? '#334155' : '#e5e7eb';
        }

        function updateChartFromServer() {
            if(!chartInstance || !state || !state.chartData) return;
            chartInstance.data.datasets[0].data = state.chartData['A'];
            chartInstance.data.datasets[1].data = state.chartData['B'];
            chartInstance.data.datasets[2].data = state.chartData['C'];
            chartInstance.data.datasets[3].data = state.chartData['D'];
            chartInstance.update();
        }

        // --- Bootstrap ---
        window.onload = () => {
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                document.body.classList.add('dark-mode');
                document.getElementById('btn-theme').innerText = '☀️';
            }
            initChart();
            initWebSocket();
        };

    </script>"""

    final_content = content[:start_idx] + new_script + content[end_idx:]

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_content)

if __name__ == "__main__":
    modify_html()
    print("UI update successful.")
