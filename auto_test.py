"""
⚡ TOOL AUTOMATION AUTO-CLICK TRẮC NGHIỆM LMS UNIAPP (MULTI-TEST) ⚡
Tự động đọc danh sách link bài test từ file urls.txt, tự động đăng nhập, làm lần lượt từng bài test
(chọn đáp án B và bấm 'Lưu câu trả lời và tiếp tục'), khi hoàn thành bài test này sẽ tự chuyển sang bài tiếp theo cho tới khi hoàn tất toàn bộ danh sách.
"""

import sys
import os
import time
import argparse
import io

# Thiết lập UTF-8 cho console Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from colorama import init, Fore, Style
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

init(autoreset=True)


def banner():
    print(Fore.CYAN + "=" * 70)
    print(Fore.YELLOW + Style.BRIGHT + "   ⚡ TOOL TỰ ĐỘNG LÀM BÀI TRẮC NGHIỆM LMS UNIAPP (MULTI-TEST) ⚡")
    print(Fore.CYAN + "   - Đăng nhập 1 lần duy nhất lúc khởi động")
    print(Fore.CYAN + "   - Đọc danh sách link bài kiểm tra từ file 'urls.txt'")
    print(Fore.CYAN + "   - Ưu tiên bấm 'Lưu câu trả lời và tiếp tục' để lưu trạng thái")
    print(Fore.CYAN + "   - Hoàn tất bài này sẽ TỰ ĐỘNG CHUYỂN sang link tiếp theo")
    print(Fore.CYAN + "=" * 70 + "\n")


def create_driver(headless: bool = False):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.set_capability("unhandledPromptBehavior", "accept")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception:
        driver = webdriver.Chrome(options=options)

    try:
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception:
        pass

    return driver


def perform_login(driver, username, password):
    """Tự động đăng nhập vào LMS Uniapp."""
    print(Fore.BLUE + f"[*] Đang mở trang đăng nhập...")
    driver.get("https://lms.uniapp.vn/elearning/login")
    
    wait = WebDriverWait(driver, 15)
    user_inp = wait.until(EC.presence_of_element_located((By.ID, "loginUsername")))
    pass_inp = driver.find_element(By.ID, "loginPassword")
    
    print(Fore.BLUE + f"[*] Đang điền tài khoản: {username}...")
    user_inp.clear()
    user_inp.send_keys(username)
    pass_inp.clear()
    pass_inp.send_keys(password)
    
    btn = driver.find_element(By.XPATH, "//button[@type='submit' and contains(., 'Đăng nhập')]")
    btn.click()
    
    print(Fore.GREEN + "[✓] Đã gửi thông tin đăng nhập thành công. Đang chờ chuyển hướng...\n")
    time.sleep(3.5)


def load_urls_from_file(file_path: str):
    """Đọc danh sách link từ file văn bản."""
    if not os.path.exists(file_path):
        return []
    
    urls = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def get_answered_count(driver):
    """Lấy số lượng câu hỏi đã trả lời hiện tại trên trang (Ví dụ: '25/185 câu')."""
    try:
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        for line in body_text.split('\n'):
            if '/185' in line or '/ ' in line:
                return line.strip()
    except Exception:
        pass
    return ""


# --- CÁC SCRIPT JAVASCRIPT ĐIỀU KHIỂN DOM ĐƯỢC TỐI ƯU ---

JS_GET_PALETTE = """
return (function() {
    let paletteBtns = Array.from(document.querySelectorAll('button')).filter(b => /^[0-9]+$/.test((b.innerText || '').trim()));
    if (paletteBtns.length === 0) {
        return { hasPalette: false, total: 0, unanswered: [], answeredCount: 0 };
    }

    let activeBtn = paletteBtns.find(b => b.className.includes('lmztXy') || window.getComputedStyle(b).backgroundColor.includes('37, 99, 235'));
    let activeChecked = document.querySelectorAll("input[type='radio']:checked").length > 0;

    let unanswered = [];
    let answered = [];
    for (let b of paletteBtns) {
        let num = parseInt(b.innerText.trim());
        let cs = window.getComputedStyle(b);
        let isGreen = b.className.includes('iXcCdn') || cs.backgroundColor.includes('220, 252, 231');
        let isWhite = b.className.includes('cRhGXV') || cs.backgroundColor.includes('255, 255, 255') || cs.borderColor.includes('226, 232, 240');
        let isActive = (b === activeBtn);

        if (isGreen) {
            answered.push(num);
        } else if (isWhite) {
            unanswered.push(num);
        } else if (isActive) {
            if (activeChecked) {
                answered.push(num);
            } else {
                unanswered.push(num);
            }
        } else {
            unanswered.push(num);
        }
    }
    return {
        hasPalette: true,
        total: paletteBtns.length,
        answeredCount: answered.length,
        unanswered: unanswered
    };
})();
"""

JS_JUMP_PALETTE = """
return (function(qNum) {
    let paletteBtns = Array.from(document.querySelectorAll('button')).filter(b => (b.innerText || '').trim() === String(qNum));
    if (paletteBtns.length > 0) {
        paletteBtns[0].scrollIntoView({ behavior: 'auto', block: 'center' });
        paletteBtns[0].click();
        return true;
    }
    return false;
})(arguments[0]);
"""

JS_CHECK_PALETTE_GREEN = """
return (function(qNum) {
    let paletteBtns = Array.from(document.querySelectorAll('button')).filter(b => (b.innerText || '').trim() === String(qNum));
    if (paletteBtns.length === 0) return false;
    let b = paletteBtns[0];
    let cs = window.getComputedStyle(b);
    return b.className.includes('iXcCdn') || cs.backgroundColor.includes('220, 252, 231');
})(arguments[0]);
"""

JS_SELECT_RADIO = """
return (function(targetIdx) {
    let labels = Array.from(document.querySelectorAll('.form-check-label, label'));
    let radios = Array.from(document.querySelectorAll("input[type='radio'], .form-check-input"));
    if (radios.length === 0 && labels.length === 0) {
        return { success: false, message: 'Không tìm thấy đáp án' };
    }

    if (targetIdx >= radios.length && radios.length > 0) targetIdx = radios.length - 1;
    if (targetIdx >= labels.length && labels.length > 0) targetIdx = labels.length - 1;

    let clickTarget = (labels.length > targetIdx) ? labels[targetIdx] : radios[targetIdx];
    let r = (radios.length > targetIdx) ? radios[targetIdx] : null;

    clickTarget.scrollIntoView({ behavior: 'auto', block: 'center' });
    let opts = { bubbles: true, cancelable: true, view: window };
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

    let text = (clickTarget.innerText || (r ? r.value : '')).trim();
    return {
        success: true,
        text: text.replace(/\\s+/g, ' ')
    };
})(arguments[0]);
"""

JS_CLICK_SAVE_BUTTON = """
return (function() {
    let btns = Array.from(document.querySelectorAll('button.btn-primary, button.btn')).filter(b => b.offsetWidth > 0 && b.offsetHeight > 0);
    
    // Tìm chính xác nút Lưu câu trả lời
    for (let b of btns) {
        let t = (b.innerText || '').trim().toLowerCase();
        if (t.includes('lưu câu trả lời') || t.includes('lưu')) {
            b.scrollIntoView({ behavior: 'auto', block: 'center' });
            b.click();
            return { clicked: true, action: 'saved', text: b.innerText.trim() };
        }
    }

    // Kiểm tra nút Nộp bài / Hoàn thành
    for (let b of btns) {
        let t = (b.innerText || '').trim().toLowerCase();
        if (t.includes('nộp bài') || t.includes('hoàn thành')) {
            return { clicked: false, isFinish: true, text: b.innerText.trim() };
        }
    }

    // TUYỆT ĐỐI KHÔNG BẤM NÚT 'Tiếp tục' KHI CHƯA LƯU ĐÁP ÁN (vì 'Tiếp tục' = Bỏ qua câu hỏi)
    return { clicked: false, isFinish: false };
})();
"""

JS_SUBMIT_TEST = """
return (function() {
    let allBtns = Array.from(document.querySelectorAll('button, a.btn, input[type="button"]')).filter(b => b.offsetWidth > 0 && b.offsetHeight > 0);

    // 1. ƯU TIÊN TUYỆT ĐỐI: Nút 'Kết Thúc Bài Làm' trong cửa sổ modal Xem lại câu trả lời
    for (let b of allBtns) {
        let t = (b.innerText || b.value || '').trim().toLowerCase();
        if (t.includes('lịch sử') || t.includes('quay lại') || t.includes('thu gọn')) continue;
        if (t.includes('kết thúc bài làm') || t.includes('ket thuc bai lam') || (t.includes('kết thúc') && !t.includes('lịch sử'))) {
            b.scrollIntoView({ behavior: 'auto', block: 'center' });
            b.click();
            return { clicked: true, text: (b.innerText || b.value || '').trim(), type: 'finish' };
        }
    }

    // 2. Nút 'Nộp bài' trên trang
    for (let b of allBtns) {
        let t = (b.innerText || b.value || '').trim().toLowerCase();
        if (t.includes('lịch sử') || t.includes('quay lại') || t.includes('thu gọn')) continue;
        if (t === 'nộp bài' || t === 'nop bai' || (t.includes('nộp bài') && !t.includes('đang'))) {
            b.scrollIntoView({ behavior: 'auto', block: 'center' });
            b.click();
            return { clicked: true, text: (b.innerText || b.value || '').trim(), type: 'submit' };
        }
    }

    return { clicked: false };
})();
"""

JS_CONFIRM_MODAL = """
return (function() {
    // Tìm các nút xác nhận trong dialog/modal/popup: 'Kết Thúc Bài Làm', 'Đồng ý', 'Xác nhận', 'Nộp bài'
    let modalBtns = Array.from(document.querySelectorAll('.modal button, .swal2-container button, [role="dialog"] button, button')).filter(b => b.offsetWidth > 0 && b.offsetHeight > 0);
    for (let b of modalBtns) {
        let t = (b.innerText || b.value || '').trim().toLowerCase();
        if (t.includes('lịch sử') || t.includes('quay lại') || t.includes('thu gọn')) continue;
        if (t.includes('kết thúc bài làm') || (t.includes('kết thúc') && !t.includes('lịch sử')) || t.includes('đồng ý') || t.includes('xác nhận') || t === 'ok') {
            b.click();
            return { clicked: true, text: (b.innerText || b.value || '').trim() };
        }
    }
    return { clicked: false };
})();
"""


JS_CLICK_START_TEST = """
return (function() {
    let elements = Array.from(document.querySelectorAll('button, a, [role="button"], input[type="button"]')).filter(el => el.offsetWidth > 0 && el.offsetHeight > 0);
    for (let el of elements) {
        let t = (el.innerText || el.value || '').trim().toLowerCase();
        if (t.includes('lịch sử') || t.includes('quay lại') || t.includes('thu gọn') || t.includes('xem lại bài làm')) continue;
        if (t.includes('thực hiện lại') || t.includes('thuc hien lai') || t.includes('thực hiện') ||
            t.includes('làm lại') || t.includes('lam lai') || t.includes('thi lại') || t.includes('thi lai') ||
            t.includes('bắt đầu làm bài') || t.includes('bat dau lam bai') || t === 'bắt đầu' || t === 'bat dau' ||
            t.includes('bắt đầu') || t === 'làm bài' || t.includes('làm bài') || (t.includes('tiếp tục') && !t.includes('tiếp theo:'))) {
            el.scrollIntoView({ behavior: 'auto', block: 'center' });
            el.click();
            return { clicked: true, text: (el.innerText || el.value || '').trim() };
        }
    }
    return { clicked: false };
})();
"""


def check_cooldown_and_wait(driver):
    """Kiểm tra thông báo giới hạn thời gian chờ giữa 2 bài test liên tiếp của LMS và tự động đếm ngược chờ."""
    cooldown_info = driver.execute_script("""
        return (function() {
            let alerts = Array.from(document.querySelectorAll('.toast, .alert, [role="alert"], [class*="toast"], [class*="alert"], [class*="notification"]'));
            let allText = alerts.map(a => a.innerText || '').join(' ') + ' ' + (document.body.innerText || '');
            let match = allText.match(/vui lòng đợi\\s*(\\d+)\\s*giây/i) || allText.match(/đợi\\s*(\\d+)\\s*giây/i);
            if (match) {
                return { hasCooldown: true, seconds: parseInt(match[1]) };
            }
            if (allText.includes('vui lòng đợi giây lát rồi bắt đầu bài mới') || allText.includes('bạn vừa bắt đầu một bài làm')) {
                return { hasCooldown: true, seconds: 60 };
            }
            return { hasCooldown: false, seconds: 0 };
        })();
    """)
    if cooldown_info and cooldown_info.get("hasCooldown"):
        sec = cooldown_info.get("seconds", 60)
        print(Fore.YELLOW + Style.BRIGHT + f"\n[⏳] HỆ THỐNG YÊU CẦU CHỜ GIỮA 2 BÀI TEST: Cần đợi {sec} giây...")
        for remaining in range(sec + 2, 0, -1):
            sys.stdout.write(Fore.YELLOW + f"\r    ➔ Đang đếm ngược: còn {remaining} giây... ")
            sys.stdout.flush()
            time.sleep(1)
        print(Fore.GREEN + "\r    ➔ Đã hết thời gian chờ! Tiếp tục bấm 'Bắt đầu làm bài'...        \n")
        return True
    return False


def run_single_test(driver, target_url: str, test_index: int, total_tests: int,
                    option_choice: str = "B", delay: float = 1.0,
                    auto_submit: bool = True, max_questions: int = 250):
    """Thực thi tự động làm một bài kiểm tra đơn lẻ với kiểm tra xác nhận lưu câu hỏi chặt chẽ."""
    print(Fore.MAGENTA + "=" * 70)
    print(Fore.YELLOW + Style.BRIGHT + f"   🚀 ĐANG LÀM BÀI TEST [{test_index}/{total_tests}]")
    print(Fore.CYAN + f"   🔗 Link: {target_url}")
    print(Fore.MAGENTA + "=" * 70)

    driver.get(target_url)
    time.sleep(3.5)

    # Chặn các popup cảnh báo rời trang
    try:
        driver.execute_script("""
            window.onbeforeunload = null;
            window.alert = function() { return true; };
            window.confirm = function() { return true; };
        """)
    except Exception:
        pass

    # 1. ĐẢM BẢO VÀO ĐƯỢC BÀI THI (Xử lý nút 'Bắt đầu làm bài' và Cooldown chống spam giữa 2 bài)
    entered_test = False
    for enter_attempt in range(25):
        # Đóng alert bất ngờ nếu có
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except Exception:
            pass

        # Kiểm tra xem đã có câu hỏi (radios) trên trang hay chưa
        radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio'], .form-check-input")
        if len(radios) > 0:
            entered_test = True
            break

        # Kiểm tra xem có bị thông báo Cooldown (chờ XX giây) hay không
        if check_cooldown_and_wait(driver):
            start_res = driver.execute_script(JS_CLICK_START_TEST)
            if start_res and start_res.get("clicked"):
                print(Fore.CYAN + f"[*] Đã bấm lại nút vào làm bài: '{start_res.get('text')}'!")
            time.sleep(3)
            continue

        # Thử tìm và click nút 'Bắt đầu làm bài' / 'Tiếp tục'
        start_res = driver.execute_script(JS_CLICK_START_TEST)
        if start_res and start_res.get("clicked"):
            btn_txt = start_res.get("text", "")
            print(Fore.CYAN + f"[*] Đã bấm nút vào làm bài: '{btn_txt}'! Đang kiểm tra phản hồi...")
            time.sleep(2)

            # Kiểm tra xem hệ thống có trả về thông báo Cooldown sau cú click không
            if check_cooldown_and_wait(driver):
                driver.execute_script(JS_CLICK_START_TEST)
                time.sleep(3)
                continue

            time.sleep(2)
        else:
            time.sleep(1)

    # Kiểm tra bảo đảm đã vào được câu hỏi, nếu vẫn ở trang giới thiệu thì không chạy vòng lặp câu hỏi
    radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio'], .form-check-input")
    if len(radios) == 0:
        pal = driver.execute_script(JS_GET_PALETTE)
        if not (pal and pal.get("hasPalette")):
            print(Fore.RED + f"\n[X] Không thể vào làm bài test (vẫn ở trang giới thiệu hoặc chưa bấm được nút Bắt đầu). Bỏ qua bài này.\n")
            return

    # Xác định chỉ số đáp án cần chọn
    target_idx = 1  # Mặc định Option B
    opt_str = str(option_choice).strip().upper()
    if opt_str in ['A', '1']: target_idx = 0
    elif opt_str in ['B', '2']: target_idx = 1
    elif opt_str in ['C', '3']: target_idx = 2
    elif opt_str in ['D', '4']: target_idx = 3

    # Chờ các đáp án của câu hỏi đầu tiên nạp xong
    for _ in range(15):
        radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio'], .form-check-input")
        if radios:
            break
        time.sleep(0.3)

    # Kiểm tra bảng danh sách câu hỏi (Palette)
    palette_info = driver.execute_script(JS_GET_PALETTE)
    total_q = palette_info.get("total", 0) if palette_info else 0
    answered_init = palette_info.get("answeredCount", 0) if palette_info else 0

    if total_q > 0:
        print(Fore.YELLOW + f"[*] Phát hiện bảng câu hỏi: Tổng cộng {total_q} câu (Đã lưu: {answered_init}/{total_q})\n")
    else:
        init_cnt = get_answered_count(driver)
        if init_cnt:
            print(Fore.YELLOW + f"[*] Tiến độ ban đầu: {init_cnt}\n")

    processed_count = 0

    for step in range(1, max_questions + 1):
        # Đóng alert bất ngờ nếu có
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except Exception:
            pass

        # 1. Kiểm tra trạng thái Palette để lấy danh sách các câu hỏi chưa trả lời
        palette_status = driver.execute_script(JS_GET_PALETTE)
        has_palette = palette_status and palette_status.get("hasPalette")
        unanswered_list = palette_status.get("unanswered", []) if has_palette else []
        current_answered = palette_status.get("answeredCount", 0) if has_palette else 0
        total_in_palette = palette_status.get("total", 0) if has_palette else total_q

        # Nếu có Palette và KHÔNG CÒN CÂU NÀO CHƯA LÀM -> ĐÃ HOÀN THÀNH 100%!
        if has_palette and len(unanswered_list) == 0:
            print(Fore.GREEN + Style.BRIGHT + f"\n[🎉] TẤT CẢ {total_in_palette}/{total_in_palette} CÂU HỎI ĐÃ ĐƯỢC LƯU XANH THÀNH CÔNG!")
            break

        # Xác định câu hỏi cần làm:
        target_q_num = None
        if has_palette and unanswered_list:
            target_q_num = unanswered_list[0]
            # Nhảy tới câu hỏi chưa làm trong bảng Palette
            driver.execute_script(JS_JUMP_PALETTE, target_q_num)
            # Chờ hệ thống chuyển sang đúng câu hỏi cần làm
            for _ in range(12):
                time.sleep(0.15)
                act_num = driver.execute_script("""
                    let act = document.querySelector('button.sc-eIcdZJ.lmztXy, button[class*="lmztXy"]');
                    return act ? parseInt(act.innerText.trim()) : null;
                """)
                if act_num == target_q_num:
                    break
            time.sleep(0.3)

        # Lấy tiêu đề câu hỏi trên giao diện
        q_title = f"Câu {target_q_num}" if target_q_num else f"Câu {step}"
        try:
            headers = [h.text.strip() for h in driver.find_elements(By.XPATH, "//*[contains(text(), 'Câu ')]") if h.is_displayed() and len(h.text.strip()) < 35]
            if headers:
                q_title = headers[0]
        except Exception:
            pass

        # Kiểm tra nếu câu hỏi đã được lưu từ trước (phòng ngừa)
        if target_q_num and driver.execute_script(JS_CHECK_PALETTE_GREEN, target_q_num):
            continue

        # Kiểm tra nếu câu hỏi đã có sẵn đáp án được chọn và đã được lưu
        has_already_selected = driver.execute_script("""
            let checked = document.querySelectorAll("input[type='radio']:checked").length > 0;
            let btns = Array.from(document.querySelectorAll('button.btn-primary, button.btn')).filter(b => b.offsetWidth > 0 && b.offsetHeight > 0);
            let hasSave = btns.some(b => (b.innerText || '').toLowerCase().includes('lưu'));
            return checked && !hasSave;
        """)
        if has_already_selected:
            continue

        # Chọn ngẫu nhiên nếu được cấu hình
        eff_target_idx = target_idx
        if opt_str == 'RANDOM':
            import random
            eff_target_idx = random.randint(0, 3)

        # 2. Chọn đáp án (Option B) và kích hoạt React
        sel_info = None
        opt_text = ""
        for retry in range(5):
            sel_info = driver.execute_script(JS_SELECT_RADIO, eff_target_idx)
            if sel_info and sel_info.get("success"):
                opt_text = sel_info.get("text", "")
                break
            time.sleep(0.3)

        # 3. Đợi nút 'Lưu câu trả lời và tiếp tục' xuất hiện và BẤM NÚT
        saved_successfully = False
        btn_clicked_name = ""
        for save_attempt in range(6):
            time.sleep(0.3)
            save_res = driver.execute_script(JS_CLICK_SAVE_BUTTON)
            if save_res and save_res.get("clicked"):
                saved_successfully = True
                btn_clicked_name = save_res.get("text", "Lưu câu trả lời và tiếp tục")
                break
            elif save_res and save_res.get("isFinish"):
                # Gặp nút nộp bài
                break
            # Nếu chưa thấy nút Lưu câu trả lời, thử click lại đáp án
            if save_attempt in [2, 4]:
                driver.execute_script(JS_SELECT_RADIO, eff_target_idx)

        processed_count += 1
        chosen_letter = chr(65 + eff_target_idx)
        detail = f" - '{opt_text[:40]}...'" if opt_text else ""

        # 4. Xác nhận câu hỏi đã chuyển sang màu xanh (Đã lưu vào hệ thống)
        is_verified_green = False
        if target_q_num and saved_successfully:
            for _ in range(12):
                time.sleep(0.3)
                if driver.execute_script(JS_CHECK_PALETTE_GREEN, target_q_num):
                    is_verified_green = True
                    break

        # In thông báo tiến độ trực quan
        if is_verified_green:
            print(Fore.GREEN + Style.BRIGHT + f"[✓] {q_title}: " +
                  Fore.CYAN + f"Chọn Option {chosen_letter} " +
                  Fore.GREEN + f"➔ Đã Lưu thành công (Màu xanh)" +
                  Fore.WHITE + detail +
                  Fore.YELLOW + f" [{current_answered + 1}/{total_in_palette}]")
        elif saved_successfully:
            print(Fore.GREEN + f"[✓] {q_title}: " +
                  Fore.CYAN + f"Chọn Option {chosen_letter} " +
                  Fore.GREEN + f"➔ Đã bấm '{btn_clicked_name}'" +
                  Fore.WHITE + detail)
        else:
            print(Fore.YELLOW + f"[!] {q_title}: " +
                  Fore.WHITE + f"Đang kiểm tra lại...")

        # Nghỉ theo cấu hình
        time.sleep(max(0.3, delay))

    # NỘP BÀI KHI HOÀN TẤT BÀI THI
    if auto_submit:
        print(Fore.CYAN + "\n[*] Đang tiến hành nộp bài tự động...")
        time.sleep(1.0)
        submitted = False
        for attempt in range(15):
            sub_res = driver.execute_script(JS_SUBMIT_TEST)
            if sub_res and sub_res.get("clicked"):
                btn_name = sub_res.get("text", "")
                btn_type = sub_res.get("type", "")
                print(Fore.GREEN + f"[✓] Đã bấm: '{btn_name}'!")

                # Nếu vừa bấm 'Nộp bài', chờ cửa sổ 'Xem lại câu trả lời' hiện lên có nút 'Kết Thúc Bài Làm'
                if btn_type == 'submit':
                    print(Fore.CYAN + "[*] Chờ cửa sổ 'Xem lại câu trả lời' và nút 'Kết Thúc Bài Làm' xuất hiện...")
                    time.sleep(2.0)
                    continue

                # Nếu đã bấm 'Kết Thúc Bài Làm'
                if btn_type == 'finish':
                    submitted = True
                    print(Fore.GREEN + Style.BRIGHT + f"[🎉] ĐÃ BẤM 'KẾT THÚC BÀI LÀM' THÀNH CÔNG CHO BÀI TEST [{test_index}/{total_tests}]!")
                    time.sleep(1.5)
                    # Xác nhận hộp thoại phụ nếu có
                    driver.execute_script(JS_CONFIRM_MODAL)
                    break
            else:
                # Thử tìm các nút xác nhận trên dialog/popup
                conf_res = driver.execute_script(JS_CONFIRM_MODAL)
                if conf_res and conf_res.get("clicked"):
                    print(Fore.GREEN + f"[✓] Đã bấm xác nhận: '{conf_res.get('text')}'!")
                    submitted = True
                    break
            time.sleep(1.0)

        # Chờ hệ thống hoàn tất lưu điểm và đóng modal
        print(Fore.CYAN + "[*] Chờ 4s để hệ thống hoàn tất ghi nhận điểm và chuyển tiếp sang bài tiếp theo...")
        time.sleep(4)

    final_count = get_answered_count(driver)
    print(Fore.GREEN + f"\n[✓] Hoàn tất bài test [{test_index}/{total_tests}]! Đã xử lý {processed_count} câu.")
    if final_count:
        print(Fore.GREEN + f"    Tiến độ hoàn thành: {final_count}\n")
    time.sleep(3)


def run_automation_suite(url_list: list, username: str, password: str,
                         option_choice: str = "B", delay: float = 1.5,
                         auto_submit: bool = True, headless: bool = False,
                         max_questions: int = 250, repeat: int = 1, loop: bool = False):
    banner()

    print(Fore.GREEN + f"[+] Tài khoản đăng nhập: {username}")
    print(Fore.GREEN + f"[+] Tổng số bài test cần làm: {len(url_list)}")
    for i, u in enumerate(url_list, 1):
        print(Fore.WHITE + f"    {i}. {u}")
    print(Fore.GREEN + f"[+] Đáp án tự động chọn: Option {option_choice.upper()}")
    print(Fore.GREEN + f"[+] Khoảng nghỉ giữa các câu: {delay}s")
    print(Fore.GREEN + f"[+] Tự động nộp bài: {'BẬT (xong sẽ tự chuyển bài tiếp)' if auto_submit else 'TẮT'}")
    if loop:
        print(Fore.MAGENTA + Style.BRIGHT + "[+] Chế độ cày giờ: LẶP VÔ TẬN (--loop) - Tool sẽ liên tục làm lại các bài để tích luỹ giờ!")
    elif repeat > 1:
        print(Fore.MAGENTA + Style.BRIGHT + f"[+] Chế độ cày giờ: LẶP LẠI {repeat} VÒNG (--repeat {repeat}) để tích luỹ thêm giờ!")
    print()

    driver = create_driver(headless=headless)

    try:
        # Đăng nhập 1 lần duy nhất
        perform_login(driver, username, password)

        total_tests = len(url_list)
        current_round = 1

        while True:
            round_info = f"VÒNG {current_round}" + (f"/{repeat}" if not loop else " (VÔ TẬN)")
            print(Fore.MAGENTA + "\n" + "=" * 70)
            print(Fore.MAGENTA + Style.BRIGHT + f"   🔄 BẮT ĐẦU {round_info} - CÀY GIỜ TÍCH LUỸ CHO TOÀN BỘ DANH SÁCH")
            print(Fore.MAGENTA + "=" * 70 + "\n")

            # Duyệt qua từng bài test trong danh sách
            for idx, test_url in enumerate(url_list, 1):
                run_single_test(
                    driver=driver,
                    target_url=test_url,
                    test_index=idx,
                    total_tests=total_tests,
                    option_choice=option_choice,
                    delay=delay,
                    auto_submit=auto_submit,
                    max_questions=max_questions
                )

            print(Fore.GREEN + "\n" + "=" * 70)
            print(Fore.GREEN + Style.BRIGHT + f"   ✅ HOÀN TẤT {round_info} ({total_tests} bài kiểm tra)!")
            print(Fore.GREEN + "=" * 70 + "\n")

            if not loop and current_round >= repeat:
                break

            current_round += 1
            print(Fore.CYAN + "[*] Nghỉ 10 giây trước khi bắt đầu vòng làm lại tiếp theo...")
            time.sleep(10)

        print(Fore.GREEN + "\n" + "=" * 70)
        print(Fore.GREEN + Style.BRIGHT + f"   🎉 CHÚC MỪNG! ĐÃ HOÀN TẤT TẤT CẢ {current_round if not loop else repeat} VÒNG CÀY GIỜ!")
        print(Fore.GREEN + "=" * 70 + "\n")

        if not headless:
            print(Fore.YELLOW + "[*] Trình duyệt đang được giữ mở để bạn kiểm tra lại.")
            print(Fore.CYAN + "[*] Nhấn phím Enter tại cửa sổ này khi bạn muốn đóng trình duyệt...")
            input()

    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Đã dừng bởi người dùng (Ctrl+C).")
    except Exception as e:
        print(Fore.RED + f"\n[X] Đã xảy ra lỗi: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except Exception:
            pass
        print(Fore.BLUE + "[*] Đã đóng trình duyệt.")


def parse_args():
    parser = argparse.ArgumentParser(description="Tool Auto Click Nhiều Bài Trắc Nghiệm LMS Uniapp")
    parser.add_argument("--file", type=str, default="urls.txt",
                        help="Đường dẫn file chứa danh sách link bài test (mặc định: urls.txt)")
    parser.add_argument("--url", type=str, default=None,
                        help="Chỉ định 1 link bài kiểm tra cụ thể nếu không muốn đọc từ file")
    parser.add_argument("--username", type=str, default="045203008804",
                        help="Tên đăng nhập")
    parser.add_argument("--password", type=str, default="Root2003@",
                        help="Mật khẩu")
    parser.add_argument("--option", type=str, default="B",
                        help="Đáp án muốn chọn: A, B, C, D hoặc RANDOM (mặc định: B)")
    parser.add_argument("--delay", type=float, default=1.5,
                        help="Thời gian chờ giữa các câu hỏi tính bằng giây (mặc định: 1.5s)")
    parser.add_argument("--max-questions", type=int, default=250,
                        help="Số lượng câu hỏi tối đa cho mỗi bài test (mặc định: 250)")
    parser.add_argument("--repeat", type=int, default=1,
                        help="Số lần lặp lại toàn bộ danh sách bài test để cày tích lũy giờ (mặc định: 1)")
    parser.add_argument("--loop", action="store_true",
                        help="Chế độ lặp vô tận: tự động làm lại liên tục cho đến khi bạn bấm Ctrl+C")
    parser.add_argument("--no-auto-submit", action="store_true",
                        help="Tắt chế độ tự động nộp bài khi hết câu")
    parser.add_argument("--headless", action="store_true",
                        help="Chạy ẩn trình duyệt không mở cửa sổ (headless)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Xác định danh sách URL cần chạy
    if args.url:
        urls = [args.url.strip()]
    else:
        urls = load_urls_from_file(args.file)
        if not urls:
            default_url = "https://lms.uniapp.vn/elearning/student/test/138?m=606&c=85"
            print(Fore.YELLOW + f"[!] File '{args.file}' trống hoặc không tồn tại. Sử dụng link mặc định: {default_url}")
            urls = [default_url]

    run_automation_suite(
        url_list=urls,
        username=args.username,
        password=args.password,
        option_choice=args.option,
        delay=args.delay,
        auto_submit=not args.no_auto_submit,
        headless=args.headless,
        max_questions=args.max_questions,
        repeat=args.repeat,
        loop=args.loop
    )

