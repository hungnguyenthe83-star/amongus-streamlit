import streamlit as st
import streamlit.components.v1 as components

# Cấu hình giao diện rộng cho Streamlit Cloud
st.set_page_config(page_title="Among Us 2D", layout="wide")

# CSS tối ưu hóa khung nhìn, ẩn menu thừa để tập trung chơi game
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .game-title {
        color: #ff2a2a;
        font-size: 32px;
        font-weight: 900;
        text-align: center;
        letter-spacing: 3px;
        margin-bottom: 10px;
        text-shadow: 2px 2px 0px #000;
    }
</style>
<div class="game-title">AMONG US 2D - FINAL EDITION</div>
""", unsafe_allow_html=True)

# Khởi tạo chuỗi mã nguồn HTML và Javascript một cách an toàn nhất
html_source = []

# Phần 1: Khung vẽ Canvas và khai báo biến khởi tạo
html_source.append("""
<div style="display: flex; justify-content: center;">
    <canvas id="gameCanvas" width="800" height="480" tabindex="1" style="border:4px solid #24344d; background:#080a0f; border-radius:12px; outline:none;"></canvas>
</div>
<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
canvas.focus();

const isUserImposter = Math.random() < 0.35;
let showRoleScreen = true;
let roleScreenTimer = 120;
let gameState = "PLAYING";
let isMinigameOpen = false;

const player = {
    x: 150, y: 240, width: 24, height: 32, speed: 4.5,
    color: isUserImposter ? "#ff3e3e" : "#00d2ff",
    role: isUserImposter ? "IMPOSTER" : "CREWMATE",
    tasksDone: 0, totalTasks: 3
};

const bot = {
    x: 650, y: 240, width: 24, height: 32, speed: 2.2,
    color: isUserImposter ? "#00d2ff" : "#ff3e3e",
    role: isUserImposter ? "CREWMATE" : "IMPOSTER",
    targetX: 650, targetY: 240, state: "patrol", isDead: false
};

const rooms = [
    { name: "Cafeteria", x: 400, y: 80, w: 180, h: 100 },
    { name: "Electrical", x: 150, y: 340, w: 130, h: 100 },
    { name: "Weapons", x: 620, y: 120, w: 120, h: 90 }
];

const wiringGame = {
    leftWires: [
        { id: 1, color: "#ff3e3e", y: 150, connected: false },
        { id: 2, color: "#00d2ff", y: 230, connected: false },
        { id: 3, color: "#f1c40f", y: 310, connected: false }
    ],
    rightWires: [
        { id: 2, color: "#00d2ff", y: 150, connected: false },
        { id: 1, color: "#ff3e3e", y: 230, connected: false },
        { id: 3, color: "#f1c40f", y: 310, connected: false }
    ],
    selectedLeft: null
};

const uiButtons = {
    use: { x: 710, y: 400, r: 35, label: "USE", active: false },
    kill: { x: 620, y: 400, r: 35, label: "KILL", active: false }
};

const keys = {};
window.addEventListener("keydown", (e) => {
    let k = e.key.toLowerCase();
    if(["arrowup","arrowdown","arrowleft","arrowright"," "].includes(k)) e.preventDefault();
    keys[k] = true;
});
window.addEventListener("keyup", (e) => { keys[e.key.toLowerCase()] = false; });
""")

# Phần 2: Xử lý sự kiện click chuột tương tác (Nút bấm UI + Minigame)
html_source.append("""
canvas.addEventListener("mousedown", (e) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    if (isMinigameOpen) {
        wiringGame.leftWires.forEach(w => {
            if (Math.abs(mouseX - 260) < 20 && Math.abs(mouseY - w.y) < 20 && !w.connected) {
                wiringGame.selectedLeft = w;
            }
        });
        if (wiringGame.selectedLeft) {
            wiringGame.rightWires.forEach(rw => {
                if (Math.abs(mouseX - 540) < 20 && Math.abs(mouseY - rw.y) < 20 && rw.id === wiringGame.selectedLeft.id) {
                    wiringGame.selectedLeft.connected = true;
                    rw.connected = true;
                    wiringGame.selectedLeft = null;
                    if (wiringGame.leftWires.every(w => w.connected)) {
                        isMinigameOpen = false;
                        player.tasksDone = player.totalTasks;
                        if (player.role === "CREWMATE") gameState = "WIN";
                    }
                }
            });
        }
        return;
    }

    for (let btnKey in uiButtons) {
        let btn = uiButtons[btnKey];
        if (btn.active && Math.hypot(mouseX - btn.x, mouseY - btn.y) < btn.r) {
            if (btnKey === "use") isMinigameOpen = true;
            if (btnKey === "kill") {
                bot.isDead = true;
                gameState = "WIN";
            }
        }
    }
});

function isInRoom(ent, roomName) {
    let r = rooms.find(rm => rm.name === roomName);
    if (!r) return false;
    let cx = ent.x + ent.width/2;
    let cy = ent.y + ent.height/2;
    return (cx >= r.x && cx <= r.x + r.w && cy >= r.y && cy <= r.y + r.h);
}
""")

# Phần 3: Hàm vẽ tạo hình nhân vật (Crewmate / Imposter) chuẩn xác
html_source.append("""
function drawCharacter(ctx, x, y, width, height, color, isDead) {
    if (isDead) {
        ctx.fillStyle = color;
        ctx.fillRect(x, y + height/2, width, height/2);
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(x + width/2 - 3, y, 6, height/2);
        return;
    }
    const r = width / 2;
    ctx.fillStyle = color;
    ctx.fillRect(x - 5, y + 8, 5, 16);
    ctx.beginPath();
    ctx.arc(x + r, y + r, r, Math.PI, 0);
    ctx.lineTo(x + width, y + height - 6);
    ctx.lineTo(x, y + height - 6);
    ctx.closePath(); 
    ctx.fill();
    ctx.fillRect(x, y + height - 6, 6, 6);
    ctx.fillRect(x + width - 6, y + height - 6, 6, 6);
    ctx.fillStyle = "#e3fafc";
    ctx.fillRect(x + width - 6, y + 6, 10, 8);
}
""")

# Phần 4: Vòng lặp cập nhật vị trí vật lý và xử lý AI của máy
html_source.append("""
function update() {
    if (showRoleScreen) {
        roleScreenTimer--;
        if (roleScreenTimer <= 0) showRoleScreen = false;
        return;
    }
    if (gameState !== "PLAYING" || isMinigameOpen) return;

    if (keys["w"] || keys["arrowup"]) player.y -= player.speed;
    if (keys["s"] || keys["arrowdown"]) player.y += player.speed;
    if (keys["a"] || keys["arrowleft"]) player.x -= player.speed;
    if (keys["d"] || keys["arrowright"]) player.x += player.speed;

    player.x = Math.max(10, Math.min(canvas.width - player.width - 10, player.x));
    player.y = Math.max(10, Math.min(canvas.height - player.height - 10, player.y));

    uiButtons.use.active = (player.role === "CREWMATE" && isInRoom(player, "Electrical"));
    
    let distToBot = Math.hypot((player.x + player.width/2) - (bot.x + bot.width/2), (player.y + player.height/2) - (bot.y + bot.height/2));
    uiButtons.kill.active = (player.role === "IMPOSTER" && distToBot < 50 && !bot.isDead);

    if (!bot.isDead) {
        if (bot.role === "IMPOSTER" && distToBot < 150) {
            let angle = Math.atan2(player.y - bot.y, player.x - bot.x);
            bot.x += Math.cos(angle) * bot.speed;
            bot.y += Math.sin(angle) * bot.speed;
            if (distToBot < 24) gameState = "LOSE";
        } else {
            if (Math.hypot(bot.targetX - bot.x, bot.targetY - bot.y) < 15) {
                bot.targetX = Math.random() * (canvas.width - 100) + 50;
                bot.targetY = Math.random() * (canvas.height - 100) + 50;
            }
            let angle = Math.atan2(bot.targetY - bot.y, bot.targetX - bot.x);
            bot.x += Math.cos(angle) * (bot.speed * 0.7);
            bot.y += Math.sin(angle) * (bot.speed * 0.7);
        }
    }
}
""")

# Phần 5: Kết xuất đồ họa lên màn hình chính (Đã bọc chuỗi an toàn cố định)
html_source.append("""
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    rooms.forEach(r => {
        ctx.fillStyle = "#111622";
        ctx.fillRect(r.x, r.y, r.w, r.h);
        ctx.strokeStyle = "#24344d";
        ctx.lineWidth = 3;
        ctx.strokeRect(r.x, r.y, r.w, r.h);

        if (r.name === "Electrical") {
            ctx.fillStyle = player.tasksDone === player.totalTasks ? "#2ecc71" : "#ffaa00";
            ctx.beginPath(); ctx.arc(r.x + r.w/2, r.y + r.h/2, 6, 0, Math.PI*2); ctx.fill();
        }

        ctx.fillStyle = "#576c8c";
        ctx.font = "bold 11px Arial";
        ctx.textAlign = "center";
        ctx.fillText(r.name.toUpperCase(), r.x + r.w/2, r.y + 20);
    });

    drawCharacter(ctx, player.x, player.y, player.width, player.height, player.color, false);
    drawCharacter(ctx, bot.x, bot.y, bot.width, bot.height, bot.color, bot.isDead);

    for (let btnKey in uiButtons) {
        let btn = uiButtons[btnKey];
        if (player.role === "IMPOSTER" && btnKey === "use") continue;
        if (player.role === "CREWMATE" && btnKey === "kill") continue;

        ctx.beginPath();
        ctx.arc(btn.x, btn.y, btn.r, 0, Math.PI * 2);
        ctx.fillStyle = btn.active ? "rgba(235, 94, 40, 0.8)" : "rgba(40, 49, 73, 0.4)";
        ctx.fill();
        ctx.strokeStyle = btn.active ? "#ff6b35" : "#485460";
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = btn.active ? "#ffffff" : "#7f8c8d";
        ctx.font = "bold 11px Arial";
        ctx.textAlign = "center";
        ctx.fillText(btn.label, btn.x, btn.y + 4);
    }

    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 14px Arial";
    ctx.textAlign = "left";
    let pct = (player.tasksDone / player.totalTasks) * 100;
    ctx.fillText("TASK PROGRESS:", 25, 32);
    ctx.fillStyle = "#2c3e50";
    ctx.fillRect(160, 20, 150, 15);
    ctx.fillStyle = "#2ecc71";
    ctx.fillRect(160, 20, (pct / 100) * 150, 15);

    if (isMinigameOpen) {
        ctx.fillStyle = "rgba(10, 15, 26, 0.95)";
        ctx.fillRect(200, 60, 400, 340);
        ctx.strokeStyle = "#34495e";
        ctx.strokeRect(200, 60, 400, 340);

        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 14px Arial";
        ctx.textAlign = "center";
        ctx.fillText("FIX WIRING - MATCH COLORS", 400, 95);

        wiringGame.leftWires.forEach(w => {
            ctx.fillStyle = w.color;
            ctx.fillRect(240, w.y - 10, 20, 20);

