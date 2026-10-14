import streamlit as str

# Cấu hình giao diện Streamlit hiển thị rộng rãi để chơi game
str.set_page_config(page_title="Among Us 2D - Streamlit Edition", layout="wide")

str.markdown("""
    <style>
        /* Tối ưu hóa giao diện Streamlit ẩn bớt các khoảng trống thừa */
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        /* Khung chứa game */
        .game-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: 'Courier New', Courier, monospace;
            background-color: #0b0e14;
            color: #ffffff;
            padding: 10px;
            border-radius: 12px;
            box-shadow: 0px 8px 24px rgba(0,0,0,0.7);
        }
        
        .game-title {
            color: #ff4747;
            font-weight: bold;
            text-shadow: 2px 2px #000;
            margin-bottom: 5px;
        }

        .instructions {
            background: #161c24;
            padding: 8px 15px;
            border-radius: 8px;
            font-size: 13px;
            margin-bottom: 10px;
            border-left: 4px solid #00bcff;
        }

        canvas {
            border: 4px solid #3a4454;
            background-color: #111721;
            box-shadow: inset 0 0 20px #000;
            border-radius: 8px;
            cursor: crosshair;
        }
    </style>
""", unsafe_allow_html=True)

# Giao diện hiển thị phía trên Canvas game
str.markdown("""
<div class="game-wrapper">
    <h1 class="game-title">AMONG US 2D</h1>
    <div class="instructions">
        🕹️ <b>Cách chơi:</b> Dùng các phím <b>W, A, S, D</b> hoặc <b>Phím Mũi Tên</b> để di chuyển. <br>
        🎯 <b>Nhiệm vụ:</b> Đến gần các chấm màu <b>Vàng (Task)</b> để sửa máy. Né tránh Bot màu <b>Đỏ (Imposter)</b> kẻo bị ám sát!
    </div>
</div>
""", unsafe_allow_html=True)

# Toàn bộ logic game viết bằng JavaScript chạy trực tiếp trên trình duyệt của người dùng
game_js_html = """
<div style="display: flex; justify-content: center;">
    <canvas id="amongUsCanvas" width="800" height="500"></canvas>
</div>

<script>
const canvas = document.getElementById("amongUsCanvas");
const ctx = canvas.getContext("2d");

// Cấu hình Người chơi (Crewmate Xanh)
const player = {
    x: 100,
    y: 250,
    size: 15,
    speed: 4,
    color: "#00d2ff",
    tasksCompleted: 0
};

// Cấu hình Kẻ giả mạo (Imposter Đỏ chạy tự động)
const imposter = {
    x: 700,
    y: 250,
    size: 15,
    speed: 2,
    color: "#ff3333",
    state: "patrol", // patrol hoặc chase
    targetX: 700,
    targetY: 250
};

// Danh sách các phòng và Vị trí nhiệm vụ (Màu vàng)
const tasks = [
    { name: "Cafeteria", x: 400, y: 80, radius: 20, completed: false },
    { name: "Electrical", x: 150, y: 400, radius: 20, completed: false },
    { name: "Weapons", x: 650, y: 120, radius: 20, completed: false },
    { name: "Navigation", x: 720, y: 300, radius: 20, completed: false }
];

// Trạng thái chung của Trận đấu
let gameState = "PLAYING"; // PLAYING, WIN, LOSE
const keys = {};

// Lắng nghe sự kiện bàn phím
window.addEventListener("keydown", (e) => { keys[e.key.toLowerCase()] = true; });
window.addEventListener("keyup", (e) => { keys[e.key.toLowerCase()] = false; });

// Hàm tính khoảng cách giữa 2 vật thể
function getDistance(x1, y1, x2, y2) {
    return Math.hypot(x2 - x1, y2 - y1);
}

// Xử lý Logic di chuyển và va chạm từng khung hình
function update() {
    if (gameState !== "PLAYING") return;

    // 1. Di chuyển Người chơi bằng phím W-A-S-D hoặc Arrow Keys
    if (keys["w"] || keys["arrowup"]) player.y -= player.speed;
    if (keys["s"] || keys["arrowdown"]) player.y += player.speed;
    if (keys["a"] || keys["arrowleft"]) player.x -= player.speed;
    if (keys["d"] || keys["arrowright"]) player.x += player.speed;

    // Giới hạn người chơi không chạy ra khỏi viền map
    player.x = Math.max(player.size, Math.min(canvas.width - player.size, player.x));
    player.y = Math.max(player.size, Math.min(canvas.height - player.size, player.y));

    // 2. Xử lý làm nhiệm vụ khi đứng đè lên chấm Vàng
    tasks.forEach(task => {
        if (!task.completed && getDistance(player.x, player.y, task.x, task.y) < task.radius + player.size) {
            task.completed = true;
            player.tasksCompleted++;
            if (player.tasksCompleted === tasks.length) {
                gameState = "WIN";
            }
        }
    });

    // 3. AI của Imposter (Kẻ giết người tự động rượt đuổi)
    let distToPlayer = getDistance(imposter.x, imposter.y, player.x, player.y);
    
    if (distToPlayer < 180) {
        // Nếu phát hiện Crewmate ở gần, chuyển sang chế độ Săn Đuổi
        imposter.state = "chase";
        let angle = Math.atan2(player.y - imposter.y, player.x - imposter.x);
        imposter.x += Math.cos(angle) * imposter.speed;
        imposter.y += Math.sin(angle) * imposter.speed;
    } else {
        // Đi tuần tra tự động giữa các phòng ngẫu nhiên
        if (imposter.state === "chase" || getDistance(imposter.x, imposter.y, imposter.targetX, imposter.targetY) < 10) {
            imposter.state = "patrol";
            imposter.targetX = Math.random() * (canvas.width - 40) + 20;
            imposter.targetY = Math.random() * (canvas.height - 40) + 20;
        }
        let angle = Math.atan2(imposter.targetY - imposter.y, imposter.targetX - imposter.x);
        imposter.x += Math.cos(angle) * (imposter.speed * 0.8);
        imposter.y += Math.sin(angle) * (imposter.speed * 0.8);
    }

    // 4. Kiểm tra điều kiện thua cuộc (Imposter chạm trúng Crewmate)
    if (distToPlayer < player.size + imposter.size) {
        gameState = "LOSE";
    }
}

// Hàm vẽ Đồ họa lên màn hình canvas
function draw() {
    // Xóa màn hình cũ để vẽ khung hình mới
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Vẽ nền Bản đồ (Hệ thống lưới vũ trụ đơn giản)
    ctx.strokeStyle = "#1b2436";
    ctx.lineWidth = 1;
    for (let i = 0; i < canvas.width; i += 40) {
        ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
    }
    for (let j = 0; j < canvas.height; j += 40) {
        ctx.beginPath(); ctx.moveTo(0, j); ctx.lineTo(canvas.width, j); ctx.stroke();
    }

    // Vẽ các Khu vực Nhiệm vụ (Vòng tròn Vàng)
    tasks.forEach(task => {
        ctx.beginPath();
        ctx.arc(task.x, task.y, task.radius, 0, Math.PI * 2);
        ctx.fillStyle = task.completed ? "rgba(46, 204, 113, 0.2)" : "rgba(241, 196, 15, 0.3)";
        ctx.fill();
        ctx.strokeStyle = task.completed ? "#2ecc71" : "#f1c40f";
        ctx.lineWidth = 2;
        ctx.stroke();

        // Tên phòng
        ctx.fillStyle = "#a5b1c2";
        ctx.font = "11px Arial";
        ctx.textAlign = "center";
        ctx.fillText(task.name, task.x, task.y - task.radius - 5);
    });

    // Vẽ Nhân vật Người chơi (Crewmate) kèm Kính bảo hộ đặc trưng
    ctx.beginPath();
    ctx.arc(player.x, player.y, player.size, 0, Math.PI * 2);
    ctx.fillStyle = player.color;
    ctx.fill();
    // Kính bảo hộ
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(player.x + 2, player.y - 6, 8, 8);

    // Vẽ Nhân vật AI Kẻ địch (Imposter Đỏ)
    ctx.beginPath();
    ctx.arc(imposter.x, imposter.y, imposter.size, 0, Math.PI * 2);
    ctx.fillStyle = imposter.color;
    ctx.fill();
    // Kính bảo hộ Imposter
    ctx.fillStyle = "#636e72";
    ctx.fillRect(imposter.x - 10, imposter.y - 6, 8, 8);

    // Hiển thị thanh Tiến trình làm nhiệm vụ (Task Bar) ở góc trên
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 14px Arial";
    ctx.textAlign = "left";
    ctx.fillText(`TOTAL TASKS COMPLETED: ${player.tasksCompleted} / ${tasks.length}`, 20, 30);

    // Giao diện khi Thắng hoặc Thua cuộc
    if (gameState === "WIN") {
        ctx.fillStyle = "rgba(0, 0, 0, 0.8)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#2ecc71";
        ctx.font = "bold 40px Courier New";
        ctx.textAlign = "center";
        ctx.fillText("VICTORY", canvas.width / 2, canvas.height / 2);
        ctx.font = "16px Arial";
        ctx.fillStyle = "#ffffff";
        ctx.fillText("Bạn đã hoàn thành xuất sắc toàn bộ nhiệm vụ!", canvas.width / 2, canvas.height / 2 + 50);
    } else if (gameState === "LOSE") {
        ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#e74c3c";
        ctx.font = "bold 40px Courier New";
        ctx.textAlign = "center";
        ctx.fillText("DEFEAT", canvas.width / 2, canvas.height / 2);
        ctx.font = "16px Arial";
        ctx.fillStyle = "#ffffff";
        ctx.fillText("Bạn đã bị Imposter sát hại bí mật!", canvas.width / 2, canvas.height / 2 + 50);
    }
}

// Vòng lặp Core của Game chạy liên tục 60 khung hình / giây
function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

// Khởi chạy game
gameLoop();
</script>
"""

# Truyền mã nguồn HTML5/JS vào giao diện Streamlit
str.components.v1.html(game_js_html, height=530)
