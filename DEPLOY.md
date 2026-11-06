# Triển khai lên PythonAnywhere

Kho mã: https://github.com/thiennv57/learning_app

Quy trình: sửa code ở máy → đẩy lên GitHub → vào PythonAnywhere kéo về và
nạp lại ứng dụng.

---

## Lần đầu: dựng ứng dụng trên PythonAnywhere

Mở **Bash console** trên PythonAnywhere và chạy:

```bash
git clone https://github.com/thiennv57/learning_app.git
cd learning_app
mkvirtualenv --python=/usr/bin/python3.10 learning_app
pip install -r requirements.txt
```

Sang tab **Web** → *Add a new web app* → chọn **Manual configuration** →
**Python 3.10**, rồi điền ba mục sau:

| Mục | Giá trị |
|---|---|
| Source code | `/home/thiennv57/learning_app` |
| Working directory | `/home/thiennv57/learning_app` |
| Virtualenv | `/home/thiennv57/.virtualenvs/learning_app` |

Bấm vào đường dẫn **WSGI configuration file**, xoá hết nội dung cũ và thay bằng:

```python
import sys

path = '/home/thiennv57/learning_app'
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
```

Cuối cùng, ở mục **Static files** thêm một dòng để ảnh, CSS, JS được phục vụ
trực tiếp cho nhanh:

| URL | Directory |
|---|---|
| `/static/` | `/home/thiennv57/learning_app/static` |

Bấm **Reload** màu xanh. Xong.

---

## Những lần sau: đồng bộ code mới

**Ở máy của bạn** — đẩy thay đổi lên GitHub:

```bash
cd C:\Users\ngo.van.thien\Documents\learning_app
git add -A
git commit -m "mô tả ngắn thay đổi"
git push
```

**Trên PythonAnywhere** — mở Bash console:

```bash
cd ~/learning_app
git pull
```

Rồi sang tab **Web** bấm nút **Reload** màu xanh. Chỉ khi nào `requirements.txt`
có thêm thư viện mới thì mới cần chạy thêm:

```bash
workon learning_app && pip install -r requirements.txt
```

### Rút gọn bằng script có sẵn

File `deploy.ps1` làm trọn ba bước commit → push → SSH vào PythonAnywhere để
pull và nạp lại:

```powershell
.\deploy.ps1 -PAUser thiennv57 -RemoteAppDir '~/learning_app' -VirtualEnv learning_app
```

Lưu ý: **SSH chỉ có ở tài khoản PythonAnywhere trả phí**. Tài khoản miễn phí
thì dùng cách thủ công ở trên.

---

## Hai điều cần biết khi vận hành

**Bấm Reload là mọi phòng đang chơi sẽ mất.** Danh sách phòng được giữ trong bộ
nhớ của tiến trình (`_rooms` trong `attack_defense_game.py` và
`team_battle_game.py`), không lưu xuống đĩa. Đừng đồng bộ code giữa giờ dạy —
học sinh sẽ bị văng khỏi phòng. Phòng cũng tự xoá sau 4 giờ.

**Reload cũng làm mất phiên đăng nhập của phần luyện tập.** `app.py` sinh
`secret_key` mới mỗi lần khởi động, nên dữ liệu trong `session` (dùng ở phần
bài tập theo môn) bị xoá. Nếu thấy phiền, đặt một khoá cố định qua biến môi
trường thay cho `secrets.token_hex(32)`.
