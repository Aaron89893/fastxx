/**
 * ⚡ SCRIPT AUTO CLICK TRẮC NGHIỆM LMS UNIAPP (DÙNG TRỰC TIẾP TRÊN TRÌNH DUYỆT) ⚡
 * Tự động chọn Option B (2) và bấm 'Lưu câu trả lời và tiếp tục' để đảm bảo câu hỏi chuyển sang màu xanh (Đã trả lời).
 */

(function () {
    const oldPanel = document.getElementById('uniapp-auto-helper');
    if (oldPanel) oldPanel.remove();

    let isRunning = false;
    let targetOption = 'B'; // A, B, C, D, RANDOM
    let delayMs = 1500;
    let completedCount = 0;

    const panel = document.createElement('div');
    panel.id = 'uniapp-auto-helper';
    panel.style.cssText = `
        position: fixed;
        bottom: 25px;
        left: 25px;
        z-index: 999999;
        background: rgba(18, 24, 38, 0.95);
        color: #ffffff;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.1);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 13px;
        width: 300px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    `;

    panel.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.15); padding-bottom: 8px;">
            <div style="font-weight: 700; color: #38bdf8; font-size: 14px; display: flex; align-items: center; gap: 6px;">
                <span>⚡</span> LMS Auto Clicker (Đã lưu)
            </div>
            <button id="close-panel-btn" style="background: none; border: none; color: #94a3b8; font-size: 16px; cursor: pointer; padding: 0 4px;">✕</button>
        </div>
        
        <div style="margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
            <label style="color: #cbd5e1;">Chọn đáp án:</label>
            <select id="auto-opt-select" style="background: #334155; color: #fff; border: 1px solid #475569; padding: 4px 8px; border-radius: 6px; font-weight: 600; cursor: pointer;">
                <option value="A">Option A (1)</option>
                <option value="B" selected>Option B (2)</option>
                <option value="C">Option C (3)</option>
                <option value="D">Option D (4)</option>
                <option value="RANDOM">Ngẫu nhiên</option>
            </select>
        </div>

        <div style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
            <label style="color: #cbd5e1;">Tốc độ chờ:</label>
            <select id="auto-delay-select" style="background: #334155; color: #fff; border: 1px solid #475569; padding: 4px 8px; border-radius: 6px; cursor: pointer;">
                <option value="1000">1.0 giây</option>
                <option value="1500" selected>1.5 giây</option>
                <option value="2000">2.0 giây</option>
                <option value="3000">3.0 giây</option>
            </select>
        </div>

        <div style="margin-bottom: 12px; background: rgba(0,0,0,0.25); padding: 8px 10px; border-radius: 6px;">
            <div style="color: #94a3b8; font-size: 12px;">Trạng thái: <span id="auto-status-text" style="color: #facc15; font-weight: 600;">Sẵn sàng</span></div>
            <div style="color: #94a3b8; font-size: 12px; margin-top: 3px;">Đã hoàn thành: <span id="auto-count-text" style="color: #38bdf8; font-weight: 600;">0</span> câu</div>
        </div>

        <div style="display: flex; gap: 8px;">
            <button id="toggle-run-btn" style="flex: 1; background: #2563eb; color: #fff; border: none; padding: 8px 12px; border-radius: 6px; font-weight: 600; cursor: pointer; transition: background 0.2s;">
                ▶ Bắt đầu chạy
            </button>
        </div>
    `;

    document.body.appendChild(panel);

    const toggleBtn = document.getElementById('toggle-run-btn');
    const statusText = document.getElementById('auto-status-text');
    const countText = document.getElementById('auto-count-text');
    const optSelect = document.getElementById('auto-opt-select');
    const delaySelect = document.getElementById('auto-delay-select');
    const closeBtn = document.getElementById('close-panel-btn');

    closeBtn.onclick = () => {
        stopAuto();
        panel.remove();
    };

    optSelect.onchange = (e) => { targetOption = e.target.value; };
    delaySelect.onchange = (e) => { delayMs = parseInt(e.target.value); };

    function getUnansweredList() {
        const paletteBtns = Array.from(document.querySelectorAll('button')).filter(b => /^[0-9]+$/.test((b.innerText || '').trim()));
        if (paletteBtns.length === 0) return null;
        let list = [];
        for (let b of paletteBtns) {
            let num = parseInt(b.innerText.trim());
            let cs = window.getComputedStyle(b);
            let isGreen = b.className.includes('iXcCdn') || cs.backgroundColor.includes('220, 252, 231');
            if (!isGreen) list.push(num);
        }
        return { total: paletteBtns.length, unanswered: list };
    }

    function jumpToPalette(qNum) {
        const paletteBtns = Array.from(document.querySelectorAll('button')).filter(b => (b.innerText || '').trim() === String(qNum));
        if (paletteBtns.length > 0) {
            paletteBtns[0].scrollIntoView({ behavior: 'auto', block: 'center' });
            paletteBtns[0].click();
            return true;
        }
        return false;
    }

    function selectOption(choice) {
        let index = 1;
        if (choice === 'A') index = 0;
        else if (choice === 'B') index = 1;
        else if (choice === 'C') index = 2;
        else if (choice === 'D') index = 3;

        let labels = Array.from(document.querySelectorAll('.form-check-label, label'));
        let radios = Array.from(document.querySelectorAll("input[type='radio'], .form-check-input"));
        if (radios.length === 0 && labels.length === 0) return null;

        if (choice === 'RANDOM') {
            index = Math.floor(Math.random() * (radios.length || labels.length || 4));
        }

        if (radios.length > 0 && index >= radios.length) index = radios.length - 1;
        if (labels.length > 0 && index >= labels.length) index = labels.length - 1;

        const clickTarget = (labels.length > index) ? labels[index] : radios[index];
        const r = (radios.length > index) ? radios[index] : null;

        clickTarget.scrollIntoView({ behavior: 'auto', block: 'center' });
        const opts = { bubbles: true, cancelable: true, view: window };
        clickTarget.dispatchEvent(new PointerEvent('pointerdown', opts));
        clickTarget.dispatchEvent(new MouseEvent('mousedown', opts));
        clickTarget.dispatchEvent(new PointerEvent('pointerup', opts));
        clickTarget.dispatchEvent(new MouseEvent('mouseup', opts));
        clickTarget.click();

        if (r) {
            r.checked = true;
            try {
                let proto = window.HTMLInputElement.prototype;
                let setter = Object.getOwnPropertyDescriptor(proto, 'checked').set;
                if (setter) setter.call(r, true);
            } catch(e) {}
            r.dispatchEvent(new Event('input', { bubbles: true }));
            r.dispatchEvent(new Event('change', { bubbles: true }));
        }

        return { index: index + 1, total: Math.max(radios.length, labels.length) };
    }

    function clickSaveButtonOnly() {
        const buttons = Array.from(document.querySelectorAll('button.btn-primary, button.btn')).filter(b => b.offsetWidth > 0 && b.offsetHeight > 0);

        // 1. Chỉ tìm nút "Lưu câu trả lời và tiếp tục"
        for (let b of buttons) {
            let t = (b.innerText || b.value || '').trim().toLowerCase();
            if (t.includes('lưu câu trả lời') || t.includes('luu cau tra loi') || t.includes('lưu')) {
                b.scrollIntoView({ behavior: 'auto', block: 'center' });
                b.click();
                return { action: 'saved', text: b.innerText.trim() };
            }
        }

        // 2. Kiểm tra nút Nộp bài / Hoàn thành
        for (let b of buttons) {
            let t = (b.innerText || b.value || '').trim().toLowerCase();
            if (t.includes('nộp bài') || t.includes('nop bai') || t.includes('hoàn thành')) {
                return { action: 'finish', text: b.innerText.trim() };
            }
        }

        // KHÔNG BẤM NÚT "Tiếp tục" nếu chưa lưu!
        return null;
    }

    function step() {
        if (!isRunning) return;

        const palInfo = getUnansweredList();
        if (palInfo) {
            if (palInfo.unanswered.length === 0) {
                statusText.innerText = `Đã làm xong tất cả ${palInfo.total}/${palInfo.total} câu! Đang nộp bài...`;
                statusText.style.color = '#4ade80';
                setTimeout(() => {
                    const buttons = Array.from(document.querySelectorAll('button, a.btn, input[type="button"]')).filter(b => b.offsetWidth > 0 && b.offsetHeight > 0);
                    for (let b of buttons) {
                        let t = (b.innerText || b.value || '').trim().toLowerCase();
                        if (t.includes('kết thúc bài làm') || t.includes('kết thúc') || t.includes('nộp bài') || t.includes('hoàn thành')) {
                            b.click();
                            statusText.innerText = `Đã bấm: '${b.innerText.trim()}'!`;
                            break;
                        }
                    }
                    setTimeout(() => {
                        let modalBtns = Array.from(document.querySelectorAll('.modal button, .swal2-container button, [role="dialog"] button, button')).filter(b => b.offsetWidth > 0 && b.offsetHeight > 0);
                        for (let mb of modalBtns) {
                            let mt = (mb.innerText || mb.value || '').trim().toLowerCase();
                            if (mt.includes('kết thúc bài làm') || mt.includes('kết thúc') || mt.includes('đồng ý') || mt.includes('xác nhận') || mt === 'ok') {
                                mb.click();
                                statusText.innerText = `[🎉] Đã nộp bài thành công!`;
                                break;
                            }
                        }
                    }, 1500);
                }, 1000);
                stopAuto();
                return;
            }
            // Nhảy tới câu chưa trả lời
            const nextQ = palInfo.unanswered[0];
            jumpToPalette(nextQ);
        }

        // Chọn đáp án
        setTimeout(() => {
            if (!isRunning) return;
            const sel = selectOption(targetOption);
            if (!sel) {
                // Kiểm tra thông báo Cooldown (chờ XX giây) giữa 2 bài test
                let alerts = Array.from(document.querySelectorAll('.toast, .alert, [role="alert"], [class*="toast"], [class*="alert"], [class*="notification"]'));
                let allText = alerts.map(a => a.innerText || '').join(' ') + ' ' + (document.body.innerText || '');
                let match = allText.match(/vui lòng đợi\\s*(\\d+)\\s*giây/i) || allText.match(/đợi\\s*(\\d+)\\s*giây/i);
                if (match) {
                    let sec = parseInt(match[1]);
                    statusText.innerText = `Chờ cooldown hệ thống: ${sec}s...`;
                    statusText.style.color = '#f97316';
                    setTimeout(step, (sec + 2) * 1000);
                    return;
                }

                // Kiểm tra nút 'Bắt đầu làm bài' / 'Thực hiện lại' nếu đang ở trang giới thiệu bài thi
                const startBtn = Array.from(document.querySelectorAll('button, a, [role="button"]')).find(b => {
                    let t = (b.innerText || '').toLowerCase();
                    if (t.includes('lịch sử') || t.includes('quay lại') || t.includes('xem lại bài làm')) return false;
                    return t.includes('thực hiện lại') || t.includes('thực hiện') || t.includes('làm lại') || t.includes('thi lại') || t.includes('bắt đầu làm bài') || t === 'bắt đầu' || t.includes('bắt đầu') || t === 'làm bài';
                });
                if (startBtn) {
                    startBtn.click();
                    statusText.innerText = `Đã bấm: ${startBtn.innerText.trim()}!`;
                    statusText.style.color = '#38bdf8';
                    setTimeout(step, 2500);
                    return;
                }
                statusText.innerText = 'Đang tải câu hỏi...';
                statusText.style.color = '#facc15';
                setTimeout(step, 800);
                return;
            }

            statusText.innerText = `Đã chọn đáp án ${sel.index}/${sel.total}`;
            statusText.style.color = '#38bdf8';

            // Chờ nút 'Lưu câu trả lời' và bấm
            let attempts = 0;
            const saveInterval = setInterval(() => {
                if (!isRunning) {
                    clearInterval(saveInterval);
                    return;
                }
                attempts++;
                const saveRes = clickSaveButtonOnly();
                if (saveRes) {
                    clearInterval(saveInterval);
                    completedCount++;
                    countText.innerText = completedCount;
                    statusText.innerText = `[✓] Đã Lưu câu trả lời!`;
                    statusText.style.color = '#4ade80';
                    setTimeout(step, delayMs);
                } else if (attempts >= 6) {
                    clearInterval(saveInterval);
                    // Thử chọn lại và tiếp tục
                    selectOption(targetOption);
                    setTimeout(step, 1000);
                }
            }, 300);
        }, 300);
    }

    function startAuto() {
        isRunning = true;
        toggleBtn.innerText = '⏸ Tạm dừng';
        toggleBtn.style.background = '#dc2626';
        statusText.innerText = 'Đang tự động chạy...';
        statusText.style.color = '#4ade80';
        step();
    }

    function stopAuto() {
        isRunning = false;
        toggleBtn.innerText = '▶ Tiếp tục';
        toggleBtn.style.background = '#2563eb';
        if (statusText.innerText.includes('Đang')) {
            statusText.innerText = 'Đã tạm dừng';
            statusText.style.color = '#facc15';
        }
    }

    toggleBtn.onclick = () => {
        if (isRunning) stopAuto();
        else startAuto();
    };

    console.log('%c[LMS Auto Tool] Đã nạp thành công! Ưu tiên click Lưu câu trả lời và tiếp tục.', 'color: #38bdf8; font-weight: bold; font-size: 14px;');
})();
