import streamlit as str

# Cấu hình hiển thị rộng cho game
str.set_page_config(page_title="Among Us 2D Web Edition", layout="wide")

str.markdown("""
    <style>
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        .game-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #0c1017;
            font-family: 'Arial', sans-serif;
            padding: 15px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
            max-width: 840px;
            margin: auto;
        }
        .game-header {
            color: #ff3e3e;
            font-size: 32px;
            font-weight: 900;
            letter-spacing: 3px;
            margin-bottom: 5px;
            text-shadow: 3px 3px 0px #000;
        }
        .tip-box {
            background-color: #161f2c;
            color: #00e1ff;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 13px;
            margin-bottom: 15px;
            border-bottom: 3px solid #ffaa00;
            text-align: center;
        }
        canvas {
            border: 4px solid #253042;
            background-color: #121824;
            border-radius: 12px;
            box-shadow: inset 0 0 30px #000;
            outline: none;
        }
    </style>
""", unsafe_allow_html=True)

str.markdown("""
<div class="game-container">
    <div class="game-header">AMONG US 2D</div>
    <div class="tip-box">
        ⚠️ <b>LƯU Ý:</b> Click chuột vào khung màn hình đen bên dưới trước khi bấm phím để kích hoạt di chuyển!<br>
        🎮 Điều khiển bằng cụm phím <b>W - A - S - D</b> hoặc <b>Phím Mũi Tên</b>. Nhiệm vụ: Chạy đến chấm <b>Vàng (Task)</b>.
    </div>
</div>
""", unsafe_allow_html=True)

# Khối mã xử lý Logic Game & Vẽ tạo hình nhân vật chân thực
game_html_code = """
<div style="display: flex; justify-content: center;">
    <canvas id="gameCanvas" width="800" height="480" tabindex="1"></canvas>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Tự động focus vào canvas ngay khi load trang để tránh lỗi phím
canvas.focus();

// Người chơi (Crewmate)
const player = {
    x: 150,
    y: 240,
    width: 24,
    height: 32,
    speed: 4.5,
    color: "#00d2ff",
    tasksDone: 0
};

// Kẻ địch AI (Imposter)
const imposter = {
    x: 650,
    y: 240,
    width: 24,
    height: 32,
    speed: 2.2,
    color: "#ff3e3e",
    targetX: 650,
    targetY: 240,
    state: "patrol"
};

// Bản đồ các vị trí Nhiệm vụ (Vòng tròn Vàng)
const tasks = [
    { name: "Electrical", x: 120, y: 100, radius: 22, done: false },
    { name: "Cafeteria", x: 400, y: 80, radius: 22, done: false },
    { name: "Storage", x: 400, y: 400, radius: 22, done: false },
    { name: "Weapons", x: 680, y: 120, radius: 22, done: false }
];

let gameState = "PLAYING";
const keys = {};

// Sự kiện nhấn phím - Chặn cuộn trang web mặc định khi chơi game
window.addEventListener("keydown", (e) => {
    if(["arrowup", "arrowdown", "arrowleft", "arrowright", " "].includes(e.key.toLowerCase())) {
        e.preventDefault();
    }
    keys[e.key.toLowerCase()] = true;
});
window.addEventListener("keyup", (e) => { keys[e.key.toLowerCase()] = false; });

// Hàm vẽ tạo hình nhân vật Among Us đặc trưng (Thân bo tròn, kính, balo sau lưng)
function drawCrewmate(ctx, x, y, width, height, color, isImposter) {
    const r = width / 2;
    
    // 1. Vẽ Balo sau lưng (Bên trái hoặc phải tùy thuộc hướng)
    ctx.fillStyle = color;
    ctx.shadowBlur = 0;
    if (!isImposter) {
        ctx.fillRect(x - width/3 - 2, y + height/4, width/3 + 2, height/2);
    } else {
        ctx.fillRect(x + width, y + height/4, width/3 + 2, height/2);
    }

    // 2. Vẽ Thân hình Bo đầu (Capsule Shape)
    ctx.beginPath();
    ctx.arc(x + r, y + r, r, Math.PI, 0); // Đầu tròn
    ctx.lineTo(x + width, y + height - r);
    ctx.lineTo(x, y + height - r);
    ctx.closePath();
    ctx.fill();

    // 3. Vẽ hai Chân tách biệt
    ctx.fillRect(x, y + height - 8, width/3, 8);
    ctx.fillRect(x + width - width/3, y + height - 8, width/3, 8);

    // 4. Vẽ Kính bảo hộ hình bầu dục (Visor) cực kỳ đặc trưng
    ctx.fillStyle = isImposter ? "#4b6584" : "#ffffff";
    ctx.strokeStyle = "#1e272e";
    ctx.lineWidth = 1.5;
    
    ctx.beginPath();
    let visorX = isImposter ? x - 4 : x + width - 10;
    ctx.roundRect(visorX, y + height/5, 14, 10, 5);
    ctx.fill();
    ctx.stroke();
}

function updateLogic() {
    if (gameState !== "PLAYING") return;

    // Di chuyển mượt mà nhờ bắt sự kiện đồng bộ trực tiếp
    if (keys["w"] || keys["arrowup"]) player.y -= player.speed;
    if (keys["s"] || keys["arrowdown"]) player.y += player.speed;
    if (keys["a"] || keys["arrowleft"]) player.x -= player.speed;
    if (keys["d"] || keys["arrowright"]) player.x += player.speed;

    // Giới hạn biên map
    player.x = Math.max(10, Math.min(canvas.width - player.width - 10, player.x));
    player.y = Math.max(10, Math.min(canvas.height - player.height - 10, player.y));

    // Trung tâm của người chơi để tính va chạm toán học
    let pCenterX = player.x + player.width/2;
    let pCenterY = player.y + player.height/2;

    // Kiểm tra làm nhiệm vụ sửa máy
    tasks.forEach(task => {
        let dist = Math.hypot(pCenterX - task.x, pCenterY - task.y);
        if (!task.done && dist < task.radius + player.width/2) {
            task.done = true;
            player.tasksDone++;
            if (player.tasksDone === tasks.length) {
                gameState = "WIN";
            }
        }
    });

    // Trí tuệ nhân tạo săn lùng của Imposter
    let impCenterX = imposter.x + imposter.width/2;
    let impCenterY = imposter.y + imposter.height/2;
    let distToPlayer = Math.hypot(pCenterX - impCenterX, pCenterY - impCenterY);

    if (distToPlayer < 200) {
        imposter.state = "chase";
        let angle = Math.atan2(pCenterY - impCenterY, pCenterX - impCenterX);
        imposter.x += Math.cos(angle) * imposter.speed;
        imposter.y += Math.sin(angle) * imposter.speed;
    } else {
        if (imposter.state === "chase" || Math.hypot(imposter.targetX - imposter.x, imposter.targetY - imposter.y) < 15) {
            imposter.state = "patrol";
            imposter.targetX = Math.random() * (canvas.width - 60) + 30;
            imposter.targetY = Math.random() * (canvas.height - 60) + 30;
        }
        let angle = Math.atan2(imposter.targetY - imposter.y, imposter.targetX - imposter.x);
        imposter.x += Math.cos(angle) * (imposter.speed * 0.8);
        imposter.y += Math.sin(angle) * (imposter.speed * 0.8);
    }

    // Bị bắt -> Kẻ mạo danh hạ gục Crewmate
    if (distToPlayer < (player.width + imposter.width) / 1.5) {
        gameState = "LOSE";
    }
}

function renderGraphics() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Vẽ sàn tàu không gian kẻ vạch
    ctx.strokeStyle = "#1a2332";
    ctx.lineWidth = 1;
    for (let i = 0; i < canvas.width; i += 40) {
        ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
    }
    for (let j = 0; j < canvas.height; j += 40) {
        ctx.beginPath(); ctx.moveTo(0, j); ctx.lineTo(canvas.width, j); ctx.stroke();
    }

    // Vẽ các căn phòng nhiệm vụ màu vàng phát sáng nhẹ
    tasks.forEach(task => {
        ctx.beginPath();
        ctx.arc(task.x, task.y, task.radius, 0, Math.PI * 2);
        ctx.fillStyle = task.done ? "rgba(46, 204, 113, 0.15)" : "rgba(241, 196, 15, 0.25)";
        ctx.fill();
        ctx.strokeStyle = task.done ? "#2ecc71" : "#f1c40f";
        ctx.lineWidth = 3;
        ctx.stroke();

        ctx.fillStyle = "#8a99ad";
        ctx.font = "bold 12px Arial";
        ctx.textAlign = "center";
        ctx.fillText(task.name, task.x, task.y - task.radius - 8);
    });

    // Vẽ Crewmate của người chơi (Xanh)
    drawCrewmate(ctx, player.x, player.y, player.width, player.height, player.color, false);

    // Vẽ Kẻ mạo danh Imposter (Đỏ)
    drawCrewmate(ctx, imposter.x, imposter.y, imposter.width, imposter.height, imposter.color, true);

    // Thanh hiển thị tiến độ làm Task
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 15px Arial";
    ctx.textAlign = "left";
    ctx.fillText(`⚡ TIẾN ĐỘ NHIỆM VỤ: ${player.tasksDone} / ${tasks.length}`, 25, 35);

    // Màn hình Kết thúc trận đấu
    if (gameState === "WIN") {
        ctx.fillStyle = "rgba(0,0,0,0.85)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#2ecc71";
        ctx.font = "bold 45px Arial";
        ctx.textAlign = "center";
        ctx.fillText("VICTORY", canvas.width / 2, canvas.height / 2);
    } else if (gameState === "LOSE") {
        ctx.fillStyle = "rgba(0,0,0,0.85)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#ea2027";
        ctx.font = "bold 45px Arial";
        ctx.textAlign = "center";
        ctx.fillText("DEFEAT", canvas.width / 2, canvas.height / 2);
    }
}

function loop() {
    updateLogic();
    renderGraphics();
    requestAnimationFrame(loop);
}

loop();
</script>
"""

# Chèn tệp mã nguồn HTML vào Streamlit
str.components.v1.html(game_html_code, height=500)
