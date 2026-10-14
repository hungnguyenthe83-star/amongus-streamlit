    ctx.textAlign = "left";
    let pct = (player.tasksDone / player.totalTasks) * 100;
    // SỬA TẠI ĐÂY: Thêm dấu ngoặc kép bao quanh dòng chữ TASK PROGRESS:
    ctx.fillText("TASK PROGRESS:", 20, 30); 
    ctx.fillStyle = "#2c3e50";
    ctx.fillRect(140, 18, 150, 15);
    ctx.fillStyle = "#2ecc71";
    ctx.fillRect(140, 18, (pct / 100) * 150, 15);

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
            if (w.connected) {
                let targetRight = wiringGame.rightWires.find(rw => rw.id === w.id);
                ctx.strokeStyle = w.color; ctx.lineWidth = 6;
                ctx.beginPath(); ctx.moveTo(260, w.y); ctx.lineTo(540, targetRight.y); ctx.stroke();
            }
        });
        
        wiringGame.rightWires.forEach(rw => {
            ctx.fillStyle = rw.color;
            ctx.fillRect(540, rw.y - 10, 20, 20);
        });
    }

    if (showRoleScreen) {
        ctx.fillStyle = "#000000";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.font = "bold 45px Arial";
        ctx.textAlign = "center";
        ctx.fillStyle = player.role === "IMPOSTER" ? "#ff3e3e" : "#00d2ff";
        ctx.fillText(player.role, canvas.width / 2, canvas.height / 2 - 20);
        ctx.font = "16px Arial";
        ctx.fillStyle = "#ffffff";
        ctx.fillText(player.role === "IMPOSTER" ? "Bí mật tiêu diệt toàn bộ phi hành đoàn!" : "Đi làm nhiệm vụ sửa điện và cảnh giác!", canvas.width / 2, canvas.height / 2 + 30);
    }

    if (gameState === "WIN") {
        ctx.fillStyle = "rgba(0,0,0,0.9)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#2ecc71"; ctx.font = "bold 45px Arial"; ctx.textAlign = "center";
        ctx.fillText("VICTORY", canvas.width / 2, canvas.height / 2);
    } else if (gameState === "LOSE") {
        ctx.fillStyle = "rgba(0,0,0,0.9)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#e74c3c"; ctx.font = "bold 45px Arial"; ctx.textAlign = "center";
        ctx.fillText("DEFEAT", canvas.width / 2, canvas.height / 2);
    }
}

function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
}
loop();
