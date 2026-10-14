import streamlit as str

# Cấu hình hiển thị rộng cho game
str.set_page_config(page_title="Among Us 2D Standard Edition", layout="wide")

str.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        .game-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #0b0d13;
            font-family: 'Arial', sans-serif;
            padding: 15px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.7);
            max-width: 840px;
            margin: auto;
        }
        .game-header {
            color: #ff2a2a;
            font-size: 36px;
            font-weight: 900;
            letter-spacing: 4px;
            margin-bottom: 5px;
            text-shadow: 3px 3px 0px #000;
        }
        .tip-box {
            background-color: #121824;
            color: #00e1ff;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 13px;
            margin-bottom: 15px;
            border: 1px solid #1f2d42;
            text-align: center;
            width: 100%;
        }
        canvas {
            border: 4px solid #1f2d42;
            background-color: #080a0f;
            border-radius: 12px;
            outline: none;
        }
    </style>
""", unsafe_allow_html=True)

str.markdown("""
<div class="game-container">
    <div class="game-header">AMONG US EVOLUTION</div>
    <div class="tip-box">
        🕹️ <b>CƠ CHẾ:</b> Game tự động phân vai ngẫu nhiên (30% làm Imposter, 70% làm Crewmate).<br>
        🔧 <b>Crewmate:</b> Đến phòng Electrical, nhấn nút <b>USE</b> góc phải để mở minigame nối dây điện.<br>
        🔪 <b>Imposter:</b> Chạy lại gần Bot Xanh, nhấn nút <b>KILL</b> góc phải để thắng trận!
    </div>
</div>
""", unsafe_allow_html=True)

game_safe_html = """
<div style="display: flex; justify-content: center; position: relative;">
    <canvas id="gameCanvas" width="800" height="480" tabindex="1"></canvas>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

canvas.focus();

// Phân vai ngẫu nhiên
const isUserImposter = Math.random() < 0.3;
let showRoleScreen = true;
let roleScreenTimer = 120; 

const player = {
    x: 150, y: 240, width: 24, height: 32, speed: 4.5,
    color: isUserImposter ? "#ff3e3e" : "#00d2ff",
    role: isUserImposter ? "IMPOSTER" : "CREWMATE",
    tasksDone: 0, totalTasks: 3
};

const bot = {
    x: 650, y: 240, width: 24, height: 32, speed: 2.0,
    color: isUserImposter ? "#00d2ff" : "#ff3e3e",
    role: isUserImposter ? "CREWMATE" : "IMPOSTER",
    targetX: 650, targetY: 240, state: "patrol",
    isDead: false
};

const rooms = [
    { name: "Cafeteria", x: 400, y: 100, w: 180, h: 100 },
    { name: "Electrical", x: 150, y: 350, w: 120, h: 90 },
    { name: "Weapons", x: 650, y: 120, w: 110, h: 90 }
];

let isMinigameOpen = false;
const wiringGame = {
    leftWires: [
        { id: 1, color: "#ff3e3e", y: 140, connected: false },
        { id: 2, color: "#00d2ff", y: 220, connected: false },
        { id: 3, color: "#f1c40f", y: 300, connected: false }
    ],
    rightWires: [
        { id: 2, color: "#00d2ff", y: 140, connected: false },
        { id: 1, color: "#ff3e3e", y: 220, connected: false },
        { id: 3, color: "#f1c40f", y: 300, connected: false }
    ],
    selectedLeft: null
};

const uiButtons = {
    use: { x: 710, y: 400, r: 35, label: "USE", active: false },
    kill: { x: 620, y: 400, r: 35, label: "KILL", active: false }
};

let gameState = "PLAYING";
const keys = {};

window.addEventListener("keydown", (e) => {
    let k = e.key.toLowerCase();
    if(["arrowup", "arrowdown", "arrowleft", "arrowright", " "].includes(k)) {
        e.preventDefault();
    }
    keys[k] = true;
});
window.addEventListener("keyup", (e) => { keys[e.key.toLowerCase()] = false; });

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

// Hàm vẽ an toàn không dùng roundRect bị lỗi
function drawCharacter(ctx, x, y, width, height, color, isDead) {
    if (isDead) {
        ctx.fillStyle = color;
        ctx.fillRect(x, y + height/2, width, height/2);
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(x + width/2 - 3, y, 6, height/2);
        return;
    }
    const r = width / 2;
    // Balo
    ctx.fillStyle = color;
    ctx.fillRect(x - 5, y + 8, 5, 16);
    // Thân
    ctx.beginPath();
    ctx.arc(x + r, y + r, r, Math.PI, 0);
    ctx.lineTo(x + width, y + height - 6);
    ctx.lineTo(x, y + height - 6);
    ctx.closePath(); ctx.fill();
    // Chân
    ctx.fillRect(x, y + height - 6, 6, 6);
    ctx.fillRect(x + width - 6, y + height - 6, 6, 6);
    // Kính bảo hộ phẳng (Tránh lỗi trình duyệt)
    ctx.fillStyle = "#e3fafc";
    ctx.fillRect(x + width - 6, y + 6, 10, 8);
}

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
            if (distToBot < 25) gameState = "LOSE";
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

