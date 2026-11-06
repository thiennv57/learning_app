# -*- coding: utf-8 -*-
"""
Quản lý bộ câu hỏi cho các đợt thi
"""
import json
import os
import csv
import io
import re
from datetime import datetime
from typing import List, Dict, Optional

# Try to import docx support
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

QUESTION_SETS_FILE = os.path.join(os.path.dirname(__file__), "data", "question_sets.json")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Tạo thư mục data nếu chưa tồn tại
os.makedirs(DATA_DIR, exist_ok=True)


def load_question_sets() -> Dict:
    """Tải tất cả bộ câu hỏi từ file"""
    if os.path.exists(QUESTION_SETS_FILE):
        try:
            with open(QUESTION_SETS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_question_sets(sets_data: Dict):
    """Lưu bộ câu hỏi vào file"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(QUESTION_SETS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sets_data, f, ensure_ascii=False, indent=2)


def parse_csv_questions(file_content: str) -> tuple[List[Dict], str]:
    """
    Parse CSV file thành danh sách câu hỏi.
    Format CSV: question, option_a, option_b, option_c, option_d, answer
    
    Returns: (list_of_questions, error_message)
    """
    try:
        lines = file_content.strip().split('\n')
        reader = csv.DictReader(lines)
        
        questions = []
        for idx, row in enumerate(reader, 1):
            # Kiểm tra các cột bắt buộc
            required_fields = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'answer']
            if not all(field in row for field in required_fields):
                return [], f"Hàng {idx}: Thiếu cột. Cần có: {', '.join(required_fields)}"
            
            # Kiểm tra answer hợp lệ
            answer = row['answer'].strip().lower()
            if answer not in ['a', 'b', 'c', 'd']:
                return [], f"Hàng {idx}: Đáp áp phải là a, b, c hoặc d. Nhận được: {answer}"
            
            # Kiểm tra question và options không trống
            question = row['question'].strip()
            if not question:
                return [], f"Hàng {idx}: Câu hỏi không được trống"
            
            options = [row[f'option_{opt}'].strip() for opt in ['a', 'b', 'c', 'd']]
            for i, opt in enumerate(options):
                if not opt:
                    return [], f"Hàng {idx}: Lựa chọn {chr(97+i)} không được trống"
            
            questions.append({
                "question": question,
                "options": {
                    "a": options[0],
                    "b": options[1],
                    "c": options[2],
                    "d": options[3],
                },
                "answer": answer
            })
        
        return questions, ""
    except Exception as e:
        return [], f"Lỗi parse CSV: {str(e)}"


def _parse_text_questions(raw_text: str) -> List[Dict]:
    """
    Parse text format (from .txt, .doc, .docx) to question list.
    Supports formats like:
      - Câu 1. Question text?
      - A. Option A
      - B. Option B
      - *C. Correct answer (marked with *)
      - D. Option D
    Returns list of question dicts
    """
    questions = []
    lines = [l.strip() for l in raw_text.splitlines()]
    
    question_text = ""
    options = {}
    answer = ""
    
    # Regex for question number: "Câu 1", "1.", "1)", etc.
    q_num_re = re.compile(r'^(?:c[aâ]u\s+\d+|question\s+\d+|\d+)[.):\s]\s*(.*)', re.IGNORECASE)
    q_alone_re = re.compile(r'^(?:c[aâ]u\s+\d+|question\s+\d+|\d+)\s*$', re.IGNORECASE)
    
    # Regex for answer option: "[*]A. text" or "[*]A) text"
    opt_re = re.compile(r'^(\*?)([ABCD])[.):\s]\s*(.*)', re.IGNORECASE)
    
    def flush():
        nonlocal question_text, options, answer
        if question_text and options and answer:
            questions.append({
                "question": question_text.strip(),
                "options": {
                    "a": options.get("A", ""),
                    "b": options.get("B", ""),
                    "c": options.get("C", ""),
                    "d": options.get("D", ""),
                },
                "answer": answer.lower()
            })
        question_text = ""
        options = {}
        answer = ""
    
    for line in lines:
        if not line:
            continue
        
        # Check for answer option
        m_opt = opt_re.match(line)
        if m_opt:
            star, letter, text = m_opt.groups()
            letter = letter.upper()
            options[letter] = text.strip()
            if star:
                answer = letter
            continue
        
        # Question alone on its line
        if q_alone_re.match(line):
            flush()
            question_text = ""
            continue
        
        # Question with number
        m_q = q_num_re.match(line)
        if m_q:
            flush()
            question_text = m_q.group(1).strip()
            continue
        
        # Continue question text if no options yet
        if not options:
            if question_text:
                question_text += " " + line
            else:
                question_text = line
    
    flush()
    return questions


def parse_question_file(file_obj, filename: str) -> tuple[List[Dict], str]:
    """
    Parse question file in various formats: CSV, TXT, DOC, DOCX
    Returns: (list_of_questions, error_message)
    """
    filename_lower = filename.lower()
    
    try:
        # CSV format
        if filename_lower.endswith('.csv'):
            stream = file_obj.read().decode("UTF8", errors="replace")
            return parse_csv_questions(stream)
        
        # DOCX format
        elif filename_lower.endswith('.docx'):
            if not DOCX_AVAILABLE:
                return [], "Thư viện python-docx chưa được cài. Hãy cài: pip install python-docx"
            
            try:
                file_obj.seek(0)
                doc = docx.Document(file_obj)
                raw_text = "\n".join(p.text for p in doc.paragraphs)
            except Exception:
                # Fallback: read XML directly
                try:
                    import zipfile
                    file_obj.seek(0)
                    data = file_obj.read()
                    with zipfile.ZipFile(io.BytesIO(data)) as zf:
                        xml_bytes = zf.read("word/document.xml")
                    xml_str = xml_bytes.decode("utf-8", errors="ignore")
                    paragraphs = re.findall(r'<w:p[ >].*?</w:p>', xml_str, re.DOTALL)
                    lines = []
                    for para in paragraphs:
                        texts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', para)
                        line = "".join(texts).strip()
                        if line:
                            lines.append(line)
                    raw_text = "\n".join(lines)
                except Exception as e:
                    return [], f"Lỗi đọc file DOCX: {str(e)}"
            
            questions = _parse_text_questions(raw_text)
            if not questions:
                return [], "Không tìm thấy câu hỏi hợp lệ trong file DOCX"
            return questions, ""
        
        # DOC or TXT format (plain text)
        else:
            file_obj.seek(0)
            raw_bytes = file_obj.read()
            
            # Try different encodings
            raw_text = None
            for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
                try:
                    raw_text = raw_bytes.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            
            if raw_text is None:
                return [], "Không thể đọc file - encoding không hỗ trợ"
            
            questions = _parse_text_questions(raw_text)
            if not questions:
                return [], "Không tìm thấy câu hỏi hợp lệ trong file"
            return questions, ""
    
    except Exception as e:
        return [], f"Lỗi xử lý file: {str(e)}"


def create_question_set(name: str, subject: str, questions: List[Dict]) -> tuple[bool, str]:
    """
    Tạo bộ câu hỏi mới.
    Số lượng câu hỏi phụ thuộc vào file tải lên (tối thiểu 1 câu).
    """
    if not questions or len(questions) < 1:
        return False, "Bộ câu hỏi phải có ít nhất 1 câu"
    
    sets_data = load_question_sets()
    
    # Tạo ID duy nhất cho bộ câu hỏi
    set_id = f"{subject}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if set_id in sets_data:
        return False, "Bộ câu hỏi này đã tồn tại"
    
    sets_data[set_id] = {
        "id": set_id,
        "name": name,
        "subject": subject,
        "total_questions": len(questions),
        "questions": questions,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    
    save_question_sets(sets_data)
    return True, f"Tạo bộ câu hỏi '{name}' thành công!"


def get_question_set(set_id: str) -> Optional[Dict]:
    """Lấy một bộ câu hỏi theo ID"""
    sets_data = load_question_sets()
    return sets_data.get(set_id)


def list_question_sets(subject: str = None) -> List[Dict]:
    """Liệt kê các bộ câu hỏi, có thể lọc theo môn"""
    sets_data = load_question_sets()
    sets_list = list(sets_data.values())
    
    if subject:
        sets_list = [s for s in sets_list if s['subject'] == subject]
    
    # Sắp xếp theo ngày tạo mới nhất trước
    sets_list.sort(key=lambda x: x['created_at'], reverse=True)
    return sets_list


def delete_question_set(set_id: str) -> tuple[bool, str]:
    """Xóa một bộ câu hỏi"""
    sets_data = load_question_sets()
    
    if set_id not in sets_data:
        return False, "Bộ câu hỏi không tồn tại"
    
    del sets_data[set_id]
    save_question_sets(sets_data)
    return True, "Xóa bộ câu hỏi thành công"


def update_question_set(set_id: str, name: str = None, questions: List[Dict] = None) -> tuple[bool, str]:
    """Cập nhật bộ câu hỏi"""
    sets_data = load_question_sets()
    
    if set_id not in sets_data:
        return False, "Bộ câu hỏi không tồn tại"
    
    if questions:
        if len(questions) < 1:
            return False, "Bộ câu hỏi phải có ít nhất 1 câu"
        sets_data[set_id]['questions'] = questions
        sets_data[set_id]['total_questions'] = len(questions)
    
    if name:
        sets_data[set_id]['name'] = name
    
    sets_data[set_id]['updated_at'] = datetime.now().isoformat()
    
    save_question_sets(sets_data)
    return True, "Cập nhật bộ câu hỏi thành công"
