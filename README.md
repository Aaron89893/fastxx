# ⚡ Tool Automation Auto-Click Trắc Nghiệm LMS Uniapp (Hỗ trợ Nhiều Bài Test)

Công cụ tự động hóa làm bài trắc nghiệm trên LMS Uniapp (`lms.uniapp.vn`), tự động đăng nhập, đọc danh sách link bài kiểm tra từ file `urls.txt`, chọn đáp án B (hoặc tùy biến) và bấm **"Lưu câu trả lời và tiếp tục"**. Khi hoàn thành một bài test, tool sẽ **tự động nộp bài và chuyển sang link bài kiểm tra tiếp theo** cho đến khi xong toàn bộ.

---

## 📋 1. Quản lý danh sách link bài test: `urls.txt`

Tất cả các link bài kiểm tra cần làm bạn chỉ cần dán vào file [urls.txt](./urls.txt), mỗi link một dòng:

```text
# Danh sách link bài kiểm tra cần làm (mỗi dòng 1 link)
https://lms.uniapp.vn/elearning/student/test/138?m=606&c=85
https://lms.uniapp.vn/elearning/student/test/139?m=607&c=86
https://lms.uniapp.vn/elearning/student/test/140?m=608&c=87
```

- Các dòng bắt đầu bằng dấu `#` hoặc để trống sẽ được bỏ qua.
- Tool sẽ tự động duyệt từ link đầu tiên đến link cuối cùng.

---

## 🚀 2. Cách khởi chạy

### Trong WSL (Linux terminal):
```bash
python.exe auto_test.py
```
Hoặc:
```bash
bash run.sh
```

### Trong Windows (CMD / PowerShell):
- Click đúp vào file [run.bat](./run.bat)
- Hoặc chạy lệnh:
  ```powershell
  python auto_test.py
  ```

---

## ⚙️ 3. Các tùy chọn nâng cao

```bash
# Chỉ định file danh sách link khác
python.exe auto_test.py --file my_tests.txt

# Chỉ làm 1 link duy nhất (bỏ qua file urls.txt)
python.exe auto_test.py --url "https://lms.uniapp.vn/elearning/student/test/..."

# Đổi đáp án cần chọn (A, B, C, D hoặc RANDOM)
python.exe auto_test.py --option B

# Thay đổi tốc độ giữa các câu (mặc định 1.5s)
python.exe auto_test.py --delay 2.0

# Chạy ẩn không mở cửa sổ Chrome
python.exe auto_test.py --headless
```
# fastxx
