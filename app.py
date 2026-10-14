import streamlit as str

# Cấu hình hiển thị rộng cho game
str.set_page_config(page_title="Among Us 2D Evolution", layout="wide")

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
        🕹️ <b>CƠ CHẾ MỚI:</b> Game tự động phân vai ngẫu nhiên (30% làm Imposter, 70% làm Crewmate).<br>
        🔧 <b>Crewmate:</b> Đến phòng Electrical, nhấn <b>E</b> hoặc nút <b>USE</b> để mở minigame nối dây điện.<br>
        🔪 <b>Imposter:</b> Chạy lại gần Bot Xanh, nhấn <b>Q</b> hoặc nút <b>KILL</b> để ám sát mục tiêu!
    </div>
</div>
""", unsafe_allow_html=True)

# Khối mã HTML5/JS xử lý toàn bộ logic phức tạp của trò chơi
game_full_html = """
<div style="display: flex; justify-content: center; position: relative;">
    <canvas id="gameCanvas" width="800" height="480" tabindex="1"></canvas>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Tự động bắt nét vào canvas
canvas.focus();

// Cấu hình phông nền và phân vai (Ngẫu nhiên 30% Imposter)
const isUserImposter = Math.random() < 0.3;
let showRoleScreen = true;
let roleScreenTimer = 120; // Hiển thị màn hình phân vai trong 2 giây (60fps * 2)

// Nhân vật của người chơi
const player = {
    x: 150, y: 240, width: 24, height: 32, speed: 4.5,
    color: isUserImposter ? "#ff3e3e" : "#00d2ff",
    role: isUserImposter ? "IMPOSTER" : "CREWMATE",
    tasksDone: 0, totalTasks: 3
};

// Bot AI máy đóng vai trò ngược lại với người chơi
const bot = {
    x: 650, y: 240, width: 24, height: 32, speed: 2.0,
    color: isUserImposter ? "#00d2ff" : "#ff3e3e",
    role: isUserImposter ? "CREWMATE" : "IMPOSTER",
    targetX: 650, targetY: 240, state: "patrol",
    isDead: false
};

// Các phòng chức năng chính
const rooms = [
    { name: "Cafeteria", x: 400, y: 100, w: 180, h: 100 },
    { name: "Electrical", x: 150, y: 350, w: 120, h: 90 },
    { name: "Weapons", x: 650, y: 120, w: 110, h: 90 }
];

// Trạng thái hệ thống Minigame sửa điện (Nối dây)
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

// Cấu hình các nút bấm UI ảo góc màn hình giống Among Us thật
const uiButtons = {
    use: { x: 710, y: 400, r: 35, label: "USE", active: false, key: "e" },
    kill: { x: 620, y: 400, r: 35, label: "KILL", active: false, key: "q" },
    report: { x: 710, y: 310, r: 30, label: "REPORT", active: false, key: "r" }
};

let gameState = "PLAYING"; // PLAYING, WIN, LOSE
const keys = {};

// Xử lý sự kiện bàn phím
window.addEventListener("keydown", (e) => {
    let k = e.key.toLowerCase();
    if(["arrowup", "arrowdown", "arrowleft", "arrowright", " "].includes(k)) {
        e.preventDefault();
    }
    keys[k] = true;

    // Phím tắt tương tác nhanh
    if (k === "e" && uiButtons.use.active) triggerUseAction();
    if (k === "q" && uiButtons.kill.active) triggerKillAction();
    if (k === "escape") isMinigameOpen = false;
});
window.addEventListener("keyup", (e) => { keys[e.key.toLowerCase()] = false; });

// Xử lý sự kiện click chuột (Cho cả nút bấm UI ảo và Minigame sửa điện)
canvas.addEventListener("mousedown", (e) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // 1. Nếu đang mở minigame sửa điện
    if (isMinigameOpen) {
        // Kiểm tra click chọn dây bên trái (X = 260)
        wiringGame.leftWires.forEach(w => {
            if (Math.abs(mouseX - 260) < 20 && Math.abs(mouseY - w.y) < 20 && !w.connected) {
                wiringGame.selectedLeft = w;
            }
        });
        
        // Kiểm tra thả/click nối sang dây bên phải (X = 540)
        if (wiringGame.selectedLeft) {
            wiringGame.rightWires.forEach(rw => {
                if (Math.abs(mouseX - 540) < 20 && Math.abs(mouseY - rw.y) < 20 && rw.id === wiringGame.selectedLeft.id) {
                    wiringGame.selectedLeft.connected = true;
                    rw.connected = true;
                    wiringGame.selectedLeft = null;
                    
                    // Kiểm tra hoàn thành tất cả các dây
                    if (wiringGame.leftWires.every(w => w.connected)) {
                        isMinigameOpen = false;
                        player.tasksDone = player.totalTasks; // Hoàn thành toàn bộ task sửa điện
                        if (player.role === "CREWMATE") gameState = "WIN";
                    }
                }
            });
        }
        return;
    }

    // 2. Kiểm tra click các nút bấm UI trên màn hình chính
    for (let btnKey in uiButtons) {
        let btn = uiButtons[btnKey];
        if (btn.active && Math.hypot(mouseX - btn.x, mouseY - btn.y) < btn.r) {
            if (btnKey === "use") triggerUseAction();
            if (btnKey === "kill") triggerKillAction();
        }
    }
});

function triggerUseAction() {
    if (player.role === "CREWMATE" && isInRoom(player, "Electrical")) {
        isMinigameOpen = true;
    }
}

function triggerKillAction() {
    if (player.role === "IMPOSTER" && !bot.isDead) {
        bot.isDead = true;
        gameState = "WIN";
    }
}

// Kiểm tra xem thực thể có đang đứng trong phòng cụ thể không
function isInRoom(ent, roomName) {
    let r = rooms.find(rm => rm.name === roomName);
    if (!r) return false;
    let cx = ent.x + ent.width/2;
    let cy = ent.y + ent.height/2;
    return (cx >= r.x && cx <= r.x + r.w && cy >= r.y && cy <= r.y + r.h);
}

// Vẽ tạo hình đặc trưng phi hành đoàn Among Us
function drawCharacter(ctx, x, y, width, height, color, isDead) {
    if (isDead) {
        // Vẽ cái xương đặc trưng khi bị hạ gục
        ctx.fillStyle = color;
        ctx.fillRect(x, y + height/2, width, height/2);
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(x + width/2 - 3, y, 6, height/2);
        return;
    }
    const r = width / 2;
    // Balo sau lưng
    ctx.fillStyle = color;
    ctx.fillRect(x - 6, y + height/4, 6, height/2);
    // Thân bo tròn đầu
    ctx.beginPath();
    ctx.arc(x + r, y + r, r, Math.PI, 0);
    ctx.lineTo(x + width, y + height - 6);
    ctx.lineTo(x, y + height - 6);
    ctx.closePath(); ctx.fill();
    // Chân
    ctx.fillRect(x, y + height - 6, 7, 6);
    ctx.fillRect(x + width - 7, y + height - 6, 7, 6);
    // Kính bảo hộ hình bầu dục (Visor)
    ctx.fillStyle = "#e3fafc";
    ctx.strokeStyle = "#101622";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.roundRect(x + width - 8, y + 6, 12, 10, 4);
    ctx.fill(); ctx.stroke();
}

function update() {
    if (showRoleScreen) {
        roleScreenTimer--;
        if (roleScreenTimer <= 0) showRoleScreen = false;
        return;
    }
    if (gameState !== "PLAYING" || isMinigameOpen) return;

    // Di chuyển nhân vật người chơi
    if (keys["w"] || keys["arrowup"]) player.y -= player.speed;
    if (keys["s"] || keys["arrowdown"]) player.y += player.speed;
    if (keys["a"] || keys["arrowleft"]) player.x -= player.speed;
    if (keys["d"] || keys["arrowright"]) player.x += player.speed;

    player.x = Math.max(10, Math.min(canvas.width - player.width - 10, player.x));
    player.y = Math.max(10, Math.min(canvas.height - player.height - 10, player.y));

    // Kích hoạt trạng thái hiển thị của các nút bấm UI
    uiButtons.use.active = (player.role === "CREWMATE" && isInRoom(player, "Electrical"));
    
    let distToBot = Math.hypot((player.x + player.width/2) - (bot.x + bot.width/2), (player.y + player.height/2) - (bot.y + bot.height/2));
    uiButtons.kill.active = (player.role === "IMPOSTER" && distToBot < 50 && !bot.isDead);

    // AI của Bot di chuyển quanh bản đồ
    if (!bot.isDead) {
        if (bot.role === "IMPOSTER" && distToBot < 150) {
            // Nếu Bot là Imposter, nó sẽ rượt đuổi người chơi để ám sát
            let angle = Math.atan2(player.y - bot.y, player.x - bot.x);
            bot.x += Math.cos(angle) * bot.speed;
            bot.y += Math.sin(angle) * bot.speed;
            if (distToBot < 25) gameState = "LOSE"; // Người chơi bị bot hạ gục
        } else {
            // Tuần tra di chuyển ngẫu nhiên
            if (Math.hypot(bot.targetX - bot.x, bot.targetY - bot.y) < 15) {
