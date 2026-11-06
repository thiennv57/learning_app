# Hướng Dẫn Quản Lý Bộ Câu Hỏi

## 📋 Tổng quan

Tính năng Quản Lý Bộ Câu Hỏi cho phép giáo viên:
- ✅ Tạo các bộ câu hỏi cho các đợt thi
- ✅ Upload file CSV với bất kỳ số lượng câu hỏi nào
- ✅ Quản lý, xem và xóa các bộ câu hỏi

## 🗂️ Cấu trúc File CSV

Mỗi file CSV phải có các cột sau (số lượng câu hỏi tùy ý, tối thiểu 1 câu):

| Cột | Mô tả | Ví dụ |
|-----|-------|-------|
| `question` | Nội dung câu hỏi | "1+1 bằng bao nhiêu?" |
| `option_a` | Lựa chọn A | "1" |
| `option_b` | Lựa chọn B | "2" |
| `option_c` | Lựa chọn C | "3" |
| `option_d` | Lựa chọn D | "4" |
| `answer` | Đáp án đúng (a/b/c/d) | "b" |

## 📝 Ví dụ File CSV

```
question,option_a,option_b,option_c,option_d,answer
1+1 bằng bao nhiêu?,1,2,3,4,b
2+2 bằng bao nhiêu?,3,4,5,6,b
3+3 bằng bao nhiêu?,5,6,7,8,b
...
(có thể có bất kỳ số lượng câu nào)
```

## 💡 Hướng dẫn Sử Dụng

### 1. Chuẩn bị File

Tạo file CSV với:
- Dòng 1: Header (tên cột)
- Dòng 2+: Các câu hỏi (tối thiểu 1 câu, không giới hạn tối đa)

### 2. Truy cập Trang Quản Lý

1. Vào trang chủ
2. Click vào "Quản Lý Bộ Câu Hỏi" hoặc truy cập `/question-sets`

### 3. Upload Bộ Câu Hỏi

1. Click tab "📤 Upload Bộ Mới"
2. Nhập tên bộ câu hỏi
3. Chọn môn học
4. Chọn file CSV
5. Click "✅ Upload & Tạo Bộ"

### 4. Xem & Quản Lý

- **Xem chi tiết**: Click "👁️ Xem" trên thẻ bộ câu hỏi
- **Xóa bộ**: Click "🗑️ Xóa" (cần xác nhận)

## ⚠️ Xác Thực Dữ Liệu

Hệ thống kiểm tra:
- ✅ File phải là CSV hợp lệ
- ✅ Phải có ít nhất 1 câu hỏi
- ✅ Tất cả cột bắt buộc phải có
- ✅ Không được để trống câu hỏi hoặc lựa chọn
- ✅ Đáp án phải là a, b, c hoặc d

## 🔗 API Endpoints

### Lấy Danh Sách Bộ Câu Hỏi
```
GET /api/question-sets?subject=toan
```

### Lấy Chi Tiết Bộ
```
GET /api/question-sets/<set_id>
```

## 📂 Cấu Trúc Thư Mục

```
data/
├── question_sets.json       # Lưu trữ các bộ câu hỏi
└── sample_questions.csv     # File mẫu
```

## 💾 Định Dạng JSON (Nội Bộ)

Các bộ câu hỏi được lưu dưới dạng JSON:

```json
{
  "toan_20240406_120530": {
    "id": "toan_20240406_120530",
    "name": "Toán Kì 1 - Tháng 1",
    "subject": "toan",
    "total_questions": 15,
    "questions": [
      {
        "question": "1+1 bằng bao nhiêu?",
        "options": {
          "a": "1",
          "b": "2",
          "c": "3",
          "d": "4"
        },
        "answer": "b"
      },
      ...
    ],
    "created_at": "2024-04-06T12:05:30.123456",
    "updated_at": "2024-04-06T12:05:30.123456"
  }
}
```

## 🎯 Những Lưu Ý Khi Tạo Câu Hỏi

1. **Câu hỏi rõ ràng**: Dễ hiểu, phù hợp với cấp độ học sinh
2. **Lựa chọn hợp lý**: Gần giống nhau để tránh quá dễ
3. **Đáp án chính xác**: Chỉ có đúng 1 đáp án đúng
4. **Định dạng đồng nhất**: Không mix tiếng Việt/Anh, dấu câu nhất quán
5. **Trộn lẫn vị trí đáp án**: Không để tất cả đáp án đúng cùng ở vị trí (a, b, c, d nên đều được dùng)

## 🚀 Ví Dụ Thực Tế

### Toán học
```csv
question,option_a,option_b,option_c,option_d,answer
5-2 bằng bao nhiêu?,2,3,4,5,b
10-7 bằng bao nhiêu?,2,3,4,5,b
8-4 bằng bao nhiêu?,3,4,5,6,b
```

### Tiếng Việt
```csv
question,option_a,option_b,option_c,option_d,answer
Từ nào là danh từ?,chạy,cái bàn,đẹp,nhanh,b
Chữ A trong "an" phát âm như thế nào?,a ngắn,a dài,a huyền,a sắc,a
```
