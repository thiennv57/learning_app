# -*- coding: utf-8 -*-
"""
Nội dung bài tập theo chương trình Kết nối tri thức lớp 1
Bộ Giáo dục và Đào tạo Việt Nam
MỞ RỘNG: Nhiều dạng bài, nhiều câu hỏi, nhiều biến thể
"""
import random

# ============================================================
# TOÁN LỚP 1 - KẾT NỐI TRI THỨC
# ============================================================

TOAN_TOPICS = {
    "ki1": {
        "name": "Toán Kì 1",
        "icon": "📐",
        "topics": {
            "so_den_10": {
                "name": "Các số đến 10",
                "icon": "🔢",
                "description": "Nhận biết, đọc, viết, đếm, so sánh các số từ 0 đến 10"
            },
            "cong_trong_10": {
                "name": "Phép cộng trong phạm vi 10",
                "icon": "➕",
                "description": "Phép cộng, tìm số bị thiếu, bài toán có lời văn"
            },
            "tru_trong_10": {
                "name": "Phép trừ trong phạm vi 10",
                "icon": "➖",
                "description": "Phép trừ, tìm số bị thiếu, bài toán có lời văn"
            },
            "so_sanh": {
                "name": "So sánh các số",
                "icon": "⚖️",
                "description": "So sánh, sắp xếp, tìm số lớn nhất, bé nhất"
            },
            "hinh_hoc_1": {
                "name": "Hình học cơ bản",
                "icon": "🔷",
                "description": "Nhận biết hình, đếm hình, đếm cạnh"
            },
        }
    },
    "ki2": {
        "name": "Toán Kì 2",
        "icon": "📏",
        "topics": {
            "so_den_20": {
                "name": "Các số đến 20",
                "icon": "🔢",
                "description": "Đọc, viết, phân tích các số từ 11 đến 20"
            },
            "cong_tru_trong_20": {
                "name": "Cộng trừ trong phạm vi 20",
                "icon": "🧮",
                "description": "Phép cộng, trừ, bài toán lời văn trong phạm vi 20"
            },
            "so_den_100": {
                "name": "Các số đến 100",
                "icon": "💯",
                "description": "Đọc, viết, phân tích, sắp xếp các số đến 100"
            },
            "cong_trong_100": {
                "name": "Cộng phạm vi 100 (không nhớ)",
                "icon": "➕",
                "description": "Phép cộng không nhớ, bài toán lời văn"
            },
            "tru_trong_100": {
                "name": "Trừ phạm vi 100 (không nhớ)",
                "icon": "➖",
                "description": "Phép trừ không nhớ, bài toán lời văn"
            },
            "xem_gio": {
                "name": "Xem giờ đúng",
                "icon": "🕐",
                "description": "Đọc giờ đúng, giờ rưỡi trên đồng hồ"
            },
            "do_do_dai": {
                "name": "Đo độ dài",
                "icon": "📏",
                "description": "Đo, so sánh, cộng trừ độ dài (cm)"
            },
        }
    }
}

SO_DOC = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín", "mười"]

EMOJI_OBJECTS = ["🍎", "⭐", "🌸", "🐟", "🦋", "🐝", "🍊", "🌺", "🐢", "🎈",
                 "🍒", "🥚", "🐤", "🌻", "🎁", "🍰", "🧁", "🍬", "🎀", "🪄"]

WORD_PROBLEM_TEMPLATES_ADD = [
    ("Lan có {a} quả táo 🍎, mẹ cho thêm {b} quả. Hỏi Lan có tất cả bao nhiêu quả táo?", "quả"),
    ("Trong vườn có {a} con bướm 🦋, bay thêm {b} con nữa. Hỏi có tất cả bao nhiêu con bướm?", "con"),
    ("Bạn An có {a} cây bút ✏️, bạn Bình cho thêm {b} cây. Hỏi An có tất cả bao nhiêu cây bút?", "cây"),
    ("Trên bàn có {a} quyển sách 📕, mẹ để thêm {b} quyển nữa. Hỏi trên bàn có bao nhiêu quyển sách?", "quyển"),
    ("Đàn gà có {a} con 🐔, mua thêm {b} con nữa. Hỏi đàn gà có bao nhiêu con?", "con"),
    ("Lớp 1A có {a} bạn nam 👦, {b} bạn nữ 👧. Hỏi lớp có tất cả bao nhiêu bạn?", "bạn"),
    ("Na hái được {a} bông hoa 🌸, Lan hái được {b} bông. Hỏi cả hai hái được bao nhiêu bông hoa?", "bông"),
    ("Xe buýt có {a} người 🚌, lên thêm {b} người nữa. Hỏi trên xe có bao nhiêu người?", "người"),
]

WORD_PROBLEM_TEMPLATES_SUB = [
    ("Lan có {a} quả cam 🍊, ăn mất {b} quả. Hỏi Lan còn lại bao nhiêu quả cam?", "quả"),
    ("Đàn vịt có {a} con 🦆, bán đi {b} con. Hỏi đàn vịt còn bao nhiêu con?", "con"),
    ("An có {a} viên bi 🔵, cho bạn {b} viên. Hỏi An còn bao nhiêu viên bi?", "viên"),
    ("Trên cây có {a} con chim 🐦, bay đi {b} con. Hỏi trên cây còn bao nhiêu con chim?", "con"),
    ("Mẹ mua {a} quả trứng 🥚, dùng hết {b} quả. Hỏi còn bao nhiêu quả trứng?", "quả"),
    ("Hộp có {a} cái kẹo 🍬, em ăn {b} cái. Hỏi trong hộp còn bao nhiêu cái kẹo?", "cái"),
    ("Bể có {a} con cá 🐟, vớt ra {b} con. Hỏi trong bể còn bao nhiêu con cá?", "con"),
    ("Bạn có {a} bông hoa 🌻, tặng bạn {b} bông. Hỏi còn lại bao nhiêu bông hoa?", "bông"),
]


def _make_choices(correct, pool, n=3):
    """Tạo danh sách lựa chọn có chứa đáp án đúng"""
    wrong = [x for x in pool if x != correct]
    if len(wrong) < n:
        wrong = wrong * (n // len(wrong) + 1)
    choices = [correct] + random.sample(wrong, n)
    random.shuffle(choices)
    return choices


def generate_toan_questions(topic_id, num_questions=10, difficulty=3):
    """Tạo câu hỏi Toán theo chủ đề - MỞ RỘNG"""
    questions = []

    # Hàm cắt qtypes theo độ khó
    def scale_qtypes(all_qtypes, diff):
        n = max(2, len(all_qtypes) * diff // 5)
        return all_qtypes[:n]

    if topic_id == "so_den_10":
        qtypes = ["doc_so", "viet_so", "dem", "lien_truoc", "lien_sau", "lon_nhat", "be_nhat", "dem_hinh", "fill_dem", "fill_lien"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            if qtype == "doc_so":
                num = random.randint(0, 10)
                questions.append({
                    "question": f"Số {num} đọc là gì?",
                    "type": "choice",
                    "choices": _make_choices(SO_DOC[num], SO_DOC),
                    "answer": SO_DOC[num],
                    "image": None
                })
            elif qtype == "viet_so":
                num = random.randint(0, 10)
                questions.append({
                    "question": f'Số "{SO_DOC[num]}" viết là số mấy?',
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(num, list(range(0, 11))))],
                    "answer": str(num),
                    "image": None
                })
            elif qtype == "dem":
                emoji = random.choice(EMOJI_OBJECTS)
                count = random.randint(1, 10)
                display = '<span style="font-size:2em;letter-spacing:8px;">' + ''.join([emoji]*count) + '</span>'
                questions.append({
                    "question": f"Đếm xem có bao nhiêu {emoji}?<br>{display}",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(count, list(range(1, 11))))],
                    "answer": str(count),
                    "image": None
                })
            elif qtype == "lien_truoc":
                num = random.randint(1, 10)
                ans = num - 1
                questions.append({
                    "question": f"Số liền trước của {num} là số nào?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(ans, list(range(0, 11))))],
                    "answer": str(ans),
                    "image": None
                })
            elif qtype == "lien_sau":
                num = random.randint(0, 9)
                ans = num + 1
                questions.append({
                    "question": f"Số liền sau của {num} là số nào?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(ans, list(range(0, 11))))],
                    "answer": str(ans),
                    "image": None
                })
            elif qtype == "lon_nhat":
                nums = random.sample(range(0, 11), 4)
                ans = max(nums)
                display = ", ".join(str(n) for n in nums)
                questions.append({
                    "question": f"Trong các số {display}, số nào lớn nhất?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(nums)],
                    "answer": str(ans),
                    "image": None
                })
            elif qtype == "be_nhat":
                nums = random.sample(range(0, 11), 4)
                ans = min(nums)
                display = ", ".join(str(n) for n in nums)
                questions.append({
                    "question": f"Trong các số {display}, số nào bé nhất?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(nums)],
                    "answer": str(ans),
                    "image": None
                })
            elif qtype == "fill_dem":
                emoji = random.choice(EMOJI_OBJECTS)
                count = random.randint(1, 10)
                display = '<span style="font-size:2em;letter-spacing:8px;">' + ''.join([emoji]*count) + '</span>'
                questions.append({
                    "question": f"Đếm và điền số: Có bao nhiêu {emoji}?<br>{display}",
                    "type": "fill",
                    "hint": "Điền một số",
                    "answer": str(count),
                    "image": None
                })
            elif qtype == "fill_lien":
                num = random.randint(0, 9)
                direction = random.choice(["truoc", "sau"])
                if direction == "truoc" and num > 0:
                    questions.append({
                        "question": f"Điền số liền trước của {num}:",
                        "type": "fill",
                        "hint": "Điền một số",
                        "answer": str(num - 1),
                        "image": None
                    })
                else:
                    questions.append({
                        "question": f"Điền số liền sau của {num}:",
                        "type": "fill",
                        "hint": "Điền một số",
                        "answer": str(num + 1),
                        "image": None
                    })
            else:  # dem_hinh
                emoji = random.choice(EMOJI_OBJECTS)
                other_emoji = random.choice([e for e in EMOJI_OBJECTS if e != emoji])
                count_target = random.randint(2, 6)
                count_other = random.randint(1, 4)
                items = [emoji]*count_target + [other_emoji]*count_other
                random.shuffle(items)
                display = '<span style="font-size:2em;letter-spacing:4px;">' + ' '.join(items) + '</span>'
                questions.append({
                    "question": f"Có bao nhiêu {emoji} trong hình dưới?<br>{display}",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(count_target, list(range(1, 10))))],
                    "answer": str(count_target),
                    "image": None
                })

    elif topic_id == "cong_trong_10":
        qtypes = ["tinh", "tim_so", "loi_van", "dien_dau", "tinh_nhanh", "fill_tinh", "fill_tim_so"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            if qtype == "tinh":
                a = random.randint(0, 10)
                b = random.randint(0, 10 - a)
                correct = a + b
                questions.append({
                    "question": f"{a} + {b} = ?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(correct, list(range(0, 11))))],
                    "answer": str(correct),
                    "image": None
                })
            elif qtype == "tim_so":
                a = random.randint(0, 10)
                b = random.randint(0, 10 - a)
                total = a + b
                hide = random.choice(["a", "b"])
                if hide == "a":
                    questions.append({
                        "question": f"? + {b} = {total}. Số cần tìm là?",
                        "type": "choice",
                        "choices": [str(c) for c in sorted(_make_choices(a, list(range(0, 11))))],
                        "answer": str(a),
                        "image": None
                    })
                else:
                    questions.append({
                        "question": f"{a} + ? = {total}. Số cần tìm là?",
                        "type": "choice",
                        "choices": [str(c) for c in sorted(_make_choices(b, list(range(0, 11))))],
                        "answer": str(b),
                        "image": None
                    })
            elif qtype == "loi_van":
                a = random.randint(1, 7)
                b = random.randint(1, 10 - a)
                correct = a + b
                template, unit = random.choice(WORD_PROBLEM_TEMPLATES_ADD)
                questions.append({
                    "question": template.format(a=a, b=b),
                    "type": "choice",
                    "choices": [str(c) + " " + unit for c in sorted(_make_choices(correct, list(range(1, 11))))],
                    "answer": str(correct) + " " + unit,
                    "image": None
                })
            elif qtype == "dien_dau":
                a = random.randint(0, 10)
                b = random.randint(0, 10)
                if random.choice([True, False]) and a + b <= 10:
                    questions.append({
                        "question": f"{a} ◻ {b} = {a + b}. Dấu cần điền là?",
                        "type": "choice",
                        "choices": ["+", "-"],
                        "answer": "+",
                        "image": None
                    })
                elif a >= b:
                    questions.append({
                        "question": f"{a} ◻ {b} = {a - b}. Dấu cần điền là?",
                        "type": "choice",
                        "choices": ["+", "-"],
                        "answer": "-",
                        "image": None
                    })
                else:
                    questions.append({
                        "question": f"{a} + {b} = ?",
                        "type": "choice",
                        "choices": [str(c) for c in sorted(_make_choices(a + b, list(range(0, 11))))],
                        "answer": str(a + b),
                        "image": None
                    })
            elif qtype == "fill_tinh":
                a = random.randint(0, 10)
                b = random.randint(0, 10 - a)
                correct = a + b
                questions.append({
                    "question": f"Điền kết quả: {a} + {b} = ?",
                    "type": "fill",
                    "hint": "Điền một số",
                    "answer": str(correct),
                    "image": None
                })
            elif qtype == "fill_tim_so":
                a = random.randint(0, 10)
                b = random.randint(0, 10 - a)
                total = a + b
                hide = random.choice(["a", "b"])
                if hide == "a":
                    questions.append({
                        "question": f"Điền số thích hợp: ☐ + {b} = {total}",
                        "type": "fill",
                        "hint": "Điền một số",
                        "answer": str(a),
                        "image": None
                    })
                else:
                    questions.append({
                        "question": f"Điền số thích hợp: {a} + ☐ = {total}",
                        "type": "fill",
                        "hint": "Điền một số",
                        "answer": str(b),
                        "image": None
                    })
            else:  # tinh_nhanh
                a = random.randint(1, 5)
                b = random.randint(1, 5)
                c = random.randint(0, 10 - a - b)
                correct = a + b + c
                questions.append({
                    "question": f"{a} + {b} + {c} = ?",
                    "type": "choice",
                    "choices": [str(x) for x in sorted(_make_choices(correct, list(range(0, 11))))],
                    "answer": str(correct),
                    "image": None
                })

    elif topic_id == "tru_trong_10":
        qtypes = ["tinh", "tim_so", "loi_van", "dien_dau", "tinh_nhanh", "fill_tinh", "fill_tim_so"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            if qtype == "tinh":
                a = random.randint(1, 10)
                b = random.randint(0, a)
                correct = a - b
                questions.append({
                    "question": f"{a} - {b} = ?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(correct, list(range(0, 11))))],
                    "answer": str(correct),
                    "image": None
                })
            elif qtype == "tim_so":
                a = random.randint(1, 10)
                b = random.randint(0, a)
                result = a - b
                hide = random.choice(["a", "b"])
                if hide == "a":
                    questions.append({
                        "question": f"? - {b} = {result}. Số cần tìm là?",
                        "type": "choice",
                        "choices": [str(c) for c in sorted(_make_choices(a, list(range(0, 11))))],
                        "answer": str(a),
                        "image": None
                    })
                else:
                    questions.append({
                        "question": f"{a} - ? = {result}. Số cần tìm là?",
                        "type": "choice",
                        "choices": [str(c) for c in sorted(_make_choices(b, list(range(0, 11))))],
                        "answer": str(b),
                        "image": None
                    })
            elif qtype == "loi_van":
                a = random.randint(3, 10)
                b = random.randint(1, a - 1)
                correct = a - b
                template, unit = random.choice(WORD_PROBLEM_TEMPLATES_SUB)
                questions.append({
                    "question": template.format(a=a, b=b),
                    "type": "choice",
                    "choices": [str(c) + " " + unit for c in sorted(_make_choices(correct, list(range(0, 11))))],
                    "answer": str(correct) + " " + unit,
                    "image": None
                })
            elif qtype == "dien_dau":
                a = random.randint(2, 10)
                b = random.randint(1, a)
                questions.append({
                    "question": f"{a} ◻ {b} = {a - b}. Dấu cần điền là?",
                    "type": "choice",
                    "choices": ["+", "-"],
                    "answer": "-",
                    "image": None
                })
            elif qtype == "fill_tinh":
                a = random.randint(1, 10)
                b = random.randint(0, a)
                correct = a - b
                questions.append({
                    "question": f"Điền kết quả: {a} - {b} = ?",
                    "type": "fill",
                    "hint": "Điền một số",
                    "answer": str(correct),
                    "image": None
                })
            elif qtype == "fill_tim_so":
                a = random.randint(1, 10)
                b = random.randint(0, a)
                result = a - b
                hide = random.choice(["a", "b"])
                if hide == "a":
                    questions.append({
                        "question": f"Điền số thích hợp: ☐ - {b} = {result}",
                        "type": "fill",
                        "hint": "Điền một số",
                        "answer": str(a),
                        "image": None
                    })
                else:
                    questions.append({
                        "question": f"Điền số thích hợp: {a} - ☐ = {result}",
                        "type": "fill",
                        "hint": "Điền một số",
                        "answer": str(b),
                        "image": None
                    })
            else:  # tinh_nhanh
                a = random.randint(5, 10)
                b = random.randint(1, a // 2)
                c = random.randint(0, a - b)
                correct = a - b - c
                questions.append({
                    "question": f"{a} - {b} - {c} = ?",
                    "type": "choice",
                    "choices": [str(x) for x in sorted(_make_choices(correct, list(range(0, 11))))],
                    "answer": str(correct),
                    "image": None
                })

    elif topic_id == "so_sanh":
        qtypes = ["dien_dau", "sap_xep_tang", "sap_xep_giam", "lon_nhat", "be_nhat", "ss_bieu_thuc"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            if qtype == "dien_dau":
                a = random.randint(0, 10)
                b = random.randint(0, 10)
                if a > b: correct = ">"
                elif a < b: correct = "<"
                else: correct = "="
                questions.append({
                    "question": f"Điền dấu thích hợp: {a} ◻ {b}",
                    "type": "choice",
                    "choices": [">", "<", "="],
                    "answer": correct,
                    "image": None
                })
            elif qtype == "sap_xep_tang":
                nums = random.sample(range(0, 11), 4)
                sorted_str = ", ".join(str(n) for n in sorted(nums))
                display = ", ".join(str(n) for n in nums)
                choices_list = []
                choices_list.append(sorted_str)
                for _ in range(3):
                    s = list(nums)
                    random.shuffle(s)
                    cs = ", ".join(str(n) for n in s)
                    if cs != sorted_str and cs not in choices_list:
                        choices_list.append(cs)
                while len(choices_list) < 4:
                    s = list(nums)
                    random.shuffle(s)
                    cs = ", ".join(str(n) for n in s)
                    if cs not in choices_list:
                        choices_list.append(cs)
                random.shuffle(choices_list)
                questions.append({
                    "question": f"Sắp xếp các số {display} theo thứ tự từ BÉ đến LỚN:",
                    "type": "choice",
                    "choices": choices_list,
                    "answer": sorted_str,
                    "image": None
                })
            elif qtype == "sap_xep_giam":
                nums = random.sample(range(0, 11), 4)
                sorted_str = ", ".join(str(n) for n in sorted(nums, reverse=True))
                display = ", ".join(str(n) for n in nums)
                choices_list = [sorted_str]
                for _ in range(10):
                    s = list(nums)
                    random.shuffle(s)
                    cs = ", ".join(str(n) for n in s)
                    if cs != sorted_str and cs not in choices_list:
                        choices_list.append(cs)
                    if len(choices_list) >= 4:
                        break
                while len(choices_list) < 4:
                    choices_list.append(", ".join(str(n) for n in random.sample(range(0, 11), 4)))
                random.shuffle(choices_list)
                questions.append({
                    "question": f"Sắp xếp các số {display} theo thứ tự từ LỚN đến BÉ:",
                    "type": "choice",
                    "choices": choices_list[:4],
                    "answer": sorted_str,
                    "image": None
                })
            elif qtype == "lon_nhat":
                nums = random.sample(range(0, 11), 4)
                ans = max(nums)
                display = ", ".join(str(n) for n in nums)
                questions.append({
                    "question": f"Trong các số {display}, số nào lớn nhất?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(nums)],
                    "answer": str(ans),
                    "image": None
                })
            elif qtype == "be_nhat":
                nums = random.sample(range(0, 11), 4)
                ans = min(nums)
                display = ", ".join(str(n) for n in nums)
                questions.append({
                    "question": f"Trong các số {display}, số nào bé nhất?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(nums)],
                    "answer": str(ans),
                    "image": None
                })
            else:  # ss_bieu_thuc
                a1 = random.randint(1, 8)
                b1 = random.randint(0, 10 - a1)
                left = a1 + b1
                right = random.randint(0, 10)
                if left > right: correct = ">"
                elif left < right: correct = "<"
                else: correct = "="
                questions.append({
                    "question": f"Điền dấu: {a1} + {b1} ◻ {right}",
                    "type": "choice",
                    "choices": [">", "<", "="],
                    "answer": correct,
                    "image": None
                })

    elif topic_id == "hinh_hoc_1":
        shapes = [
            {"name": "Hình vuông", "emoji": "🟥", "desc": "có 4 cạnh bằng nhau, 4 góc vuông", "canh": 4, "goc": 4},
            {"name": "Hình tròn", "emoji": "🔵", "desc": "tròn, không có cạnh, không có góc", "canh": 0, "goc": 0},
            {"name": "Hình tam giác", "emoji": "🔺", "desc": "có 3 cạnh và 3 góc", "canh": 3, "goc": 3},
            {"name": "Hình chữ nhật", "emoji": "🟩", "desc": "có 2 cạnh dài bằng nhau, 2 cạnh ngắn bằng nhau", "canh": 4, "goc": 4},
        ]
        qtypes = ["nhan_biet", "dem_canh", "dem_goc", "dem_hinh", "mo_ta"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            shape = random.choice(shapes)
            if qtype == "nhan_biet":
                questions.append({
                    "question": f"Hình nào {shape['desc']}?",
                    "type": "choice",
                    "choices": [s["name"] for s in shapes],
                    "answer": shape["name"],
                    "image": None
                })
            elif qtype == "dem_canh":
                questions.append({
                    "question": f"{shape['emoji']} {shape['name']} có bao nhiêu cạnh?",
                    "type": "choice",
                    "choices": ["0", "3", "4", "5"],
                    "answer": str(shape["canh"]),
                    "image": None
                })
            elif qtype == "dem_goc":
                questions.append({
                    "question": f"{shape['emoji']} {shape['name']} có bao nhiêu góc?",
                    "type": "choice",
                    "choices": ["0", "3", "4", "5"],
                    "answer": str(shape["goc"]),
                    "image": None
                })
            elif qtype == "dem_hinh":
                count = random.randint(2, 5)
                display = '<span style="font-size:2.5em;letter-spacing:10px;">' + shape["emoji"] * count + '</span>'
                questions.append({
                    "question": f"Có bao nhiêu {shape['name']}?<br>{display}",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(count, [2, 3, 4, 5, 6]))],
                    "answer": str(count),
                    "image": None
                })
            else:  # mo_ta
                questions.append({
                    "question": f'{shape["emoji"]} Hình này tên là gì?',
                    "type": "choice",
                    "choices": [s["name"] for s in shapes],
                    "answer": shape["name"],
                    "image": None
                })

    elif topic_id == "so_den_20":
        words_11_20 = {
            11: "mười một", 12: "mười hai", 13: "mười ba", 14: "mười bốn",
            15: "mười lăm", 16: "mười sáu", 17: "mười bảy", 18: "mười tám",
            19: "mười chín", 20: "hai mươi"
        }
        qtypes = ["doc", "viet", "phan_tich", "lien_truoc", "lien_sau", "sap_xep"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            num = random.randint(11, 20)
            word = words_11_20[num]
            if qtype == "doc":
                other_words = [words_11_20[k] for k in words_11_20 if k != num]
                choices = [word] + random.sample(other_words, 3)
                random.shuffle(choices)
                questions.append({
                    "question": f"Số {num} đọc là gì?",
                    "type": "choice",
                    "choices": choices,
                    "answer": word,
                    "image": None
                })
            elif qtype == "viet":
                other_nums = [k for k in range(11, 21) if k != num]
                choices = sorted([num] + random.sample(other_nums, 3))
                questions.append({
                    "question": f'Số "{word}" viết là số mấy?',
                    "type": "choice",
                    "choices": [str(c) for c in choices],
                    "answer": str(num),
                    "image": None
                })
            elif qtype == "phan_tich":
                chuc = num // 10
                dv = num % 10
                questions.append({
                    "question": f"Số {num} gồm mấy chục và mấy đơn vị?",
                    "type": "choice",
                    "choices": [f"{chuc} chục {dv} đơn vị", f"{dv} chục {chuc} đơn vị",
                               f"{chuc+1} chục {dv} đơn vị", f"{chuc} chục {dv+1} đơn vị"],
                    "answer": f"{chuc} chục {dv} đơn vị",
                    "image": None
                })
            elif qtype == "lien_truoc":
                ans = num - 1
                questions.append({
                    "question": f"Số liền trước của {num} là?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(ans, list(range(10, 21))))],
                    "answer": str(ans),
                    "image": None
                })
            elif qtype == "lien_sau":
                if num < 20:
                    ans = num + 1
                    questions.append({
                        "question": f"Số liền sau của {num} là?",
                        "type": "choice",
                        "choices": [str(c) for c in sorted(_make_choices(ans, list(range(10, 22))))],
                        "answer": str(ans),
                        "image": None
                    })
                else:
                    questions.append({
                        "question": f"Số {num} đọc là gì?",
                        "type": "choice",
                        "choices": _make_choices(word, list(words_11_20.values())),
                        "answer": word,
                        "image": None
                    })
            else:  # sap_xep
                nums = random.sample(range(11, 21), 4)
                sorted_str = ", ".join(str(n) for n in sorted(nums))
                display = ", ".join(str(n) for n in nums)
                choices_list = [sorted_str]
                for _ in range(10):
                    s = list(nums); random.shuffle(s)
                    cs = ", ".join(str(n) for n in s)
                    if cs not in choices_list: choices_list.append(cs)
                    if len(choices_list) >= 4: break
                while len(choices_list) < 4:
                    choices_list.append(", ".join(str(n) for n in random.sample(range(11, 21), 4)))
                random.shuffle(choices_list)
                questions.append({
                    "question": f"Sắp xếp từ bé đến lớn: {display}",
                    "type": "choice",
                    "choices": choices_list[:4],
                    "answer": sorted_str,
                    "image": None
                })

    elif topic_id == "cong_tru_trong_20":
        qtypes = ["cong", "tru", "tim_so_cong", "tim_so_tru", "loi_van", "hon_kem", "fill_cong", "fill_tru"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            if qtype == "cong":
                a = random.randint(1, 19)
                b = random.randint(1, 20 - a)
                correct = a + b
                wrong = [x for x in range(0, 21) if x != correct]
                questions.append({
                    "question": f"{a} + {b} = ?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(correct, list(range(0, 21))))],
                    "answer": str(correct),
                    "image": None
                })
            elif qtype == "tru":
                a = random.randint(2, 20)
                b = random.randint(1, a)
                correct = a - b
                questions.append({
                    "question": f"{a} - {b} = ?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(correct, list(range(0, 21))))],
                    "answer": str(correct),
                    "image": None
                })
            elif qtype == "tim_so_cong":
                a = random.randint(1, 18)
                b = random.randint(1, 20 - a)
                total = a + b
                hide = random.choice(["a", "b"])
                if hide == "a":
                    questions.append({
                        "question": f"? + {b} = {total}",
                        "type": "choice",
                        "choices": [str(c) for c in sorted(_make_choices(a, list(range(0, 21))))],
                        "answer": str(a),
                        "image": None
                    })
                else:
                    questions.append({
                        "question": f"{a} + ? = {total}",
                        "type": "choice",
                        "choices": [str(c) for c in sorted(_make_choices(b, list(range(0, 21))))],
                        "answer": str(b),
                        "image": None
                    })
            elif qtype == "tim_so_tru":
                a = random.randint(2, 20)
                b = random.randint(1, a)
                result = a - b
                questions.append({
                    "question": f"{a} - ? = {result}",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(b, list(range(0, 21))))],
                    "answer": str(b),
                    "image": None
                })
            elif qtype == "loi_van":
                op = random.choice(["add", "sub"])
                if op == "add":
                    a = random.randint(1, 15)
                    b = random.randint(1, 20 - a)
                    correct = a + b
                    template, unit = random.choice(WORD_PROBLEM_TEMPLATES_ADD)
                else:
                    a = random.randint(5, 20)
                    b = random.randint(1, a - 1)
                    correct = a - b
                    template, unit = random.choice(WORD_PROBLEM_TEMPLATES_SUB)
                questions.append({
                    "question": template.format(a=a, b=b),
                    "type": "choice",
                    "choices": [str(c) + " " + unit for c in sorted(_make_choices(correct, list(range(1, 21))))],
                    "answer": str(correct) + " " + unit,
                    "image": None
                })
            elif qtype == "hon_kem":
                a = random.randint(3, 18)
                b = random.randint(1, 20 - a)
                diff = abs(a - b)
                if a > b:
                    questions.append({
                        "question": f"Số {a} hơn số {b} là bao nhiêu?",
                        "type": "choice",
                        "choices": [str(c) for c in sorted(_make_choices(diff, list(range(0, 20))))],
                        "answer": str(diff),
                        "image": None
                    })
                else:
                    questions.append({
                        "question": f"Số {a} kém số {b} là bao nhiêu?",
                        "type": "choice",
                        "choices": [str(c) for c in sorted(_make_choices(diff, list(range(0, 20))))],
                        "answer": str(diff),
                        "image": None
                    })
            elif qtype == "fill_cong":
                a = random.randint(1, 19)
                b = random.randint(1, 20 - a)
                correct = a + b
                questions.append({
                    "question": f"Điền kết quả: {a} + {b} = ?",
                    "type": "fill",
                    "hint": "Điền một số",
                    "answer": str(correct),
                    "image": None
                })
            elif qtype == "fill_tru":
                a = random.randint(2, 20)
                b = random.randint(1, a)
                correct = a - b
                questions.append({
                    "question": f"Điền kết quả: {a} - {b} = ?",
                    "type": "fill",
                    "hint": "Điền một số",
                    "answer": str(correct),
                    "image": None
                })

    elif topic_id == "so_den_100":
        chuc_words = ["", "mười", "hai mươi", "ba mươi", "bốn mươi",
                     "năm mươi", "sáu mươi", "bảy mươi", "tám mươi", "chín mươi"]
        def doc_so_100(num):
            if num < 11: return SO_DOC[num]
            c = num // 10
            d = num % 10
            if d == 0: return chuc_words[c]
            dv_basic = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
            if d == 5 and c > 1: return chuc_words[c] + " lăm"
            if d == 1 and c > 1: return chuc_words[c] + " mốt"
            return chuc_words[c] + " " + dv_basic[d]

        qtypes = ["doc", "viet", "phan_tich", "lien_truoc", "lien_sau", "sap_xep", "chan_le"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            num = random.randint(21, 99)
            word = doc_so_100(num)
            if qtype == "doc":
                others = [doc_so_100(random.randint(21, 99)) for _ in range(10)]
                others = [o for o in others if o != word][:3]
                while len(others) < 3:
                    others.append(doc_so_100(random.randint(21, 99)))
                choices = [word] + others
                random.shuffle(choices)
                questions.append({
                    "question": f"Số {num} đọc là gì?",
                    "type": "choice",
                    "choices": choices,
                    "answer": word,
                    "image": None
                })
            elif qtype == "viet":
                other_nums = [x for x in range(21, 100) if x != num]
                choices = sorted([num] + random.sample(other_nums, 3))
                questions.append({
                    "question": f'Số "{word}" viết là số mấy?',
                    "type": "choice",
                    "choices": [str(c) for c in choices],
                    "answer": str(num),
                    "image": None
                })
            elif qtype == "phan_tich":
                chuc = num // 10
                dv = num % 10
                questions.append({
                    "question": f"Số {num} có bao nhiêu chục và bao nhiêu đơn vị?",
                    "type": "choice",
                    "choices": [f"{chuc} chục {dv} đơn vị", f"{dv} chục {chuc} đơn vị",
                               f"{chuc+1} chục {dv} đơn vị", f"{chuc} chục {dv+1 if dv<9 else 0} đơn vị"],
                    "answer": f"{chuc} chục {dv} đơn vị",
                    "image": None
                })
            elif qtype == "lien_truoc":
                ans = num - 1
                questions.append({
                    "question": f"Số liền trước của {num} là?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted([ans, ans-1, ans+1, ans+2])],
                    "answer": str(ans),
                    "image": None
                })
            elif qtype == "lien_sau":
                ans = num + 1
                questions.append({
                    "question": f"Số liền sau của {num} là?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted([ans, ans-1, ans+1, ans-2])],
                    "answer": str(ans),
                    "image": None
                })
            elif qtype == "sap_xep":
                nums = random.sample(range(21, 100), 4)
                sorted_str = ", ".join(str(n) for n in sorted(nums))
                display = ", ".join(str(n) for n in nums)
                choices_list = [sorted_str]
                for _ in range(10):
                    s = list(nums); random.shuffle(s)
                    cs = ", ".join(str(n) for n in s)
                    if cs not in choices_list: choices_list.append(cs)
                    if len(choices_list) >= 4: break
                while len(choices_list) < 4:
                    choices_list.append(", ".join(str(n) for n in random.sample(range(21, 100), 4)))
                random.shuffle(choices_list)
                questions.append({
                    "question": f"Sắp xếp từ bé đến lớn: {display}",
                    "type": "choice",
                    "choices": choices_list[:4],
                    "answer": sorted_str,
                    "image": None
                })
            else:  # chan_le
                num2 = random.choice(list(range(2, 100, 2)) if random.choice([True, False]) else list(range(1, 100, 2)))
                is_even = (num2 % 2 == 0)
                questions.append({
                    "question": f"Số {num2} là số chẵn hay số lẻ?",
                    "type": "choice",
                    "choices": ["Số chẵn", "Số lẻ"],
                    "answer": "Số chẵn" if is_even else "Số lẻ",
                    "image": None
                })

    elif topic_id == "cong_trong_100":
        qtypes = ["tinh", "tim_so", "loi_van", "dat_tinh", "so_sanh_bt", "fill_tinh"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            if qtype == "tinh" or qtype == "dat_tinh":
                while True:
                    a = random.randint(10, 89)
                    b = random.randint(1, 99 - a)
                    if (a % 10) + (b % 10) < 10:
                        break
                correct = a + b
                wrong = [x for x in range(max(0, correct-10), min(100, correct+11)) if x != correct]
                if len(wrong) < 3: wrong = [x for x in range(0, 100) if x != correct]
                questions.append({
                    "question": f"{a} + {b} = ?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(correct, wrong))],
                    "answer": str(correct),
                    "image": None
                })
            elif qtype == "tim_so":
                while True:
                    a = random.randint(10, 80)
                    b = random.randint(1, 99 - a)
                    if (a % 10) + (b % 10) < 10:
                        break
                total = a + b
                hide = random.choice(["a", "b"])
                if hide == "a":
                    questions.append({
                        "question": f"? + {b} = {total}",
                        "type": "choice",
                        "choices": [str(c) for c in sorted(_make_choices(a, list(range(10, 90))))],
                        "answer": str(a),
                        "image": None
                    })
                else:
                    questions.append({
                        "question": f"{a} + ? = {total}",
                        "type": "choice",
                        "choices": [str(c) for c in sorted(_make_choices(b, list(range(1, 50))))],
                        "answer": str(b),
                        "image": None
                    })
            elif qtype == "loi_van":
                while True:
                    a = random.randint(10, 70)
                    b = random.randint(10, 99 - a)
                    if (a % 10) + (b % 10) < 10:
                        break
                correct = a + b
                template, unit = random.choice(WORD_PROBLEM_TEMPLATES_ADD)
                questions.append({
                    "question": template.format(a=a, b=b),
                    "type": "choice",
                    "choices": [str(c) + " " + unit for c in sorted(_make_choices(correct, list(range(20, 100))))],
                    "answer": str(correct) + " " + unit,
                    "image": None
                })
            elif qtype == "so_sanh_bt":
                while True:
                    a1 = random.randint(10, 70)
                    b1 = random.randint(1, 99 - a1)
                    if (a1 % 10) + (b1 % 10) < 10: break
                left = a1 + b1
                right = random.randint(20, 99)
                if left > right: correct = ">"
                elif left < right: correct = "<"
                else: correct = "="
                questions.append({
                    "question": f"{a1} + {b1} ◻ {right}",
                    "type": "choice",
                    "choices": [">", "<", "="],
                    "answer": correct,
                    "image": None
                })
            elif qtype == "fill_tinh":
                while True:
                    a = random.randint(10, 89)
                    b = random.randint(1, 99 - a)
                    if (a % 10) + (b % 10) < 10:
                        break
                correct = a + b
                questions.append({
                    "question": f"Điền kết quả: {a} + {b} = ?",
                    "type": "fill",
                    "hint": "Điền một số",
                    "answer": str(correct),
                    "image": None
                })

    elif topic_id == "tru_trong_100":
        qtypes = ["tinh", "tim_so", "loi_van", "so_sanh_bt", "fill_tinh"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            if qtype == "tinh":
                while True:
                    a = random.randint(11, 99)
                    b = random.randint(1, a)
                    if (a % 10) >= (b % 10): break
                correct = a - b
                wrong = [x for x in range(max(0, correct-10), min(100, correct+11)) if x != correct]
                if len(wrong) < 3: wrong = [x for x in range(0, 100) if x != correct]
                questions.append({
                    "question": f"{a} - {b} = ?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(correct, wrong))],
                    "answer": str(correct),
                    "image": None
                })
            elif qtype == "tim_so":
                while True:
                    a = random.randint(20, 99)
                    b = random.randint(1, a)
                    if (a % 10) >= (b % 10): break
                result = a - b
                questions.append({
                    "question": f"{a} - ? = {result}",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(b, list(range(1, 50))))],
                    "answer": str(b),
                    "image": None
                })
            elif qtype == "loi_van":
                while True:
                    a = random.randint(20, 99)
                    b = random.randint(5, a - 1)
                    if (a % 10) >= (b % 10): break
                correct = a - b
                template, unit = random.choice(WORD_PROBLEM_TEMPLATES_SUB)
                questions.append({
                    "question": template.format(a=a, b=b),
                    "type": "choice",
                    "choices": [str(c) + " " + unit for c in sorted(_make_choices(correct, list(range(0, 90))))],
                    "answer": str(correct) + " " + unit,
                    "image": None
                })
            elif qtype == "so_sanh_bt":
                while True:
                    a1 = random.randint(20, 99)
                    b1 = random.randint(1, a1)
                    if (a1 % 10) >= (b1 % 10): break
                left = a1 - b1
                right = random.randint(0, 90)
                if left > right: correct = ">"
                elif left < right: correct = "<"
                else: correct = "="
                questions.append({
                    "question": f"{a1} - {b1} ◻ {right}",
                    "type": "choice",
                    "choices": [">", "<", "="],
                    "answer": correct,
                    "image": None
                })
            elif qtype == "fill_tinh":
                while True:
                    a = random.randint(11, 99)
                    b = random.randint(1, a)
                    if (a % 10) >= (b % 10): break
                correct = a - b
                questions.append({
                    "question": f"Điền kết quả: {a} - {b} = ?",
                    "type": "fill",
                    "hint": "Điền một số",
                    "answer": str(correct),
                    "image": None
                })

    elif topic_id == "xem_gio":
        import math
        def svg_clock(hour, minute=0, size=150):
            """Generate an SVG clock face with numbers 1-12 and hour/minute hands."""
            cx, cy, r = size//2, size//2, size//2 - 10
            svg = f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">'
            # Clock face with shadow
            svg += f'<circle cx="{cx}" cy="{cy+2}" r="{r+2}" fill="rgba(0,0,0,0.08)"/>'
            svg += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fffff5" stroke="#222" stroke-width="4"/>'
            svg += f'<circle cx="{cx}" cy="{cy}" r="{r-2}" fill="none" stroke="#ccc" stroke-width="1"/>'
            # Tick marks
            for i in range(60):
                a = math.radians(i * 6 - 90)
                if i % 5 == 0:
                    x1, y1 = cx + (r-14)*math.cos(a), cy + (r-14)*math.sin(a)
                    x2, y2 = cx + (r-4)*math.cos(a), cy + (r-4)*math.sin(a)
                    svg += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#222" stroke-width="2.5"/>'
                else:
                    x1, y1 = cx + (r-7)*math.cos(a), cy + (r-7)*math.sin(a)
                    x2, y2 = cx + (r-4)*math.cos(a), cy + (r-4)*math.sin(a)
                    svg += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#bbb" stroke-width="1"/>'
            # Numbers 1-12 (large, bold, colored)
            num_fs = max(size // 7, 14)
            for n in range(1, 13):
                a = math.radians(n * 30 - 90)
                nr = r - 30 if size >= 200 else r - 20
                nx, ny = cx + nr*math.cos(a), cy + nr*math.sin(a)
                svg += f'<text x="{nx:.1f}" y="{ny:.1f}" text-anchor="middle" dominant-baseline="central" font-size="{num_fs}" font-family="Arial Black, Arial, sans-serif" font-weight="900" fill="#e74c3c" stroke="#fff" stroke-width="0.5">{n}</text>'
            # Hour hand (thick, dark)
            h_angle = math.radians((hour % 12 + minute / 60) * 30 - 90)
            hx, hy = cx + (r*0.45)*math.cos(h_angle), cy + (r*0.45)*math.sin(h_angle)
            svg += f'<line x1="{cx}" y1="{cy}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="#222" stroke-width="5" stroke-linecap="round"/>'
            # Minute hand (thinner, red)
            m_angle = math.radians(minute * 6 - 90)
            mx, my = cx + (r*0.68)*math.cos(m_angle), cy + (r*0.68)*math.sin(m_angle)
            svg += f'<line x1="{cx}" y1="{cy}" x2="{mx:.1f}" y2="{my:.1f}" stroke="#e74c3c" stroke-width="3" stroke-linecap="round"/>'
            # Center dot
            svg += f'<circle cx="{cx}" cy="{cy}" r="5" fill="#e74c3c"/>'
            svg += f'<circle cx="{cx}" cy="{cy}" r="2" fill="#fff"/>'
            svg += '</svg>'
            return svg

        def clock_html(hour, minute=0):
            return svg_clock(hour, minute, 260)

        def clock_small(hour, minute=0):
            return svg_clock(hour, minute, 90)
        qtypes = ["gio_dung", "gio_ruoi", "hoat_dong", "chon_dong_ho"]
        qtypes = scale_qtypes(qtypes, difficulty)
        hoat_dong_map = [
            (7, "đi học 🏫"), (11, "ăn trưa 🍚"), (6, "thức dậy ⏰"),
            (5, "ăn chiều 🍜"), (8, "ngủ 😴"), (9, "đọc sách 📖"),
            (3, "tan học 🎒"), (10, "uống sữa 🥛"), (4, "chơi ⚽"),
        ]
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            if qtype == "gio_dung":
                hour = random.randint(1, 12)
                other_hours = [h for h in range(1, 13) if h != hour]
                questions.append({
                    "question": f'{clock_html(hour, 0)}<br>Đồng hồ chỉ mấy giờ?',
                    "type": "choice",
                    "choices": [f"{c} giờ" for c in sorted([hour] + random.sample(other_hours, 3))],
                    "answer": f"{hour} giờ",
                    "image": None
                })
            elif qtype == "gio_ruoi":
                hour = random.randint(1, 12)
                other_hours = [h for h in range(1, 13) if h != hour]
                gio_choices = [f"{hour} giờ 30 phút"] + [f"{h} giờ 30 phút" for h in random.sample(other_hours, 2)] + [f"{hour} giờ"]
                random.shuffle(gio_choices)
                questions.append({
                    "question": f'{clock_html(hour, 30)}<br>Đồng hồ chỉ mấy giờ?',
                    "type": "choice",
                    "choices": gio_choices,
                    "answer": f"{hour} giờ 30 phút",
                    "image": None
                })
            elif qtype == "hoat_dong":
                hd = random.choice(hoat_dong_map)
                hour = hd[0]
                questions.append({
                    "question": f'Bạn Lan {hd[1]} lúc:<br>{clock_html(hour, 0)}<br>Hỏi bạn Lan {hd[1]} lúc mấy giờ?',
                    "type": "choice",
                    "choices": [f"{c} giờ" for c in sorted([hour] + random.sample([h for h in range(1, 13) if h != hour], 3))],
                    "answer": f"{hour} giờ",
                    "image": None
                })
            else:  # chon_dong_ho
                hour = random.randint(1, 12)
                others = random.sample([h for h in range(1, 13) if h != hour], 3)
                all_hours = [hour] + others
                random.shuffle(all_hours)
                choices = [f'{clock_small(h, 0)} {h} giờ' for h in all_hours]
                questions.append({
                    "question": f"Chọn đồng hồ chỉ {hour} giờ:",
                    "type": "choice",
                    "choices": choices,
                    "answer": f'{clock_small(hour, 0)} {hour} giờ',
                    "image": None
                })

    elif topic_id == "do_do_dai":
        objects_cm = [
            ("Bút chì ✏️", 15), ("Quyển sách 📕", 25), ("Cục tẩy", 4), ("Thước kẻ 📏", 20),
            ("Ngón tay ☝️", 5), ("Bàn tay 🤚", 18), ("Chiếc lá 🍃", 8), ("Điện thoại 📱", 14),
            ("Hộp bút", 22), ("Chai nước 🧴", 20), ("Con kiến 🐜", 1), ("Cây viết máy 🖊️", 12),
        ]
        qtypes = ["so_sanh", "uoc_luong", "cong_dai", "tru_dai", "sap_xep"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            if qtype == "so_sanh":
                a_cm = random.randint(1, 30)
                b_cm = random.randint(1, 30)
                while a_cm == b_cm: b_cm = random.randint(1, 30)
                answer = "Đoạn A" if a_cm > b_cm else "Đoạn B"
                questions.append({
                    "question": f"📏 Đoạn A dài {a_cm} cm. Đoạn B dài {b_cm} cm. Đoạn nào dài hơn?",
                    "type": "choice",
                    "choices": ["Đoạn A", "Đoạn B"],
                    "answer": answer,
                    "image": None
                })
            elif qtype == "uoc_luong":
                obj = random.choice(objects_cm)
                correct = obj[1]
                wrong = [x for x in [1, 3, 4, 5, 8, 10, 12, 14, 15, 18, 20, 22, 25, 30] if x != correct]
                choices = sorted([correct] + random.sample(wrong, 3))
                questions.append({
                    "question": f"{obj[0]} dài khoảng bao nhiêu cm?",
                    "type": "choice",
                    "choices": [f"{c} cm" for c in choices],
                    "answer": f"{correct} cm",
                    "image": None
                })
            elif qtype == "cong_dai":
                a = random.randint(1, 30)
                b = random.randint(1, 30)
                correct = a + b
                wrong = [x for x in range(max(2, correct-5), correct+6) if x != correct]
                questions.append({
                    "question": f"Đoạn A dài {a} cm, đoạn B dài {b} cm. Tổng độ dài = ?",
                    "type": "choice",
                    "choices": [f"{c} cm" for c in sorted(_make_choices(correct, wrong))],
                    "answer": f"{correct} cm",
                    "image": None
                })
            elif qtype == "tru_dai":
                a = random.randint(10, 40)
                b = random.randint(1, a - 1)
                correct = a - b
                wrong = [x for x in range(max(0, correct-5), correct+6) if x != correct]
                questions.append({
                    "question": f"Đoạn thẳng dài {a} cm, cắt bỏ {b} cm. Đoạn còn lại dài bao nhiêu?",
                    "type": "choice",
                    "choices": [f"{c} cm" for c in sorted(_make_choices(correct, wrong))],
                    "answer": f"{correct} cm",
                    "image": None
                })
            else:  # sap_xep
                lens = random.sample(range(1, 35), 4)
                sorted_str = ", ".join(f"{n} cm" for n in sorted(lens))
                display = ", ".join(f"{n} cm" for n in lens)
                choices_list = [sorted_str]
                for _ in range(10):
                    s = list(lens); random.shuffle(s)
                    cs = ", ".join(f"{n} cm" for n in s)
                    if cs not in choices_list: choices_list.append(cs)
                    if len(choices_list) >= 4: break
                while len(choices_list) < 4:
                    choices_list.append(", ".join(f"{n} cm" for n in random.sample(range(1, 35), 4)))
                random.shuffle(choices_list)
                questions.append({
                    "question": f"Sắp xếp từ ngắn đến dài: {display}",
                    "type": "choice",
                    "choices": choices_list[:4],
                    "answer": sorted_str,
                    "image": None
                })

    return questions


# ============================================================
# TIẾNG VIỆT LỚP 1 - KẾT NỐI TRI THỨC
# ============================================================

TIENG_VIET_TOPICS = {
    "ki1": {
        "name": "Tiếng Việt Kì 1",
        "icon": "📖",
        "topics": {
            "chu_cai": {
                "name": "Bảng chữ cái",
                "icon": "🔤",
                "description": "Nhận biết, viết hoa, thứ tự 29 chữ cái"
            },
            "nguyen_am": {
                "name": "Nguyên âm",
                "icon": "🅰️",
                "description": "Nhận biết, phân biệt 12 nguyên âm tiếng Việt"
            },
            "phu_am": {
                "name": "Phụ âm đầu",
                "icon": "🅱️",
                "description": "Nhận biết, ghép phụ âm đầu với vần"
            },
            "ghep_van_1": {
                "name": "Ghép vần đơn giản",
                "icon": "🧩",
                "description": "Ghép vần: an, at, am, ap, en, et..."
            },
            "tap_doc_tu": {
                "name": "Tập đọc từ đơn giản",
                "icon": "📕",
                "description": "Đọc từ, hiểu nghĩa, nối từ với hình"
            },
        }
    },
    "ki2": {
        "name": "Tiếng Việt Kì 2",
        "icon": "📗",
        "topics": {
            "van_phuc_tap": {
                "name": "Vần phức tạp",
                "icon": "🧩",
                "description": "Vần: ong, ông, ung, ưng, ang, anh, inh..."
            },
            "tap_doc_cau": {
                "name": "Tập đọc câu",
                "icon": "📖",
                "description": "Đọc hiểu câu ngắn, trả lời câu hỏi"
            },
            "chinh_ta": {
                "name": "Chính tả",
                "icon": "✏️",
                "description": "Phân biệt s/x, ch/tr, r/d/gi, l/n..."
            },
            "dau_cau": {
                "name": "Dấu câu",
                "icon": "❓",
                "description": "Dấu chấm, dấu phẩy, dấu hỏi, dấu chấm than"
            },
            "sap_xep_cau": {
                "name": "Sắp xếp câu",
                "icon": "📝",
                "description": "Sắp xếp các từ thành câu có nghĩa"
            },
        }
    }
}

CHU_CAI_VN = [
    "a", "ă", "â", "b", "c", "d", "đ", "e", "ê", "g",
    "h", "i", "k", "l", "m", "n", "o", "ô", "ơ", "p",
    "q", "r", "s", "t", "u", "ư", "v", "x", "y"
]

NGUYEN_AM = ["a", "ă", "â", "e", "ê", "i", "o", "ô", "ơ", "u", "ư", "y"]
PHU_AM = ["b", "c", "d", "đ", "g", "h", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "x"]

VAN_DON_GIAN = [
    "an", "at", "am", "ap", "ac", "ang",
    "en", "et", "em", "ep", "ec", "eng",
    "in", "it", "im", "ip",
    "on", "ot", "om", "op", "oc", "ong",
    "un", "ut", "um", "up", "uc", "ung",
    "ôn", "ôt", "ôm", "ôp", "ôc", "ông",
    "ơn", "ơt", "ơm", "ơp",
    "ăn", "ăt", "ăm", "ăp", "ăc", "ăng",
    "ân", "ât", "âm", "âp", "âc", "âng",
    "ưn", "ưt", "ưc", "ưng",
]

VAN_PHUC_TAP = [
    "ong", "ông", "ung", "ưng", "ang", "anh", "inh", "ênh",
    "ach", "ich", "oai", "oay", "uôi", "ươi", "ươn", "ương",
    "iêu", "yêu", "uôn", "uông", "uyên", "uyết",
    "oanh", "oang", "uâng", "uynh", "iêng", "uông",
    "oat", "oăn", "oăt", "uân", "uât",
]

TU_DON_GIAN = [
    {"tu": "ba", "nghia": "bố/cha 👨", "van": "a"},
    {"tu": "mẹ", "nghia": "mẹ 👩", "van": "e"},
    {"tu": "bé", "nghia": "em bé 👶", "van": "e"},
    {"tu": "cá", "nghia": "con cá 🐟", "van": "a"},
    {"tu": "gà", "nghia": "con gà 🐔", "van": "a"},
    {"tu": "hoa", "nghia": "bông hoa 🌸", "van": "oa"},
    {"tu": "nhà", "nghia": "ngôi nhà 🏠", "van": "a"},
    {"tu": "bàn", "nghia": "cái bàn 🪑", "van": "an"},
    {"tu": "ghế", "nghia": "cái ghế 💺", "van": "ê"},
    {"tu": "sách", "nghia": "quyển sách 📕", "van": "ach"},
    {"tu": "bút", "nghia": "cây bút ✏️", "van": "ut"},
    {"tu": "mèo", "nghia": "con mèo 🐱", "van": "eo"},
    {"tu": "chó", "nghia": "con chó 🐕", "van": "o"},
    {"tu": "voi", "nghia": "con voi 🐘", "van": "oi"},
    {"tu": "trâu", "nghia": "con trâu 🐃", "van": "âu"},
    {"tu": "trời", "nghia": "bầu trời 🌤️", "van": "ơi"},
    {"tu": "mưa", "nghia": "trời mưa 🌧️", "van": "ưa"},
    {"tu": "nắng", "nghia": "trời nắng ☀️", "van": "ăng"},
    {"tu": "lá", "nghia": "chiếc lá 🍃", "van": "a"},
    {"tu": "cây", "nghia": "cái cây 🌳", "van": "ây"},
    {"tu": "xe", "nghia": "chiếc xe 🚗", "van": "e"},
    {"tu": "cơm", "nghia": "bát cơm 🍚", "van": "ơm"},
    {"tu": "nước", "nghia": "nước uống 💧", "van": "ươc"},
    {"tu": "trăng", "nghia": "mặt trăng 🌙", "van": "ăng"},
    {"tu": "sao", "nghia": "ngôi sao ⭐", "van": "ao"},
    {"tu": "biển", "nghia": "biển cả 🌊", "van": "iên"},
    {"tu": "núi", "nghia": "ngọn núi ⛰️", "van": "ui"},
    {"tu": "sông", "nghia": "dòng sông 🏞️", "van": "ông"},
    {"tu": "chim", "nghia": "con chim 🐦", "van": "im"},
    {"tu": "ong", "nghia": "con ong 🐝", "van": "ong"},
    {"tu": "bướm", "nghia": "con bướm 🦋", "van": "ươm"},
    {"tu": "thỏ", "nghia": "con thỏ 🐰", "van": "o"},
    {"tu": "rùa", "nghia": "con rùa 🐢", "van": "ua"},
    {"tu": "bánh", "nghia": "cái bánh 🍰", "van": "anh"},
    {"tu": "sữa", "nghia": "ly sữa 🥛", "van": "ưa"},
]

CHINH_TA_DATA = [
    {"q": "con ___á 🐟", "choices": ["c", "k"], "answer": "c"},
    {"q": "con ___iến 🐜", "choices": ["c", "k"], "answer": "k"},
    {"q": "bầu ___ời 🌤️", "choices": ["tr", "ch"], "answer": "tr"},
    {"q": "___iếc lá 🍃", "choices": ["ch", "tr"], "answer": "ch"},
    {"q": "cây ___e 🎋", "choices": ["tr", "ch"], "answer": "tr"},
    {"q": "quyển ___ách 📕", "choices": ["s", "x"], "answer": "s"},
    {"q": "___e đạp 🚲", "choices": ["x", "s"], "answer": "x"},
    {"q": "con ___ó 🐕", "choices": ["ch", "tr"], "answer": "ch"},
    {"q": "con ___âu 🐃", "choices": ["tr", "ch"], "answer": "tr"},
    {"q": "___à 🍵", "choices": ["tr", "ch"], "answer": "tr"},
    {"q": "___ạo 🌾", "choices": ["g", "gh"], "answer": "g"},
    {"q": "___i chép ✍️", "choices": ["g", "gh"], "answer": "gh"},
    {"q": "___ong lanh ✨", "choices": ["l", "n"], "answer": "l"},
    {"q": "___ói chuyện 💬", "choices": ["l", "n"], "answer": "n"},
    {"q": "cái ___ón 🧢", "choices": ["l", "n"], "answer": "n"},
    {"q": "___úa 🌾", "choices": ["l", "n"], "answer": "l"},
    {"q": "___i đi 🚶", "choices": ["d", "gi"], "answer": "d"},
    {"q": "cái ___ếng 💧", "choices": ["d", "gi"], "answer": "gi"},
    {"q": "___ạo phố 🚶‍♂️", "choices": ["d", "gi"], "answer": "d"},
    {"q": "đôi ___ày 👟", "choices": ["d", "gi"], "answer": "gi"},
    {"q": "con ___a 🦎", "choices": ["r", "d"], "answer": "d"},
    {"q": "cái ___ĩa 🍽️", "choices": ["d", "gi"], "answer": "d"},
    {"q": "___ặt trời ☀️", "choices": ["m", "n"], "answer": "m"},
]

DAU_CAU_DATA = [
    {"cau": "Em đi học", "answer": ".", "loai": "câu kể"},
    {"cau": "Bạn tên gì", "answer": "?", "loai": "câu hỏi"},
    {"cau": "Ôi đẹp quá", "answer": "!", "loai": "câu cảm thán"},
    {"cau": "Mẹ đi chợ", "answer": ".", "loai": "câu kể"},
    {"cau": "Bạn có khỏe không", "answer": "?", "loai": "câu hỏi"},
    {"cau": "Trời ơi", "answer": "!", "loai": "câu cảm thán"},
    {"cau": "Ba đọc báo", "answer": ".", "loai": "câu kể"},
    {"cau": "Hôm nay thứ mấy", "answer": "?", "loai": "câu hỏi"},
    {"cau": "Hoan hô", "answer": "!", "loai": "câu cảm thán"},
    {"cau": "Con mèo nằm trên ghế", "answer": ".", "loai": "câu kể"},
    {"cau": "Em bao nhiêu tuổi", "answer": "?", "loai": "câu hỏi"},
    {"cau": "Tuyệt vời", "answer": "!", "loai": "câu cảm thán"},
    {"cau": "Bé uống sữa", "answer": ".", "loai": "câu kể"},
    {"cau": "Ai đang hát", "answer": "?", "loai": "câu hỏi"},
    {"cau": "Thật tuyệt", "answer": "!", "loai": "câu cảm thán"},
    {"cau": "Hoa nở trong vườn", "answer": ".", "loai": "câu kể"},
    {"cau": "Bạn ở đâu", "answer": "?", "loai": "câu hỏi"},
    {"cau": "Chạy nhanh lên", "answer": "!", "loai": "câu cảm thán"},
]

TAP_DOC_CAU_DATA = [
    {"cau": "Em đi học.", "hoi": "Em đi đâu?", "answer": "đi học"},
    {"cau": "Mẹ nấu cơm.", "hoi": "Mẹ làm gì?", "answer": "nấu cơm"},
    {"cau": "Ba đọc báo.", "hoi": "Ba làm gì?", "answer": "đọc báo"},
    {"cau": "Bé chơi với mèo.", "hoi": "Bé chơi với ai?", "answer": "mèo"},
    {"cau": "Hoa nở trong vườn.", "hoi": "Hoa nở ở đâu?", "answer": "trong vườn"},
    {"cau": "Con chim hót trên cây.", "hoi": "Con chim ở đâu?", "answer": "trên cây"},
    {"cau": "Trời mưa to.", "hoi": "Trời mưa như thế nào?", "answer": "to"},
    {"cau": "Lan ăn cơm với mẹ.", "hoi": "Lan ăn cơm với ai?", "answer": "mẹ"},
    {"cau": "Bạn Nam ngồi bàn đầu.", "hoi": "Bạn Nam ngồi ở đâu?", "answer": "bàn đầu"},
    {"cau": "Mẹ mua bánh cho bé.", "hoi": "Mẹ mua gì?", "answer": "bánh"},
    {"cau": "Con mèo nằm trên ghế.", "hoi": "Con mèo nằm ở đâu?", "answer": "trên ghế"},
    {"cau": "Ông trồng cây trong vườn.", "hoi": "Ông làm gì?", "answer": "trồng cây"},
    {"cau": "Bé đi ngủ lúc 8 giờ.", "hoi": "Bé đi ngủ lúc mấy giờ?", "answer": "8 giờ"},
    {"cau": "Chị mặc áo đỏ.", "hoi": "Chị mặc áo màu gì?", "answer": "đỏ"},
    {"cau": "Em có 5 viên bi.", "hoi": "Em có mấy viên bi?", "answer": "5"},
]

SAP_XEP_CAU_DATA = [
    {"words": ["Em", "đi", "học"], "answer": "Em đi học"},
    {"words": ["Mẹ", "nấu", "cơm"], "answer": "Mẹ nấu cơm"},
    {"words": ["Ba", "đọc", "báo"], "answer": "Ba đọc báo"},
    {"words": ["Bé", "uống", "sữa"], "answer": "Bé uống sữa"},
    {"words": ["Chim", "hót", "trên", "cây"], "answer": "Chim hót trên cây"},
    {"words": ["Hoa", "nở", "trong", "vườn"], "answer": "Hoa nở trong vườn"},
    {"words": ["Con", "mèo", "nằm", "ngủ"], "answer": "Con mèo nằm ngủ"},
    {"words": ["Em", "yêu", "mẹ"], "answer": "Em yêu mẹ"},
    {"words": ["Trời", "mưa", "to"], "answer": "Trời mưa to"},
    {"words": ["Bé", "đi", "chơi"], "answer": "Bé đi chơi"},
    {"words": ["Mẹ", "mua", "sách", "cho", "bé"], "answer": "Mẹ mua sách cho bé"},
    {"words": ["Con", "cá", "bơi", "trong", "hồ"], "answer": "Con cá bơi trong hồ"},
    {"words": ["Ông", "trồng", "cây"], "answer": "Ông trồng cây"},
    {"words": ["Bạn", "An", "chạy", "nhanh"], "answer": "Bạn An chạy nhanh"},
]


def generate_tieng_viet_questions(topic_id, num_questions=10, difficulty=3):
    """Tạo câu hỏi Tiếng Việt - MỞ RỘNG"""
    questions = []

    def scale_qtypes(all_qtypes, diff):
        n = max(2, len(all_qtypes) * diff // 5)
        return all_qtypes[:n]

    if topic_id == "chu_cai":
        qtypes = ["nhan_biet", "thu_tu", "nguyen_phu", "viet_hoa", "diem_chu", "dau_truoc"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            if qtype == "nhan_biet":
                letter = random.choice(CHU_CAI_VN)
                choices = [letter.upper()] + [l.upper() for l in random.sample([x for x in CHU_CAI_VN if x != letter], 3)]
                random.shuffle(choices)
                questions.append({
                    "question": f'Chữ cái "{letter}" viết hoa là gì?',
                    "type": "choice",
                    "choices": choices,
                    "answer": letter.upper(),
                    "image": None
                })
            elif qtype == "thu_tu":
                idx = random.randint(0, len(CHU_CAI_VN) - 2)
                letter = CHU_CAI_VN[idx]
                next_letter = CHU_CAI_VN[idx + 1]
                choices = [next_letter] + random.sample([l for l in CHU_CAI_VN if l != next_letter], 3)
                random.shuffle(choices)
                questions.append({
                    "question": f'Chữ cái nào đứng SAU chữ "{letter}"?',
                    "type": "choice",
                    "choices": choices,
                    "answer": next_letter,
                    "image": None
                })
            elif qtype == "dau_truoc":
                idx = random.randint(1, len(CHU_CAI_VN) - 1)
                letter = CHU_CAI_VN[idx]
                prev_letter = CHU_CAI_VN[idx - 1]
                choices = [prev_letter] + random.sample([l for l in CHU_CAI_VN if l != prev_letter], 3)
                random.shuffle(choices)
                questions.append({
                    "question": f'Chữ cái nào đứng TRƯỚC chữ "{letter}"?',
                    "type": "choice",
                    "choices": choices,
                    "answer": prev_letter,
                    "image": None
                })
            elif qtype == "nguyen_phu":
                letter = random.choice(CHU_CAI_VN)
                is_nguyen = letter in NGUYEN_AM
                questions.append({
                    "question": f'Chữ "{letter}" là nguyên âm hay phụ âm?',
                    "type": "choice",
                    "choices": ["Nguyên âm", "Phụ âm"],
                    "answer": "Nguyên âm" if is_nguyen else "Phụ âm",
                    "image": None
                })
            elif qtype == "viet_hoa":
                letter = random.choice(CHU_CAI_VN)
                choices = [letter] + random.sample([l for l in CHU_CAI_VN if l != letter], 3)
                random.shuffle(choices)
                questions.append({
                    "question": f'Chữ hoa "{letter.upper()}" viết thường là gì?',
                    "type": "choice",
                    "choices": choices,
                    "answer": letter,
                    "image": None
                })
            else:  # diem_chu
                count = random.choice([12, 17, 29])
                label = {12: "nguyên âm", 17: "phụ âm", 29: "chữ cái"}
                questions.append({
                    "question": f"Bảng chữ cái tiếng Việt có bao nhiêu {label[count]}?",
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(count, [10, 12, 17, 20, 24, 26, 29]))],
                    "answer": str(count),
                    "image": None
                })

    elif topic_id == "nguyen_am":
        qtypes = ["chon_nguyen", "dem_nguyen", "dien_nguyen"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            if qtype == "chon_nguyen":
                correct = random.choice(NGUYEN_AM)
                decoy = random.sample(PHU_AM, 3)
                choices = [correct] + decoy
                random.shuffle(choices)
                questions.append({
                    "question": "Chữ nào là NGUYÊN ÂM?",
                    "type": "choice",
                    "choices": choices,
                    "answer": correct,
                    "image": None
                })
            elif qtype == "dem_nguyen":
                word = random.choice(TU_DON_GIAN)
                nguyen_count = sum(1 for ch in word["tu"].lower() if ch in "aăâeêioôơuưy")
                questions.append({
                    "question": f'Từ "{word["tu"]}" có bao nhiêu nguyên âm?',
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(nguyen_count, [0, 1, 2, 3, 4]))],
                    "answer": str(nguyen_count),
                    "image": None
                })
            else:  # dien_nguyen
                word_map = [("b_n", "a", "bàn"), ("m_o", "è", "mèo"), ("ch_m", "i", "chim"),
                           ("h_a", "o", "hoa"), ("b_t", "ú", "bút"), ("c_y", "â", "cây"),
                           ("l_", "á", "lá"), ("m_", "ẹ", "mẹ"), ("c_", "á", "cá")]
                item = random.choice(word_map)
                others = [w[1] for w in word_map if w[1] != item[1]]
                choices = [item[1]] + random.sample(list(set(others)), min(3, len(set(others))))
                while len(choices) < 4:
                    choices.append(random.choice(NGUYEN_AM))
                random.shuffle(choices)
                questions.append({
                    "question": f'Điền nguyên âm: {item[0]}',
                    "type": "choice",
                    "choices": choices[:4],
                    "answer": item[1],
                    "image": None
                })

    elif topic_id == "phu_am":
        qtypes = ["chon_phu", "ghep_tu", "am_dau"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            if qtype == "chon_phu":
                correct = random.choice(PHU_AM)
                decoy = random.sample(NGUYEN_AM, 3)
                choices = [correct] + decoy
                random.shuffle(choices)
                questions.append({
                    "question": "Chữ nào là PHỤ ÂM?",
                    "type": "choice",
                    "choices": choices,
                    "answer": correct,
                    "image": None
                })
            elif qtype == "ghep_tu":
                phu = random.choice(["b", "c", "d", "h", "l", "m", "n", "t", "s", "v"])
                van = random.choice(["an", "at", "en", "in", "on", "ot", "un", "ut"])
                tu = phu + van
                others = [random.choice(PHU_AM) + van for _ in range(3)]
                others = [o for o in others if o != tu][:3]
                while len(others) < 3:
                    others.append(random.choice(PHU_AM) + random.choice(VAN_DON_GIAN))
                choices = [tu] + others
                random.shuffle(choices)
                questions.append({
                    "question": f'Ghép phụ âm "{phu}" với vần "{van}" được từ gì?',
                    "type": "choice",
                    "choices": choices,
                    "answer": tu,
                    "image": None
                })
            else:  # am_dau
                tu_info = random.choice(TU_DON_GIAN)
                tu = tu_info["tu"]
                first_char = tu[0]
                if tu[:2] in ["ch", "gh", "kh", "ng", "nh", "ph", "th", "tr", "gi"]:
                    first_char = tu[:2]
                choices = [first_char] + random.sample([p for p in PHU_AM if p != first_char], min(3, len([p for p in PHU_AM if p != first_char])))
                while len(choices) < 4:
                    choices.append(random.choice(PHU_AM))
                random.shuffle(choices)
                questions.append({
                    "question": f'Từ "{tu}" có âm đầu là gì?',
                    "type": "choice",
                    "choices": choices[:4],
                    "answer": first_char,
                    "image": None
                })

    elif topic_id == "ghep_van_1":
        qtypes = ["tim_van", "ghep", "cung_van", "dien_van", "fill_ghep"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            if qtype == "tim_van":
                van = random.choice(VAN_DON_GIAN)
                phu = random.choice(["b", "c", "d", "h", "l", "m", "n", "t"])
                tu = phu + van
                others = [v for v in VAN_DON_GIAN if v != van]
                choices = [van] + random.sample(others, 3)
                random.shuffle(choices)
                questions.append({
                    "question": f'Từ "{tu}" có vần gì?',
                    "type": "choice",
                    "choices": choices,
                    "answer": van,
                    "image": None
                })
            elif qtype == "ghep":
                phu = random.choice(["b", "c", "d", "h", "l", "m", "n", "t"])
                van = random.choice(VAN_DON_GIAN[:16])  # vần đơn giản nhất
                tu = phu + van
                wrong_vans = random.sample([v for v in VAN_DON_GIAN if v != van], 3)
                choices = [tu] + [phu + v for v in wrong_vans]
                random.shuffle(choices)
                questions.append({
                    "question": f'Ghép "{phu}" + "{van}" = ?',
                    "type": "choice",
                    "choices": choices,
                    "answer": tu,
                    "image": None
                })
            elif qtype == "cung_van":
                van = random.choice(VAN_DON_GIAN[:12])
                phu1 = random.choice(["b", "c", "d", "h", "l"])
                phu2 = random.choice(["m", "n", "s", "t", "v"])
                tu1 = phu1 + van
                tu2 = phu2 + van
                wrong_van = random.choice([v for v in VAN_DON_GIAN if v != van])
                wrong_tu = random.choice(["b", "c", "d"]) + wrong_van
                choices = [tu2, wrong_tu, random.choice(["b", "h"]) + random.choice([v for v in VAN_DON_GIAN if v != van]),
                          random.choice(["l", "m"]) + random.choice([v for v in VAN_DON_GIAN if v != van])]
                random.shuffle(choices)
                questions.append({
                    "question": f'Từ nào có cùng vần với "{tu1}"?',
                    "type": "choice",
                    "choices": choices,
                    "answer": tu2,
                    "image": None
                })
            elif qtype == "dien_van":
                van = random.choice(VAN_DON_GIAN[:12])
                phu = random.choice(["b", "c", "d", "h", "l", "m", "n", "t"])
                tu = phu + van
                display = phu + "___"
                others = random.sample([v for v in VAN_DON_GIAN if v != van], 3)
                choices = [van] + others
                random.shuffle(choices)
                questions.append({
                    "question": f'Điền vần: {display}',
                    "type": "choice",
                    "choices": choices,
                    "answer": van,
                    "image": None
                })
            elif qtype == "fill_ghep":
                phu = random.choice(["b", "c", "d", "h", "l", "m", "n", "t"])
                van = random.choice(VAN_DON_GIAN[:12])
                tu = phu + van
                questions.append({
                    "question": f'Ghép phụ âm "{phu}" với vần "{van}", điền từ được:',
                    "type": "fill",
                    "hint": f"Viết từ ghép được",
                    "answer": tu,
                    "image": None
                })

    elif topic_id == "tap_doc_tu":
        qtypes = ["nghia_tu", "chon_tu", "noi_hinh", "phan_loai"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            tu_info = random.choice(TU_DON_GIAN)
            others = [t for t in TU_DON_GIAN if t["tu"] != tu_info["tu"]]
            if qtype == "nghia_tu":
                choices = [tu_info["nghia"]] + [t["nghia"] for t in random.sample(others, 3)]
                random.shuffle(choices)
                questions.append({
                    "question": f'Từ "{tu_info["tu"]}" có nghĩa là gì?',
                    "type": "choice",
                    "choices": choices,
                    "answer": tu_info["nghia"],
                    "image": None
                })
            elif qtype == "chon_tu":
                choices = [tu_info["tu"]] + [t["tu"] for t in random.sample(others, 3)]
                random.shuffle(choices)
                questions.append({
                    "question": f'Từ nào có nghĩa là "{tu_info["nghia"]}"?',
                    "type": "choice",
                    "choices": choices,
                    "answer": tu_info["tu"],
                    "image": None
                })
            elif qtype == "noi_hinh":
                animals = [t for t in TU_DON_GIAN if "con" in t["nghia"].lower() or "🐟" in t["nghia"] or "🐔" in t["nghia"]]
                if len(animals) >= 4:
                    a = random.choice(animals)
                    emoji = ""
                    for ch in a["nghia"]:
                        if ord(ch) > 127:
                            emoji = ch
                    if emoji:
                        others_a = [t for t in animals if t["tu"] != a["tu"]]
                        choices = [a["tu"]] + [t["tu"] for t in random.sample(others_a, min(3, len(others_a)))]
                        while len(choices) < 4:
                            choices.append(random.choice(TU_DON_GIAN)["tu"])
                        random.shuffle(choices)
                        questions.append({
                            "question": f'<span style="font-size:3em;">{emoji}</span><br>Đây là con gì?',
                            "type": "choice",
                            "choices": choices[:4],
                            "answer": a["tu"],
                            "image": None
                        })
                        continue
                # fallback
                choices = [tu_info["tu"]] + [t["tu"] for t in random.sample(others, 3)]
                random.shuffle(choices)
                questions.append({
                    "question": f'Từ nào có nghĩa là "{tu_info["nghia"]}"?',
                    "type": "choice",
                    "choices": choices,
                    "answer": tu_info["tu"],
                    "image": None
                })
            else:  # phan_loai
                categories = {
                    "con vật": ["cá", "gà", "mèo", "chó", "voi", "trâu", "chim", "ong", "bướm", "thỏ", "rùa"],
                    "đồ vật": ["bàn", "ghế", "sách", "bút", "xe"],
                    "thiên nhiên": ["trời", "mưa", "nắng", "lá", "cây", "trăng", "sao", "biển", "núi", "sông"],
                }
                cat = random.choice(list(categories.keys()))
                correct_words = categories[cat]
                correct_word = random.choice(correct_words)
                other_cats = [c for c in categories if c != cat]
                wrong_words = []
                for oc in other_cats:
                    wrong_words.extend(categories[oc])
                choices = [correct_word] + random.sample(wrong_words, 3)
                random.shuffle(choices)
                questions.append({
                    "question": f'Từ nào chỉ "{cat}"?',
                    "type": "choice",
                    "choices": choices,
                    "answer": correct_word,
                    "image": None
                })

    elif topic_id == "van_phuc_tap":
        qtypes = ["tim_van", "ghep", "cung_van"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            van = random.choice(VAN_PHUC_TAP)
            phu = random.choice(["b", "c", "d", "h", "l", "m", "n", "t", "s", "x"])
            tu = phu + van
            qtype = random.choice(qtypes)
            if qtype == "tim_van":
                others = [v for v in VAN_PHUC_TAP if v != van]
                choices = [van] + random.sample(others, 3)
                random.shuffle(choices)
                questions.append({
                    "question": f'Từ "{tu}" có vần gì?',
                    "type": "choice",
                    "choices": choices,
                    "answer": van,
                    "image": None
                })
            elif qtype == "ghep":
                wrong_vans = random.sample([v for v in VAN_PHUC_TAP if v != van], 3)
                choices = [tu] + [phu + v for v in wrong_vans]
                random.shuffle(choices)
                questions.append({
                    "question": f'Ghép "{phu}" + "{van}" = ?',
                    "type": "choice",
                    "choices": choices,
                    "answer": tu,
                    "image": None
                })
            else:  # cung_van
                phu2 = random.choice([p for p in ["b", "c", "d", "h", "l", "m", "n", "t"] if p != phu])
                tu2 = phu2 + van
                wrong_tus = [random.choice(["b", "c", "d", "h"]) + random.choice([v for v in VAN_PHUC_TAP if v != van]) for _ in range(3)]
                choices = [tu2] + wrong_tus
                random.shuffle(choices)
                questions.append({
                    "question": f'Từ nào cùng vần với "{tu}"?',
                    "type": "choice",
                    "choices": choices,
                    "answer": tu2,
                    "image": None
                })

    elif topic_id == "tap_doc_cau":
        qtypes = ["hieu_cau", "dien_tu", "dung_sai"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            if qtype == "hieu_cau":
                item = random.choice(TAP_DOC_CAU_DATA)
                all_answers = [c["answer"] for c in TAP_DOC_CAU_DATA if c["answer"] != item["answer"]]
                choices = [item["answer"]] + random.sample(all_answers, min(3, len(all_answers)))
                random.shuffle(choices)
                questions.append({
                    "question": f'Đọc câu: "{item["cau"]}"<br>{item["hoi"]}',
                    "type": "choice",
                    "choices": choices,
                    "answer": item["answer"],
                    "image": None
                })
            elif qtype == "dien_tu":
                fill_data = [
                    ("___ đi học mỗi ngày.", "Em", ["Em", "Cây", "Nhà", "Sách"]),
                    ("Con mèo ___ trên ghế.", "nằm", ["nằm", "bay", "bơi", "chạy"]),
                    ("Hoa ___ trong vườn.", "nở", ["nở", "chạy", "ăn", "hát"]),
                    ("Bé ___ sữa mỗi sáng.", "uống", ["uống", "viết", "đọc", "ngủ"]),
                    ("Con chim ___ trên cành.", "hót", ["hót", "bơi", "chạy", "ăn"]),
                    ("Mẹ ___ cơm cho bé.", "nấu", ["nấu", "hát", "đọc", "bay"]),
                    ("Ba ___ báo mỗi sáng.", "đọc", ["đọc", "nấu", "bay", "bơi"]),
                    ("Con cá ___ dưới nước.", "bơi", ["bơi", "bay", "chạy", "hát"]),
                ]
                item = random.choice(fill_data)
                questions.append({
                    "question": f"Điền từ thích hợp: {item[0]}",
                    "type": "choice",
                    "choices": item[2],
                    "answer": item[1],
                    "image": None
                })
            else:  # dung_sai
                true_false = [
                    ("Con cá bơi dưới nước.", True),
                    ("Con chim bay trên trời.", True),
                    ("Con mèo sống dưới nước.", False),
                    ("Mặt trời mọc ở phía đông.", True),
                    ("Con cá biết bay.", False),
                    ("Hoa nở vào mùa xuân.", True),
                    ("Con chó biết bay.", False),
                    ("Mẹ nấu cơm trong bếp.", True),
                    ("Con voi rất nhỏ.", False),
                    ("Con kiến rất to.", False),
                ]
                item = random.choice(true_false)
                questions.append({
                    "question": f'Câu sau đúng hay sai?<br>"{item[0]}"',
                    "type": "choice",
                    "choices": ["Đúng ✅", "Sai ❌"],
                    "answer": "Đúng ✅" if item[1] else "Sai ❌",
                    "image": None
                })

    elif topic_id == "chinh_ta":
        for _ in range(num_questions):
            pair = random.choice(CHINH_TA_DATA)
            questions.append({
                "question": f'Điền phụ âm đầu: {pair["q"]}',
                "type": "choice",
                "choices": pair["choices"],
                "answer": pair["answer"],
                "image": None
            })

    elif topic_id == "dau_cau":
        qtypes = ["dien_dau", "phan_loai"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            s = random.choice(DAU_CAU_DATA)
            if qtype == "dien_dau":
                questions.append({
                    "question": f'Điền dấu câu thích hợp:<br>"{s["cau"]}___"',
                    "type": "choice",
                    "choices": [".", "?", "!"],
                    "answer": s["answer"],
                    "image": None
                })
            else:
                loai_map = {".": "Câu kể", "?": "Câu hỏi", "!": "Câu cảm thán"}
                questions.append({
                    "question": f'"{s["cau"]}{s["answer"]}" là loại câu gì?',
                    "type": "choice",
                    "choices": ["Câu kể", "Câu hỏi", "Câu cảm thán"],
                    "answer": loai_map[s["answer"]],
                    "image": None
                })

    elif topic_id == "sap_xep_cau":
        for _ in range(num_questions):
            item = random.choice(SAP_XEP_CAU_DATA)
            words = list(item["words"])
            # Tạo các thứ tự sai
            correct_str = " ".join(item["words"])
            choices = [correct_str]
            for __ in range(20):
                shuffled = list(item["words"])
                random.shuffle(shuffled)
                s = " ".join(shuffled)
                if s != correct_str and s not in choices:
                    choices.append(s)
                if len(choices) >= 4:
                    break
            while len(choices) < 4:
                shuffled = list(item["words"])
                random.shuffle(shuffled)
                choices.append(" ".join(shuffled))
            random.shuffle(choices)
            display = " / ".join(words)
            random.shuffle(words)
            display = " / ".join(words)
            questions.append({
                "question": f"Sắp xếp thành câu có nghĩa:<br><b>{display}</b>",
                "type": "choice",
                "choices": choices[:4],
                "answer": correct_str,
                "image": None
            })

    return questions


# ============================================================
# TIẾNG ANH LỚP 1 - GLOBAL SUCCESS (KẾT NỐI TRI THỨC)
# ============================================================

TIENG_ANH_TOPICS = {
    "ki1": {
        "name": "Tiếng Anh Kì 1",
        "icon": "🇬🇧",
        "topics": {
            "alphabet": {
                "name": "The Alphabet (Bảng chữ cái)",
                "icon": "🔤",
                "description": "Học bảng chữ cái A-Z, viết hoa/thường"
            },
            "hello": {
                "name": "Unit 1: Hello",
                "icon": "👋",
                "description": "Chào hỏi, giới thiệu bản thân"
            },
            "my_school": {
                "name": "Unit 2: My School",
                "icon": "🏫",
                "description": "Đồ dùng học tập và trường học"
            },
            "my_body": {
                "name": "Unit 3: My Body",
                "icon": "🧒",
                "description": "Các bộ phận cơ thể"
            },
            "my_family": {
                "name": "Unit 4: My Family",
                "icon": "👨‍👩‍👧‍👦",
                "description": "Thành viên gia đình"
            },
        }
    },
    "ki2": {
        "name": "Tiếng Anh Kì 2",
        "icon": "🇺🇸",
        "topics": {
            "my_toys": {
                "name": "Unit 5: My Toys",
                "icon": "🧸",
                "description": "Đồ chơi yêu thích"
            },
            "my_pet": {
                "name": "Unit 6: My Pet",
                "icon": "🐕",
                "description": "Vật nuôi của em"
            },
            "my_house": {
                "name": "Unit 7: My House",
                "icon": "🏠",
                "description": "Các phòng trong nhà"
            },
            "colors": {
                "name": "Unit 8: Colors",
                "icon": "🎨",
                "description": "Màu sắc"
            },
            "my_clothes": {
                "name": "Unit 9: My Clothes",
                "icon": "👕",
                "description": "Quần áo"
            },
            "numbers_en": {
                "name": "Unit 10: Numbers",
                "icon": "🔢",
                "description": "Số đếm 1-20 bằng tiếng Anh"
            },
            "fruits": {
                "name": "Unit 11: Fruits",
                "icon": "🍎",
                "description": "Các loại trái cây"
            },
        }
    }
}

ENGLISH_VOCAB = {
    "alphabet": {
        "words": [
            {"en": "A", "vn": "Ây", "emoji": "🅰️"},
            {"en": "B", "vn": "Bi", "emoji": "🅱️"},
            {"en": "C", "vn": "Xi", "emoji": "©️"},
            {"en": "D", "vn": "Đi", "emoji": "🇩"},
            {"en": "E", "vn": "I", "emoji": "📧"},
            {"en": "F", "vn": "Ép", "emoji": "🇫"},
            {"en": "G", "vn": "Gi", "emoji": "🇬"},
            {"en": "H", "vn": "Ết", "emoji": "🇭"},
            {"en": "I", "vn": "Ai", "emoji": "ℹ️"},
            {"en": "J", "vn": "Giây", "emoji": "🇯"},
            {"en": "K", "vn": "Kây", "emoji": "🇰"},
            {"en": "L", "vn": "Eo", "emoji": "🇱"},
            {"en": "M", "vn": "Em", "emoji": "Ⓜ️"},
            {"en": "N", "vn": "En", "emoji": "🇳"},
            {"en": "O", "vn": "Âu", "emoji": "🅾️"},
            {"en": "P", "vn": "Pi", "emoji": "🅿️"},
            {"en": "Q", "vn": "Kiu", "emoji": "🇶"},
            {"en": "R", "vn": "A-rờ", "emoji": "🇷"},
            {"en": "S", "vn": "Ét", "emoji": "🇸"},
            {"en": "T", "vn": "Ti", "emoji": "🇹"},
            {"en": "U", "vn": "Du", "emoji": "🇺"},
            {"en": "V", "vn": "Vi", "emoji": "🇻"},
            {"en": "W", "vn": "Đáp-bờ-liu", "emoji": "🇼"},
            {"en": "X", "vn": "Éc-xờ", "emoji": "❌"},
            {"en": "Y", "vn": "Oai", "emoji": "🇾"},
            {"en": "Z", "vn": "Zét", "emoji": "🇿"},
        ]
    },
    "hello": {
        "sentences": [
            {"en": "Hello!", "vn": "Xin chào!"},
            {"en": "Hi!", "vn": "Chào!"},
            {"en": "Goodbye!", "vn": "Tạm biệt!"},
            {"en": "I'm fine.", "vn": "Tôi khỏe."},
            {"en": "Thank you.", "vn": "Cảm ơn."},
            {"en": "What's your name?", "vn": "Bạn tên là gì?"},
            {"en": "My name is...", "vn": "Tên tôi là..."},
            {"en": "Nice to meet you.", "vn": "Rất vui được gặp bạn."},
            {"en": "How are you?", "vn": "Bạn khỏe không?"},
            {"en": "I'm good.", "vn": "Tôi ổn."},
            {"en": "See you later.", "vn": "Hẹn gặp lại."},
            {"en": "Good morning.", "vn": "Chào buổi sáng."},
            {"en": "Good afternoon.", "vn": "Chào buổi chiều."},
            {"en": "Good night.", "vn": "Chúc ngủ ngon."},
        ]
    },
    "my_school": {
        "words": [
            {"en": "book", "vn": "quyển sách", "emoji": "📕"},
            {"en": "pen", "vn": "cây bút", "emoji": "🖊️"},
            {"en": "pencil", "vn": "bút chì", "emoji": "✏️"},
            {"en": "ruler", "vn": "thước kẻ", "emoji": "📏"},
            {"en": "eraser", "vn": "cục tẩy", "emoji": "🧽"},
            {"en": "bag", "vn": "cặp sách", "emoji": "🎒"},
            {"en": "desk", "vn": "bàn học", "emoji": "🪑"},
            {"en": "chair", "vn": "ghế", "emoji": "💺"},
            {"en": "teacher", "vn": "giáo viên", "emoji": "👩‍🏫"},
            {"en": "school", "vn": "trường học", "emoji": "🏫"},
            {"en": "notebook", "vn": "vở", "emoji": "📓"},
            {"en": "board", "vn": "bảng", "emoji": "📋"},
            {"en": "crayon", "vn": "bút sáp màu", "emoji": "🖍️"},
            {"en": "scissors", "vn": "cái kéo", "emoji": "✂️"},
            {"en": "glue", "vn": "keo dán", "emoji": "🧴"},
        ]
    },
    "my_body": {
        "words": [
            {"en": "head", "vn": "đầu", "emoji": "🧠"},
            {"en": "eyes", "vn": "mắt", "emoji": "👀"},
            {"en": "ears", "vn": "tai", "emoji": "👂"},
            {"en": "nose", "vn": "mũi", "emoji": "👃"},
            {"en": "mouth", "vn": "miệng", "emoji": "👄"},
            {"en": "hand", "vn": "bàn tay", "emoji": "🤚"},
            {"en": "foot", "vn": "bàn chân", "emoji": "🦶"},
            {"en": "arm", "vn": "cánh tay", "emoji": "💪"},
            {"en": "leg", "vn": "chân", "emoji": "🦵"},
            {"en": "finger", "vn": "ngón tay", "emoji": "☝️"},
            {"en": "hair", "vn": "tóc", "emoji": "💇"},
            {"en": "face", "vn": "khuôn mặt", "emoji": "😊"},
            {"en": "teeth", "vn": "răng", "emoji": "🦷"},
            {"en": "shoulder", "vn": "vai", "emoji": "🧍"},
        ]
    },
    "my_family": {
        "words": [
            {"en": "father", "vn": "bố", "emoji": "👨"},
            {"en": "mother", "vn": "mẹ", "emoji": "👩"},
            {"en": "brother", "vn": "anh/em trai", "emoji": "👦"},
            {"en": "sister", "vn": "chị/em gái", "emoji": "👧"},
            {"en": "grandfather", "vn": "ông", "emoji": "👴"},
            {"en": "grandmother", "vn": "bà", "emoji": "👵"},
            {"en": "baby", "vn": "em bé", "emoji": "👶"},
            {"en": "family", "vn": "gia đình", "emoji": "👨‍👩‍👧‍👦"},
            {"en": "uncle", "vn": "chú/bác", "emoji": "👨‍🦱"},
            {"en": "aunt", "vn": "cô/dì", "emoji": "👩‍🦱"},
        ]
    },
    "my_toys": {
        "words": [
            {"en": "ball", "vn": "quả bóng", "emoji": "⚽"},
            {"en": "doll", "vn": "búp bê", "emoji": "🧸"},
            {"en": "car", "vn": "xe ô tô", "emoji": "🚗"},
            {"en": "kite", "vn": "cái diều", "emoji": "🪁"},
            {"en": "robot", "vn": "người máy", "emoji": "🤖"},
            {"en": "teddy bear", "vn": "gấu bông", "emoji": "🧸"},
            {"en": "puzzle", "vn": "xếp hình", "emoji": "🧩"},
            {"en": "bicycle", "vn": "xe đạp", "emoji": "🚲"},
            {"en": "train", "vn": "tàu hỏa", "emoji": "🚂"},
            {"en": "plane", "vn": "máy bay", "emoji": "✈️"},
            {"en": "boat", "vn": "thuyền", "emoji": "⛵"},
            {"en": "balloon", "vn": "bóng bay", "emoji": "🎈"},
        ]
    },
    "my_pet": {
        "words": [
            {"en": "dog", "vn": "con chó", "emoji": "🐕"},
            {"en": "cat", "vn": "con mèo", "emoji": "🐈"},
            {"en": "fish", "vn": "con cá", "emoji": "🐟"},
            {"en": "bird", "vn": "con chim", "emoji": "🐦"},
            {"en": "rabbit", "vn": "con thỏ", "emoji": "🐇"},
            {"en": "hamster", "vn": "chuột hamster", "emoji": "🐹"},
            {"en": "turtle", "vn": "con rùa", "emoji": "🐢"},
            {"en": "parrot", "vn": "con vẹt", "emoji": "🦜"},
            {"en": "goldfish", "vn": "cá vàng", "emoji": "🐠"},
            {"en": "duck", "vn": "con vịt", "emoji": "🦆"},
            {"en": "chicken", "vn": "con gà", "emoji": "🐔"},
            {"en": "horse", "vn": "con ngựa", "emoji": "🐴"},
        ]
    },
    "my_house": {
        "words": [
            {"en": "house", "vn": "ngôi nhà", "emoji": "🏠"},
            {"en": "bedroom", "vn": "phòng ngủ", "emoji": "🛏️"},
            {"en": "kitchen", "vn": "nhà bếp", "emoji": "🍳"},
            {"en": "bathroom", "vn": "phòng tắm", "emoji": "🚿"},
            {"en": "living room", "vn": "phòng khách", "emoji": "🛋️"},
            {"en": "garden", "vn": "vườn", "emoji": "🌻"},
            {"en": "door", "vn": "cửa ra vào", "emoji": "🚪"},
            {"en": "window", "vn": "cửa sổ", "emoji": "🪟"},
            {"en": "roof", "vn": "mái nhà", "emoji": "🏠"},
            {"en": "floor", "vn": "sàn nhà", "emoji": "🧱"},
            {"en": "stairs", "vn": "cầu thang", "emoji": "🪜"},
            {"en": "garage", "vn": "nhà để xe", "emoji": "🅿️"},
        ]
    },
    "colors": {
        "words": [
            {"en": "red", "vn": "màu đỏ", "emoji": "🔴"},
            {"en": "blue", "vn": "màu xanh dương", "emoji": "🔵"},
            {"en": "green", "vn": "màu xanh lá", "emoji": "🟢"},
            {"en": "yellow", "vn": "màu vàng", "emoji": "🟡"},
            {"en": "orange", "vn": "màu cam", "emoji": "🟠"},
            {"en": "purple", "vn": "màu tím", "emoji": "🟣"},
            {"en": "pink", "vn": "màu hồng", "emoji": "💗"},
            {"en": "white", "vn": "màu trắng", "emoji": "⚪"},
            {"en": "black", "vn": "màu đen", "emoji": "⚫"},
            {"en": "brown", "vn": "màu nâu", "emoji": "🟤"},
            {"en": "gray", "vn": "màu xám", "emoji": "🩶"},
            {"en": "gold", "vn": "màu vàng kim", "emoji": "🥇"},
        ]
    },
    "my_clothes": {
        "words": [
            {"en": "shirt", "vn": "áo sơ mi", "emoji": "👕"},
            {"en": "dress", "vn": "váy đầm", "emoji": "👗"},
            {"en": "hat", "vn": "mũ/nón", "emoji": "🧢"},
            {"en": "shoes", "vn": "giày", "emoji": "👟"},
            {"en": "socks", "vn": "tất/vớ", "emoji": "🧦"},
            {"en": "pants", "vn": "quần dài", "emoji": "👖"},
            {"en": "jacket", "vn": "áo khoác", "emoji": "🧥"},
            {"en": "skirt", "vn": "chân váy", "emoji": "👗"},
            {"en": "scarf", "vn": "khăn quàng", "emoji": "🧣"},
            {"en": "gloves", "vn": "găng tay", "emoji": "🧤"},
            {"en": "boots", "vn": "ủng", "emoji": "🥾"},
            {"en": "T-shirt", "vn": "áo phông", "emoji": "👕"},
        ]
    },
    "numbers_en": {
        "words": [
            {"en": "one", "vn": "một", "emoji": "1️⃣", "num": 1},
            {"en": "two", "vn": "hai", "emoji": "2️⃣", "num": 2},
            {"en": "three", "vn": "ba", "emoji": "3️⃣", "num": 3},
            {"en": "four", "vn": "bốn", "emoji": "4️⃣", "num": 4},
            {"en": "five", "vn": "năm", "emoji": "5️⃣", "num": 5},
            {"en": "six", "vn": "sáu", "emoji": "6️⃣", "num": 6},
            {"en": "seven", "vn": "bảy", "emoji": "7️⃣", "num": 7},
            {"en": "eight", "vn": "tám", "emoji": "8️⃣", "num": 8},
            {"en": "nine", "vn": "chín", "emoji": "9️⃣", "num": 9},
            {"en": "ten", "vn": "mười", "emoji": "🔟", "num": 10},
            {"en": "eleven", "vn": "mười một", "emoji": "1️⃣1️⃣", "num": 11},
            {"en": "twelve", "vn": "mười hai", "emoji": "1️⃣2️⃣", "num": 12},
            {"en": "thirteen", "vn": "mười ba", "emoji": "1️⃣3️⃣", "num": 13},
            {"en": "fourteen", "vn": "mười bốn", "emoji": "1️⃣4️⃣", "num": 14},
            {"en": "fifteen", "vn": "mười lăm", "emoji": "1️⃣5️⃣", "num": 15},
            {"en": "sixteen", "vn": "mười sáu", "emoji": "1️⃣6️⃣", "num": 16},
            {"en": "seventeen", "vn": "mười bảy", "emoji": "1️⃣7️⃣", "num": 17},
            {"en": "eighteen", "vn": "mười tám", "emoji": "1️⃣8️⃣", "num": 18},
            {"en": "nineteen", "vn": "mười chín", "emoji": "1️⃣9️⃣", "num": 19},
            {"en": "twenty", "vn": "hai mươi", "emoji": "2️⃣0️⃣", "num": 20},
        ]
    },
    "fruits": {
        "words": [
            {"en": "apple", "vn": "quả táo", "emoji": "🍎"},
            {"en": "banana", "vn": "quả chuối", "emoji": "🍌"},
            {"en": "orange", "vn": "quả cam", "emoji": "🍊"},
            {"en": "grape", "vn": "quả nho", "emoji": "🍇"},
            {"en": "watermelon", "vn": "dưa hấu", "emoji": "🍉"},
            {"en": "strawberry", "vn": "dâu tây", "emoji": "🍓"},
            {"en": "mango", "vn": "xoài", "emoji": "🥭"},
            {"en": "pineapple", "vn": "dứa", "emoji": "🍍"},
            {"en": "cherry", "vn": "quả anh đào", "emoji": "🍒"},
            {"en": "peach", "vn": "quả đào", "emoji": "🍑"},
            {"en": "lemon", "vn": "chanh", "emoji": "🍋"},
            {"en": "coconut", "vn": "dừa", "emoji": "🥥"},
        ]
    },
}


def generate_english_questions(topic_id, num_questions=10, difficulty=3):
    """Tạo câu hỏi Tiếng Anh - MỞ RỘNG"""
    questions = []

    def scale_qtypes(all_qtypes, diff):
        n = max(2, len(all_qtypes) * diff // 5)
        return all_qtypes[:n]
    vocab_data = ENGLISH_VOCAB.get(topic_id, {})

    if topic_id == "alphabet":
        letters = vocab_data.get("words", [])
        qtypes = ["upper_lower", "next_letter", "identify", "count", "missing"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            letter = random.choice(letters)
            if qtype == "upper_lower":
                lower = letter["en"].lower()
                upper = letter["en"].upper()
                others = [l["en"].upper() for l in letters if l["en"] != letter["en"]]
                choices = [upper] + random.sample(others, 3)
                random.shuffle(choices)
                questions.append({
                    "question": f'Chữ "{lower}" viết hoa là gì?',
                    "type": "choice",
                    "choices": choices,
                    "answer": upper,
                    "image": None
                })
            elif qtype == "next_letter":
                idx = ord(letter["en"]) - ord("A")
                if idx < 25:
                    next_l = chr(ord("A") + idx + 1)
                    others = [chr(ord("A") + i) for i in range(26) if chr(ord("A") + i) != next_l]
                    choices = [next_l] + random.sample(others, 3)
                    random.shuffle(choices)
                    questions.append({
                        "question": f'Chữ cái nào đứng sau "{letter["en"]}"?',
                        "type": "choice",
                        "choices": choices,
                        "answer": next_l,
                        "image": None
                    })
                else:
                    questions.append({
                        "question": 'Bảng chữ cái tiếng Anh có bao nhiêu chữ?',
                        "type": "choice",
                        "choices": ["24", "25", "26", "28"],
                        "answer": "26",
                        "image": None
                    })
            elif qtype == "identify":
                choices = [letter["en"]] + [l["en"] for l in random.sample([x for x in letters if x["en"] != letter["en"]], 3)]
                random.shuffle(choices)
                questions.append({
                    "question": f'Chữ cái nào đọc là "{letter["vn"]}"?',
                    "type": "choice",
                    "choices": choices,
                    "answer": letter["en"],
                    "image": None
                })
            elif qtype == "count":
                idx = ord(letter["en"]) - ord("A") + 1
                questions.append({
                    "question": f'Chữ "{letter["en"]}" là chữ cái thứ mấy?',
                    "type": "choice",
                    "choices": [str(c) for c in sorted(_make_choices(idx, list(range(1, 27))))],
                    "answer": str(idx),
                    "image": None
                })
            else:  # missing
                idx = random.randint(0, 23)
                seq = [chr(ord("A") + idx), "?", chr(ord("A") + idx + 2)]
                answer = chr(ord("A") + idx + 1)
                display = " _ ".join(seq).replace("?", "___")
                others = [chr(ord("A") + i) for i in range(26) if chr(ord("A") + i) != answer]
                choices = [answer] + random.sample(others, 3)
                random.shuffle(choices)
                questions.append({
                    "question": f"Điền chữ cái còn thiếu: {seq[0]}, ___, {seq[2]}",
                    "type": "choice",
                    "choices": choices,
                    "answer": answer,
                    "image": None
                })

    elif topic_id == "hello":
        sentences = vocab_data.get("sentences", [])
        qtypes = ["en_to_vn", "vn_to_en", "reply"]
        qtypes = scale_qtypes(qtypes, difficulty)
        replies = [
            {"q": "Hello!", "a": "Hi!", "wrong": ["Goodbye!", "Thank you.", "I'm sorry."]},
            {"q": "How are you?", "a": "I'm fine.", "wrong": ["Goodbye!", "My name is...", "Thank you."]},
            {"q": "What's your name?", "a": "My name is...", "wrong": ["I'm fine.", "Goodbye!", "Thank you."]},
            {"q": "Thank you.", "a": "You're welcome.", "wrong": ["Goodbye!", "Hello!", "I'm fine."]},
            {"q": "Goodbye!", "a": "See you later.", "wrong": ["I'm fine.", "Thank you.", "My name is..."]},
        ]
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            if qtype == "en_to_vn":
                s = random.choice(sentences)
                others = [x for x in sentences if x["en"] != s["en"]]
                choices = [s["vn"]] + [x["vn"] for x in random.sample(others, min(3, len(others)))]
                random.shuffle(choices)
                questions.append({
                    "question": f'"{s["en"]}" nghĩa là gì?',
                    "type": "choice",
                    "choices": choices,
                    "answer": s["vn"],
                    "image": None
                })
            elif qtype == "vn_to_en":
                s = random.choice(sentences)
                others = [x for x in sentences if x["en"] != s["en"]]
                choices = [s["en"]] + [x["en"] for x in random.sample(others, min(3, len(others)))]
                random.shuffle(choices)
                questions.append({
                    "question": f'"{s["vn"]}" dịch sang tiếng Anh là gì?',
                    "type": "choice",
                    "choices": choices,
                    "answer": s["en"],
                    "image": None
                })
            else:  # reply
                r = random.choice(replies)
                choices = [r["a"]] + r["wrong"]
                random.shuffle(choices)
                questions.append({
                    "question": f'Bạn nói: "{r["q"]}". Trả lời thế nào?',
                    "type": "choice",
                    "choices": choices,
                    "answer": r["a"],
                    "image": None
                })

    elif topic_id == "numbers_en":
        words = vocab_data.get("words", [])
        qtypes = ["en_to_num", "num_to_en", "vn_to_en", "next_num", "count_emoji"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            qtype = random.choice(qtypes)
            word = random.choice(words)
            others = [w for w in words if w["en"] != word["en"]]
            if qtype == "en_to_num":
                choices = [str(word["num"])] + [str(w["num"]) for w in random.sample(others, 3)]
                random.shuffle(choices)
                questions.append({
                    "question": f'"{word["en"]}" là số mấy?',
                    "type": "choice",
                    "choices": choices,
                    "answer": str(word["num"]),
                    "image": None
                })
            elif qtype == "num_to_en":
                choices = [word["en"]] + [w["en"] for w in random.sample(others, 3)]
                random.shuffle(choices)
                questions.append({
                    "question": f'Số {word["num"]} trong tiếng Anh là gì?',
                    "type": "choice",
                    "choices": choices,
                    "answer": word["en"],
                    "image": None
                })
            elif qtype == "vn_to_en":
                choices = [word["en"]] + [w["en"] for w in random.sample(others, 3)]
                random.shuffle(choices)
                questions.append({
                    "question": f'"{word["vn"]}" trong tiếng Anh là?',
                    "type": "choice",
                    "choices": choices,
                    "answer": word["en"],
                    "image": None
                })
            elif qtype == "next_num":
                if word["num"] < 20:
                    next_w = [w for w in words if w["num"] == word["num"] + 1]
                    if next_w:
                        nw = next_w[0]
                        choices = [nw["en"]] + [w["en"] for w in random.sample(others, 3)]
                        random.shuffle(choices)
                        questions.append({
                            "question": f'Sau "{word["en"]}" là số nào?',
                            "type": "choice",
                            "choices": choices,
                            "answer": nw["en"],
                            "image": None
                        })
                        continue
                # fallback
                choices = [word["en"]] + [w["en"] for w in random.sample(others, 3)]
                random.shuffle(choices)
                questions.append({
                    "question": f'Số {word["num"]} trong tiếng Anh là gì?',
                    "type": "choice",
                    "choices": choices,
                    "answer": word["en"],
                    "image": None
                })
            else:  # count_emoji
                count = random.randint(1, 10)
                emoji = random.choice(["⭐", "🍎", "🎈", "🌸", "🐟"])
                count_word = [w for w in words if w.get("num") == count]
                if count_word:
                    cw = count_word[0]
                    display = '<span style="font-size:2em;letter-spacing:6px;">' + emoji * count + '</span>'
                    choices = [cw["en"]] + [w["en"] for w in random.sample([x for x in words if x["en"] != cw["en"]], 3)]
                    random.shuffle(choices)
                    questions.append({
                        "question": f"Count: How many {emoji}?<br>{display}",
                        "type": "choice",
                        "choices": choices,
                        "answer": cw["en"],
                        "image": None
                    })
                else:
                    choices = [word["en"]] + [w["en"] for w in random.sample(others, 3)]
                    random.shuffle(choices)
                    questions.append({
                        "question": f'Số {word["num"]} trong tiếng Anh là gì?',
                        "type": "choice",
                        "choices": choices,
                        "answer": word["en"],
                        "image": None
                    })

    else:
        # Generic vocabulary topics (my_school, my_body, my_family, etc.)
        words = vocab_data.get("words", vocab_data.get("sentences", []))
        if not words:
            return questions

        qtypes = ["en_to_vn", "vn_to_en", "emoji_to_en", "emoji_to_vn", "spelling", "fill_en", "fill_vn"]
        qtypes = scale_qtypes(qtypes, difficulty)
        for _ in range(num_questions):
            word = random.choice(words)
            others = [w for w in words if w.get("en", "") != word.get("en", "")]
            if len(others) < 3:
                others = others * 3
            qtype = random.choice(qtypes)
            emoji = word.get("emoji", "")

            if qtype == "en_to_vn":
                display = f'{emoji} "{word["en"]}"' if emoji else f'"{word["en"]}"'
                choices = [word["vn"]] + [w["vn"] for w in random.sample(others, 3)]
                random.shuffle(choices)
                questions.append({
                    "question": f'{display} nghĩa là gì?',
                    "type": "choice",
                    "choices": choices,
                    "answer": word["vn"],
                    "image": None
                })
            elif qtype == "vn_to_en":
                display = f'{emoji} "{word["vn"]}"' if emoji else f'"{word["vn"]}"'
                choices = [word["en"]] + [w["en"] for w in random.sample(others, 3)]
                random.shuffle(choices)
                questions.append({
                    "question": f'{display} dịch sang tiếng Anh là?',
                    "type": "choice",
                    "choices": choices,
                    "answer": word["en"],
                    "image": None
                })
            elif qtype == "emoji_to_en" and emoji:
                choices = [word["en"]] + [w["en"] for w in random.sample(others, 3)]
                random.shuffle(choices)
                questions.append({
                    "question": f'<span style="font-size:3em;">{emoji}</span><br>Đây là gì trong tiếng Anh?',
                    "type": "choice",
                    "choices": choices,
                    "answer": word["en"],
                    "image": None
                })
            elif qtype == "emoji_to_vn" and emoji:
                choices = [word["vn"]] + [w["vn"] for w in random.sample(others, 3)]
                random.shuffle(choices)
                questions.append({
                    "question": f'<span style="font-size:3em;">{emoji}</span><br>Đây là gì?',
                    "type": "choice",
                    "choices": choices,
                    "answer": word["vn"],
                    "image": None
                })
            elif qtype == "spelling" and len(word["en"]) >= 3:
                en = word["en"]
                idx = random.randint(0, len(en) - 1)
                display = en[:idx] + "___" + en[idx+1:]
                correct = en[idx]
                wrong_letters = [chr(c) for c in range(ord('a'), ord('z')+1) if chr(c) != correct.lower()]
                choices = [correct] + random.sample(wrong_letters, 3)
                random.shuffle(choices)
                questions.append({
                    "question": f'{emoji} Điền chữ cái: <b>{display}</b> ({word["vn"]})',
                    "type": "choice",
                    "choices": choices,
                    "answer": correct,
                    "image": None
                })
            elif qtype == "fill_en":
                display = f'{emoji} "{word["vn"]}"' if emoji else f'"{word["vn"]}"'
                questions.append({
                    "question": f'{display} viết bằng tiếng Anh là gì?',
                    "type": "fill",
                    "hint": "Viết từ tiếng Anh",
                    "answer": word["en"],
                    "image": None
                })
            elif qtype == "fill_vn" and emoji:
                questions.append({
                    "question": f'<span style="font-size:3em;">{emoji}</span><br>Viết tên tiếng Việt:',
                    "type": "fill",
                    "hint": "Viết từ tiếng Việt",
                    "answer": word["vn"],
                    "image": None
                })
            else:
                # Fallback en_to_vn
                choices = [word["vn"]] + [w["vn"] for w in random.sample(others, 3)]
                random.shuffle(choices)
                questions.append({
                    "question": f'"{word.get("en", "")}" nghĩa là gì?',
                    "type": "choice",
                    "choices": choices,
                    "answer": word["vn"],
                    "image": None
                })

    return questions


# ============================================================
# ALL SUBJECTS
# ============================================================

SUBJECTS = {
    "toan": {
        "name": "Toán",
        "icon": "🔢",
        "color": "#FF6B6B",
        "description": "Toán lớp 1 - Kết nối tri thức",
        "semesters": TOAN_TOPICS
    },
    "tieng_viet": {
        "name": "Tiếng Việt",
        "icon": "📖",
        "color": "#4ECDC4",
        "description": "Tiếng Việt lớp 1 - Kết nối tri thức",
        "semesters": TIENG_VIET_TOPICS
    },
    "tieng_anh": {
        "name": "Tiếng Anh",
        "icon": "🌍",
        "color": "#45B7D1",
        "description": "Tiếng Anh lớp 1 - Global Success",
        "semesters": TIENG_ANH_TOPICS
    }
}

GENERATORS = {
    "toan": generate_toan_questions,
    "tieng_viet": generate_tieng_viet_questions,
    "tieng_anh": generate_english_questions
}
