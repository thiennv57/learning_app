# -*- coding: utf-8 -*-
"""
Attack & Defense Game - Logic Backend
Tách biệt với app.py để dễ quản lý.

Luồng:
  1. Admin upload file câu hỏi  → tạo Room (room_id)
  2. Admin gửi link /attack-defense/play/<room_id> cho học sinh
  3. Học sinh vào → điền tên → nhấn Sẵn sàng
  4. Admin nhấn Bắt đầu → game chạy
  5. Mỗi vòng:
       a. Gửi câu hỏi tới tất cả
       b. Học sinh trả lời (đúng → nhận kỹ năng, sai → không nhận)
       c. Học sinh chọn sử dụng 1 kỹ năng đang có hoặc bỏ qua
       d. Khi TẤT CẢ đã submit kỹ năng/bỏ qua → áp dụng hiệu ứng → chuyển câu tiếp
  6. Hết câu hỏi → kết thúc game
"""

import uuid
import re
import io
import random
import threading
from datetime import datetime, timedelta
from typing import Optional

# ------------------------------------------------------------------
# Cố gắng import python-docx; nếu chưa cài thì dùng plain-text fallback
# ------------------------------------------------------------------
try:
    import docx  # python-docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# ==================================================================
# CONSTANTS
# ==================================================================


# Danh sách nhân vật người chơi được chọn ở màn nhập tên.
# Hai người chọn trùng con vật vẫn phân biệt được vì client tự đổi màu.
ANIMALS = ["boy_short", "boy_glass", "boy_cap", "boy_spiky", "girl_tail",
           "girl_two", "girl_bob", "girl_bow", "boy_curly", "girl_long"]


def _clean_avatar(value: str) -> str:
    v = (value or "").strip().lower()
    return v if v in ANIMALS else ANIMALS[0]


SKILL_MAX_ROUNDS = 3   # Kỹ năng tối đa tồn tại 3 vòng (câu hỏi)
ROOM_TTL_SECONDS = 4 * 3600  # Phòng tự xóa sau 4 giờ

# Danh sách nhân vật hoạt hình
CARTOON_CHARACTERS = [
    "SpongeBob", "Patrick", "Squidward", "Doraemon", "Nobita",
    "Mickey", "Minnie", "Tom", "Jerry", "Superman",
    "Batman", "Wonder Woman", "Pikachu", "Charmander", "Squirtle",
    "Elmo", "Big Bird", "Conan", "Luffy", "Naruto",
]

SKILLS = {
    "attack":       {"name": "⚔️ Tấn công",           "desc": "Chọn 1 người, -10 điểm"},
    "heal":         {"name": "💊 Tăng máu",            "desc": "+10 điểm cho bản thân"},
    "counter":      {"name": "🛡️ Phản đòn",           "desc": "Phản lại đòn đơn (-10 điểm → kẻ tấn công), phản đòn toàn bộ (-5 điểm → kẻ tấn công)"},
    "double":       {"name": "💥 Tấn công mạnh hơn",   "desc": "Chọn 1 người, -15 điểm"},
    "aoe":          {"name": "🌪️ Tấn công toàn bộ",   "desc": "Tất cả người còn lại -5 điểm"},
    "balance":      {"name": "⚡ Công thủ toàn diện", "desc": "+5 điểm bản thân, tấn công ai đó -5 điểm"},
    "eliminate":    {"name": "🔮 Loại bỏ gợi ý",      "desc": "Loại bỏ 2 phương án sai ở câu tiếp theo"},
    "time_steal":   {"name": "⏱️ Cướp thời gian",     "desc": "Chọn 1 người, trừ 15s thời gian trả lời"},
    "time_bomb":    {"name": "💣 Bom thời gian",      "desc": "Tất cả người chơi trừ 15% thời gian trả lời"},
    "hide":         {"name": "👻 Ẩn Mình",             "desc": "Ẩn khỏi tấn công ở vòng sau"},
}

# ==================================================================
# DATA MODELS
# ==================================================================

class Player:
    def __init__(self, player_id: str, name: str):
        self.player_id = player_id
        self.name = name
        self.hp = 100.0
        self.ready = False
        # skills: list of {"skill": str, "rounds_left": int} (hệ cũ — không còn dùng để chơi)
        self.skills: list[dict] = []
        # Mỗi vòng: 3 kỹ năng ngẫu nhiên để chọn 1 (chỉ khi trả lời đúng)
        self.skill_options: list[str] = []
        # Phản đòn đang bật (chọn trong vòng này) — tự tắt khi bị đánh hoặc hết vòng
        self.counter_active: bool = False
        # Kỹ năng đã chọn cho vòng hiện tại (None = chưa chọn)
        self.current_action: Optional[dict] = None   # {"skill": str, "target": Optional[str]}
        self.answered_current: bool = False  # đã trả lời câu hiện tại chưa
        self.alive: bool = True
        self.eliminate_next: bool = False   # đang có buff loại 2 phương án sai câu tiếp
        self.eliminate_options: list = []   # 2 đáp án bị ẩn
        self.avatar: str = "boy_short"           # Nhân vật người chơi tự chọn
        self.correct_streak: int = 0        # Chuỗi câu trả lời đúng liên tiếp
        self.correct_count: int = 0         # Tổng số câu đúng = số rào đã nhảy qua
        self.hide_active: bool = False      # Hide đang hoạt động (bảo vệ khỏi tấn công vòng này)
        self.hide_expires_at_round: Optional[int] = None  # Hide lỹ hạn ở vòng này (active khi current_q_index < this)
        # Trừ thời gian = TRÌ HOÃN hiện câu hỏi ở vòng kế: chờ pending_delay giây mới thấy câu
        self.pending_delay: float = 0.0            # số giây sẽ bị hoãn ở vòng kế tiếp
        self.pending_delay_from: str = ""          # tên người gây ra
        self.delay_until: Optional[datetime] = None  # mốc thời gian câu hỏi mới hiện (vòng hiện tại)
        self.delay_from: str = ""                  # tên người đã trừ thời gian (vòng hiện tại)

    def to_public_dict(self):
        """Dữ liệu hiển thị cho TẤT CẢ (không lộ kỹ năng)."""
        return {
            "player_id": self.player_id,
            "name": self.name,
            "avatar": self.avatar,
            "hp": round(self.hp, 1),
            "alive": self.alive,
            "ready": self.ready,
            "hide_active": self.hide_active,  # Để client biết ai đang ẩn (bảo vệ khỏi tấn công)
            "correct_streak": self.correct_streak,  # Chuỗi trả lời đúng liên tiếp
            "correct_count": self.correct_count,    # Số rào đã vượt trên đường đua
        }

    def to_private_dict(self):
        """Dữ liệu riêng của người chơi đó (có kỹ năng)."""
        return {
            **self.to_public_dict(),
            # 3 kỹ năng được tặng vòng này để chọn 1
            "skills": [
                {**SKILLS[k], "skill": k}
                for k in self.skill_options
            ],
            "current_action": self.current_action,
            "answered_current": self.answered_current,
            "eliminate_options": self.eliminate_options,
            "delay_remaining": (
                max(0.0, round((self.delay_until - datetime.utcnow()).total_seconds(), 1))
                if self.delay_until else 0.0
            ),
            "delay_from": self.delay_from,
        }

    def tick_skills(self):
        """Giảm rounds_left của mỗi kỹ năng đi 1, loại hết các kỹ năng hết hạn."""
        for s in self.skills:
            s["rounds_left"] -= 1
        self.skills = [s for s in self.skills if s["rounds_left"] > 0]

    def add_skill(self, skill_key: str):
        """Thêm 1 kỹ năng mới (chỉ giữ tối đa 1 bản của mỗi loại, làm mới rounds_left)."""
        for s in self.skills:
            if s["skill"] == skill_key:
                s["rounds_left"] = SKILL_MAX_ROUNDS
                return
        self.skills.append({"skill": skill_key, "rounds_left": SKILL_MAX_ROUNDS})

    def consume_skill(self, skill_key: str) -> bool:
        """Tiêu thụ kỹ năng sau khi dùng. Trả về True nếu thành công."""
        for s in self.skills[:]:
            if s["skill"] == skill_key:
                self.skills.remove(s)
                return True
        return False

    def has_counter(self) -> bool:
        return self.counter_active


class Question:
    def __init__(self, text: str, options: dict, answer: str, is_html: bool = False):
        self.text = text          # nội dung câu hỏi
        self.options = options    # {"A": "...", "B": "...", "C": "...", "D": "..."}
        self.answer = answer      # "A" | "B" | "C" | "D"
        self.is_html = is_html    # True khi text/options chứa HTML (hình ảnh, công thức)

    def to_dict(self):
        """Dữ liệu câu hỏi KHÔNG có đáp án (gửi cho người chơi)."""
        return {
            "text": self.text,
            "options": self.options,
            "html": self.is_html,
        }

    def to_admin_dict(self):
        """Dữ liệu câu hỏi CÓ đáp án (chỉ gửi cho admin)."""
        return {
            "text": self.text,
            "options": self.options,
            "answer": self.answer,
            "html": self.is_html,
        }


class Room:
    def __init__(self, room_id: str, questions: list[Question], time_limit: int = 0):
        self.room_id = room_id
        self.questions = questions
        self.players: dict[str, Player] = {}   # player_id → Player
        self.state = "lobby"   # lobby | running | finished
        self.current_q_index = -1
        self.lock = threading.Lock()
        self.created_at = datetime.utcnow()
        self.time_limit = time_limit          # giây/câu, 0 = không giới hạn
        self.question_start_time: Optional[datetime] = None
        # Kết quả các vòng để hiển thị (tổng hợp cuối vòng — cho màn người chơi)
        self.round_log: list[dict] = []
        # Dòng sự kiện tức thời (mỗi khi 1 người dùng skill) — cho admin phát hoạt ảnh ngay
        self.action_log: list[dict] = []
        self._action_seq: int = 0
        # Sự kiện trong vòng hiện tại (gom lại để đẩy vào round_log cuối vòng)
        self.current_round_events: list[dict] = []
        # Snapshot HP đầu vòng (cho hp_before của round_log)
        self.hp_at_round_start: dict[str, float] = {}
        # Giai đoạn hiển thị kết quả (server-controlled, tất cả chuyển câu cùng lúc)
        self.result_phase: bool = False
        self.result_phase_until: Optional[datetime] = None
        # Lưu tổng thời gian bị trừ cho mỗi player (giây)
        self.time_penalties: dict[str, float] = {}
        # Track khi nào penalty hết hạn (vòng nào): nếu penalty dùng ở vòng N, nó lỹ hạn ở vòng N+2
        self.time_penalty_expires: dict[str, int] = {}
        # Các câu "Double HP" (nhân đôi mọi thay đổi HP) — chọn ngẫu nhiên khi bắt đầu
        self.double_rounds: set[int] = set()
        # Thống kê đáp án mỗi câu: q_index -> {"A":n,"B":n,"C":n,"D":n,"correct":n,"total":n}
        self.answer_stats: dict[int, dict] = {}
        # Tạm dừng cả phòng (đóng băng đồng hồ)
        self.paused: bool = False
        self.paused_at: Optional[datetime] = None

    # ------ helpers ------

    def alive_players(self) -> list[Player]:
        return [p for p in self.players.values() if p.alive]

    def current_question(self) -> Optional[Question]:
        if 0 <= self.current_q_index < len(self.questions):
            return self.questions[self.current_q_index]
        return None

    def all_submitted(self) -> bool:
        """Tất cả người chơi còn sống đã submit hành động (hoặc bỏ qua)."""
        return all(p.current_action is not None for p in self.alive_players())

    def _now(self) -> datetime:
        """Mốc thời gian hiện tại — đóng băng khi phòng đang tạm dừng."""
        return self.paused_at if (self.paused and self.paused_at) else datetime.utcnow()

    def get_time_remaining(self, player_id: str) -> Optional[float]:
        """Tính thời gian còn lại cho 1 player (đóng băng khi tạm dừng)."""
        if not self.time_limit > 0 or not self.question_start_time or self.state != "running" or self.result_phase:
            return None
        elapsed = (self._now() - self.question_start_time).total_seconds()
        penalty = self.time_penalties.get(player_id, 0.0)
        time_remaining = max(0.0, round(self.time_limit - elapsed + penalty, 1))
        return time_remaining

    def _base_state(self, include_answer: bool = False, player_id: str = None) -> dict:
        q = self.current_question()
        time_remaining = None
        # Nếu có player_id, tính time_remaining riêng cho player đó
        if player_id:
            time_remaining = self.get_time_remaining(player_id)
        else:
            # Fallback: tính cho trường hợp không có penalty
            if not self.result_phase and self.time_limit > 0 and self.question_start_time and self.state == "running":
                elapsed = (self._now() - self.question_start_time).total_seconds()
                time_remaining = max(0.0, round(self.time_limit - elapsed, 1))
        alive = self.alive_players()
        pending_count = sum(1 for p in alive if p.current_action is None)
        # Trạng thái hành động công khai (chỉ biết đã submit hay chưa, không biết dùng gì)
        action_status = {
            p.player_id: (p.current_action is not None)
            for p in alive
        }
        return {
            "room_id": self.room_id,
            "state": self.state,
            "current_q_index": self.current_q_index,
            "total_questions": len(self.questions),
            "question": (q.to_admin_dict() if include_answer else q.to_dict()) if q else None,
            "players": [p.to_public_dict() for p in self.players.values()],
            "round_log": self.round_log[-10:],
            "time_limit": self.time_limit,
            "time_remaining": time_remaining,
            "result_phase": self.result_phase,
            "pending_count": pending_count,
            "action_status": action_status,
            "is_double": self.current_q_index in self.double_rounds,  # vòng Double HP
            "paused": self.paused,
        }

    def public_state(self) -> dict:
        """Trạng thái cho người chơi — KHÔNG có đáp án."""
        return self._base_state(include_answer=False)

    def admin_state(self) -> dict:
        """Trạng thái cho admin — CÓ đáp án + dòng sự kiện tức thời + thống kê đáp án."""
        base = self._base_state(include_answer=True)
        base["action_log"] = self.action_log[-40:]
        base["answer_stats"] = {str(k): v for k, v in self.answer_stats.items()}
        return base

    def private_state(self, player_id: str) -> dict:
        """Trạng thái riêng tư cho 1 người chơi — KHÔNG có đáp án."""
        base = self._base_state(include_answer=False, player_id=player_id)
        base["round_log"] = _scrub_attackers(base.get("round_log"))
        player = self.players.get(player_id)
        if player:
            me = player.to_private_dict()
            if me.get("delay_from"):
                me["delay_from"] = ANON_ATTACKER
            # Đóng băng đếm lùi trừ thời gian khi phòng tạm dừng
            if player.delay_until:
                me["delay_remaining"] = max(0.0, round((player.delay_until - self._now()).total_seconds(), 1))
            base["me"] = me
        return base



# ------------------------------------------------------------------
# Giấu danh tính người ra đòn trong dữ liệu gửi cho NGƯỜI CHƠI.
# Người chơi chỉ thấy "một ai đó" — tên kẻ tấn công không rời khỏi server.
# Màn hình quản trị (admin_state) vẫn giữ đầy đủ tên để giáo viên theo dõi.
# ------------------------------------------------------------------
ANON_ATTACKER = "?"
_ATTACKER_KEYS = ("attacker", "attacker_team", "attacker_id")


def _scrub_attackers(round_log: list) -> list:
    """Trả về bản sao round_log đã xóa mọi thông tin nhận dạng kẻ tấn công."""
    cleaned = []
    for rnd in round_log or []:
        r = dict(rnd)
        evs = []
        for ev in r.get("events", []) or []:
            e = dict(ev)
            for k in _ATTACKER_KEYS:
                if k in e:
                    e[k] = ANON_ATTACKER if k == "attacker" else ""
            evs.append(e)
        r["events"] = evs
        cleaned.append(r)
    return cleaned


# ==================================================================
# THƯỞNG TỐC ĐỘ THEO BLOCK THỜI GIAN
# ==================================================================
# Trả lời càng nhanh điểm càng cao. Thời gian trả lời được chia thành các
# block bằng nhau; mỗi block trôi qua thì thưởng giảm 5 điểm (20→15→10→5→0).
#
# Người bị TRỪ THỜI GIAN (bị hoãn hiện câu hỏi) không bị thiệt: block được
# chia theo phần thời gian họ THỰC SỰ có để trả lời, và đồng hồ chỉ bắt đầu
# chạy từ lúc câu hỏi hiện ra với họ.

SPEED_BLOCKS = 4          # số block khi câu hỏi có giới hạn thời gian
SPEED_BASE = 20.0         # thưởng của block đầu tiên
SPEED_STEP = 5.0          # mỗi block sau giảm bấy nhiêu điểm
SPEED_FREE_BLOCK = 12.0   # độ dài 1 block khi phòng không giới hạn thời gian


def _answer_delay(room: "Room", player: "Player") -> float:
    """Số giây người chơi bị hoãn hiện câu hỏi ở vòng này (0 nếu không bị trừ)."""
    if not player.delay_until or not room.question_start_time:
        return 0.0
    return max(0.0, (player.delay_until - room.question_start_time).total_seconds())


def speed_blocks(room: "Room", player: "Player") -> dict:
    """Mô tả thang điểm tốc độ của riêng người chơi này ở câu hiện tại."""
    delay = _answer_delay(room, player)
    if room.time_limit > 0:
        window = max(1.0, room.time_limit - delay)
        block_size = window / SPEED_BLOCKS
        blocks = SPEED_BLOCKS
    else:
        window = 0.0
        block_size = SPEED_FREE_BLOCK
        blocks = int(SPEED_BASE // SPEED_STEP)
    return {
        "delay": round(delay, 1),
        "window": round(window, 1),
        "block_size": round(block_size, 1),
        "blocks": blocks,
        "base": SPEED_BASE,
        "step": SPEED_STEP,
    }


def _speed_bonus(room: "Room", player: "Player") -> tuple:
    """Trả về (điểm thưởng tốc độ, chỉ số block bắt đầu từ 1, 0 nếu hết giờ)."""
    if not room.question_start_time:
        return 0.0, 0
    delay = _answer_delay(room, player)
    answer_time = max(0.0, (room._now() - room.question_start_time).total_seconds() - delay)

    if room.time_limit > 0:
        window = max(1.0, room.time_limit - delay)   # thời gian thật sự để trả lời
        if answer_time >= window:
            return 0.0, 0                            # quá giờ, không còn thưởng
        block_size = window / SPEED_BLOCKS
        block = min(SPEED_BLOCKS - 1, int(answer_time // block_size))
    else:
        block = int(answer_time // SPEED_FREE_BLOCK)

    bonus = SPEED_BASE - SPEED_STEP * block
    if bonus <= 0:
        return 0.0, 0
    return round(bonus, 1), block + 1


# ==================================================================
# ROOM REGISTRY (in-memory)
# ==================================================================

_rooms: dict[str, Room] = {}
_rooms_lock = threading.Lock()


def get_room(room_id: str) -> Optional[Room]:
    room = _rooms.get(room_id)
    if room is None:
        return None
    # Lazy TTL cleanup
    age = (datetime.utcnow() - room.created_at).total_seconds()
    if age > ROOM_TTL_SECONDS:
        delete_room(room_id)
        return None
    return room


def create_room(questions: list[Question], time_limit: int = 0) -> Room:
    room_id = uuid.uuid4().hex[:8].upper()
    room = Room(room_id, questions, time_limit=time_limit)
    with _rooms_lock:
        _rooms[room_id] = room
    return room


def delete_room(room_id: str):
    with _rooms_lock:
        _rooms.pop(room_id, None)


# ==================================================================
# QUESTION PARSER
# ==================================================================

def _parse_text(raw: str) -> list[Question]:
    """
    Phân tích văn bản câu hỏi. Hỗ trợ các định dạng:
      - "Câu 1: Nội dung?"  /  "Câu 1. ..."  /  "Câu 1 ..."
      - "1. Nội dung?"  /  "1) ..."
      Đáp án: A/B/C/D (có thể kèm . ) : sau chữ cái)
      Đáp án đúng đánh dấu bằng dấu * trước chữ cái: *A. / *A)
    """
    questions = []
    lines = [l.strip() for l in raw.splitlines()]

    question_text = ""
    options: dict[str, str] = {}
    answer = ""

    # Dòng đáp án: [*][ABCD] theo sau bởi .). hoặc khoảng trắng rồi text
    opt_re = re.compile(r'^(\*?)([ABCD])[.):\s]\s*(.*)', re.IGNORECASE)
    # Dòng câu hỏi: "Câu 1" / "Câu 1." / "Câu 1:" / "1." / "1)"
    q_num_re = re.compile(
        r'^(?:c[aâ]u\s+\d+|question\s+\d+|\d+)[.):\s]\s*(.*)',
        re.IGNORECASE
    )
    # "Câu 1" đứng một mình (không có text kèm theo)
    q_alone_re = re.compile(r'^(?:c[aâ]u\s+\d+|question\s+\d+|\d+)\s*$', re.IGNORECASE)

    def flush():
        nonlocal question_text, options, answer
        if question_text and options and answer:
            questions.append(Question(question_text.strip(), dict(options), answer.upper()))
        question_text = ""
        options = {}
        answer = ""

    for line in lines:
        if not line:
            continue

        m_opt = opt_re.match(line)
        if m_opt:
            star, letter, text = m_opt.groups()
            letter = letter.upper()
            options[letter] = text.strip()
            if star:
                answer = letter
            continue

        # "Câu 1" đứng một mình → flush câu trước, bắt đầu câu mới (text ở dòng tiếp)
        if q_alone_re.match(line):
            flush()
            question_text = ""
            continue

        m_q = q_num_re.match(line)
        if m_q:
            flush()
            question_text = m_q.group(1).strip()
            continue

        # Dòng tiếp theo của câu hỏi (nếu câu hỏi chưa có đáp án)
        if not options:
            if question_text:
                question_text += " " + line
            else:
                question_text = line

    flush()
    return questions


def _parse_html_mammoth(html_content: str) -> list[Question]:
    """
    Phân tích câu hỏi từ HTML đầu ra của mammoth.
    Hệ thống <p> là dòng, hình ảnh được giữ nguyên dưới dạng base64 <img>.
    """
    import re as _re

    def strip_tags(s: str) -> str:
        return _re.sub(r'<[^>]+>', '', s)

    # Xóa thẻ nguy hiểm
    html_content = _re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=_re.DOTALL | _re.IGNORECASE)
    html_content = _re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=_re.DOTALL | _re.IGNORECASE)

    # Tách HTML thành các "token": <p>...</p> hoặc <img .../> standalone
    # Ảnh nằm ngoài <p> vẫn được xử lý
    tokens_raw = _re.findall(r'(<p[^>]*>.*?</p>|<img\s[^>]*/?>)', html_content, _re.DOTALL | _re.IGNORECASE)
    if not tokens_raw:
        tokens_raw = _re.split(r'<br\s*/?>', html_content)

    # Mỗi item: (para_html, is_img)
    paras = []
    for tok in tokens_raw:
        if _re.match(r'<img\s', tok, _re.IGNORECASE):
            paras.append((tok, True))
        else:
            inner = _re.sub(r'^<p[^>]*>|</p>$', '', tok, flags=_re.IGNORECASE | _re.DOTALL)
            paras.append((inner, False))

    opt_re = _re.compile(r'^(\*?)([ABCD])[.):\s]\s*(.*)', _re.IGNORECASE | _re.DOTALL)
    q_num_re = _re.compile(r'^(?:c[a\xc3\xa2u]\s+\d+|c\u00e2u\s+\d+|question\s+\d+|\d+)[.):\s]\s*(.*)', _re.IGNORECASE | _re.DOTALL)
    q_alone_re = _re.compile(r'^(?:c[a\xc3\xa2u]\s+\d+|c\u00e2u\s+\d+|question\s+\d+|\d+)\s*$', _re.IGNORECASE)

    questions = []
    question_html = ""
    options: dict = {}
    answer = ""

    def flush():
        nonlocal question_html, options, answer
        if question_html.strip() and options and answer:
            questions.append(Question(question_html.strip(), dict(options), answer.upper(), is_html=True))
        question_html, options, answer = "", {}, ""

    for para_html, is_img in paras:
        # Ảnh standalone: gắn vào question_html đang xây dựng (hoặc bỏ qua nếu chưa có câu hỏi)
        if is_img:
            if question_html:  # ảnh thuộc câu hỏi đang mở
                question_html += para_html
            continue

        plain = strip_tags(para_html).strip()
        if not plain:
            continue

        m_opt = opt_re.match(plain)
        if m_opt:
            star, letter, opt_plain = m_opt.groups()
            letter = letter.upper()
            # Xóa MỌI prefix lặp lại "A. A. text" → "text"
            opt_plain_clean = _re.sub(r'^(\*?[ABCD][.):\s]\s*)+', '', opt_plain, flags=_re.IGNORECASE).strip()
            # Tính số ký tự plain-text cần bỏ qua trong HTML
            chars_to_skip = len(plain) - len(opt_plain_clean)
            # Bước qua tokens HTML, bỏ qua đúng chars_to_skip ký tự text
            tokens = _re.split(r'(<[^>]+>)', para_html)
            out_tokens = []
            skipped = 0
            for tok in tokens:
                if tok.startswith('<'):
                    out_tokens.append(tok)
                elif skipped < chars_to_skip:
                    skip_now = min(chars_to_skip - skipped, len(tok))
                    skipped += skip_now
                    rest = tok[skip_now:]
                    if rest:
                        out_tokens.append(rest)
                else:
                    out_tokens.append(tok)
            opt_html = ''.join(out_tokens).strip() or opt_plain_clean
            options[letter] = opt_html
            if star:
                answer = letter
            continue

        if q_alone_re.match(plain):
            flush()
            question_html = ""
            continue

        m_q = q_num_re.match(plain)
        if m_q:
            flush()
            q_html = _re.sub(r'^(?:c[\u00e2a]u\s+\d+|question\s+\d+|\d+)[.):\s]\s*', '', para_html.strip(), flags=_re.IGNORECASE, count=1)
            question_html = q_html
            continue

        if not options:
            if question_html:
                question_html += " " + para_html
            else:
                question_html = para_html

    flush()
    return questions


def parse_questions_from_file(file_storage) -> list[Question]:
    """
    Nhận flask.request.files object.
    Hỗ trợ: .txt, .doc (plain text), .docx (python-docx).
    Trả về list[Question].
    """
    filename = (file_storage.filename or "").lower()
    raw_text = ""

    if filename.endswith(".docx") and DOCX_AVAILABLE:
        # --- Thử mammoth trước: giữ hình ảnh và công thức ---
        try:
            import mammoth as _mammoth
            import base64 as _b64

            def _img_handler(image):
                with image.open() as img_stream:
                    data = _b64.b64encode(img_stream.read()).decode()
                return {"src": f"data:{image.content_type};base64,{data}"}

            file_storage.stream.seek(0)
            result = _mammoth.convert_to_html(
                file_storage.stream,
                convert_image=_mammoth.images.img_element(_img_handler)
            )
            html_out = result.value
            qs = _parse_html_mammoth(html_out)
            if qs:
                return qs
            # mammoth parse không ra câu hỏi → fallback python-docx
        except ImportError:
            pass  # mammoth chưa cài → fallback
        except Exception:
            pass  # lỗi khác → fallback

        # --- Fallback python-docx ---
        file_storage.stream.seek(0)
        try:
            doc = docx.Document(file_storage.stream)
            raw_text = "\n".join(p.text for p in doc.paragraphs)
        except (KeyError, Exception):
            # Fallback: đọc document.xml trực tiếp từ zip, nhóm theo đoạn <w:p>
            import zipfile as _zf, re as _re, io as _io
            file_storage.stream.seek(0)
            data = file_storage.stream.read()
            with _zf.ZipFile(_io.BytesIO(data)) as zf:
                xml_bytes = zf.read("word/document.xml")
            xml_str = xml_bytes.decode("utf-8", errors="ignore")
            # Nhóm text theo từng đoạn văn <w:p>
            paragraphs = _re.findall(r'<w:p[ >].*?</w:p>', xml_str, _re.DOTALL)
            lines = []
            for para in paragraphs:
                texts = _re.findall(r'<w:t[^>]*>([^<]*)</w:t>', para)
                line = "".join(texts).strip()
                if line:
                    lines.append(line)
            raw_text = "\n".join(lines)
    elif filename.endswith(".docx") and not DOCX_AVAILABLE:
        raise ValueError("Thư viện python-docx chưa được cài. Hãy dùng file .txt hoặc chạy: pip install python-docx")
    else:
        # .txt, .doc (plain text), hoặc bất kỳ
        raw_bytes = file_storage.read()
        for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
            try:
                raw_text = raw_bytes.decode(enc)
                break
            except UnicodeDecodeError:
                continue

    questions = _parse_text(raw_text)
    if not questions:
        raise ValueError(
            "Không tìm thấy câu hỏi hợp lệ trong file.\n"
            "Định dạng hỗ trợ:\n"
            "  1. Câu hỏi?       hoặc   Câu 1. Câu hỏi?\n"
            "  A. Lựa chọn 1\n"
            "  B. Lựa chọn 2\n"
            "  *C. Đáp án đúng   (dấu * trước đáp án đúng)\n"
            "  D. Lựa chọn 4\n"
            "Đảm bảo file lưu dạng UTF-8 hoặc có đủ 4 lựa chọn A-D."
        )
    return questions


# ==================================================================
# PLAYER MANAGEMENT
# ==================================================================

def _check_name_available(room: "Room", name: str) -> tuple[bool, str]:
    """
    Kiểm tra xem tên có khả dụng không.
    Trả về: (is_available, error_message)
    """
    if not name or not name.strip():
        return False, "Tên không được để trống"
    
    name = name.strip()
    used_names = {p.name.lower() for p in room.players.values()}
    
    if name.lower() in used_names:
        return False, f"Tên '{name}' đã được sử dụng. Vui lòng chọn tên khác."
    
    return True, ""

def join_room(room_id: str, name: str, player_id: Optional[str] = None,
              avatar: str = "") -> dict:
    """
    Người chơi tham gia phòng, hoặc THAM GIA LẠI (rejoin) sau khi thoát.
    Thứ tự ưu tiên:
      1. Có player_id đã lưu và còn trong phòng → lấy lại đúng nhân vật đó.
      2. Trùng tên với người đã có:
         - Đang trong game/kết thúc → cho rejoin (kết nối lại).
         - Đang ở lobby → báo lỗi trùng tên (tránh 2 người giành tên).
      3. Tên mới hợp lệ, phòng đang lobby → tạo nhân vật mới.
    Trả về:
      success: {"player_id": str, "name": str, "rejoin": bool}
      error: {"error": str}
    """
    room = get_room(room_id)
    if not room:
        return {"error": "Phòng không tồn tại"}

    # (1) Rejoin bằng player_id đã lưu (ưu tiên, không phụ thuộc tên)
    if player_id and player_id in room.players:
        p = room.players[player_id]
        if avatar:
            p.avatar = _clean_avatar(avatar)
        return {"player_id": p.player_id, "name": p.name, "avatar": p.avatar, "rejoin": True}

    name = (name or "").strip()
    if not name:
        return {"error": "Tên không được để trống"}

    # (2) Trùng tên với người đã có trong phòng
    existing = next((p for p in room.players.values() if p.name.lower() == name.lower()), None)
    if existing:
        if room.state != "lobby":
            # Đang chơi/kết thúc → coi như kết nối lại nhân vật cùng tên
            return {"player_id": existing.player_id, "name": existing.name,
                    "avatar": existing.avatar, "rejoin": True}
        # Lobby → không cho 2 người giành cùng tên
        return {"error": f"Tên '{name}' đã được sử dụng. Vui lòng chọn tên khác."}

    # (3) Tên mới
    if room.state != "lobby":
        return {"error": "Phòng đang trong game, không thể tham gia"}

    with room.lock:
        new_id = uuid.uuid4().hex[:12]
        player = Player(new_id, name)
        player.avatar = _clean_avatar(avatar)
        room.players[new_id] = player

    return {"player_id": player.player_id, "name": player.name,
            "avatar": player.avatar, "rejoin": False}


def set_player_ready(room_id: str, player_id: str) -> bool:
    room = get_room(room_id)
    if not room:
        return False
    player = room.players.get(player_id)
    if not player:
        return False
    player.ready = True
    return True


# ==================================================================
# GAME FLOW
# ==================================================================

def start_game(room_id: str) -> bool:
    """Admin bắt đầu game. Trả về True nếu thành công."""
    room = get_room(room_id)
    if not room or room.state != "lobby":
        return False
    if len(room.players) < 1:
        return False
    with room.lock:
        room.state = "running"
        room.current_q_index = 0
        room.question_start_time = datetime.utcnow()
        # Chọn ngẫu nhiên ~25% số câu làm vòng "Double HP"
        room.double_rounds = {i for i in range(len(room.questions)) if random.random() < 0.25}
        _reset_round(room)
    return True


def _reset_round(room: Room):
    """Reset trạng thái mỗi vòng: current_action = None, answered = False, eliminate_options = []."""
    # Xoá trạng thái ẩn mình đã hết hạn (active khi current_q_index < hide_expires_at_round)
    for p in room.players.values():
        if p.hide_expires_at_round is not None and room.current_q_index >= p.hide_expires_at_round:
            p.hide_active = False
            p.hide_expires_at_round = None
    # Bắt đầu gom sự kiện của vòng mới + chụp HP đầu vòng
    room.current_round_events = []
    room.hp_at_round_start = {p.player_id: round(p.hp, 1) for p in room.players.values()}
    for p in room.alive_players():
        p.current_action = None
        p.answered_current = False
        p.eliminate_options = []
        p.skill_options = []       # lựa chọn kỹ năng chỉ có khi trả lời đúng vòng này
        p.counter_active = False   # phản đòn chỉ tồn tại trong vòng được chọn


def _import_skill_for_correct(room: Room, player_id: str) -> str:
    """
    Khi trả lời đúng → tặng kỹ năng ngẫu nhiên (hoặc theo cycle).
    Đơn giản: round-robin qua 6 kỹ năng theo thứ tự idx câu hỏi.
    """
    import random
    skill_keys = list(SKILLS.keys())
    key = random.choice(skill_keys)
    return key


def submit_answer(room_id: str, player_id: str, selected: str) -> dict:
    """
    Người chơi nộp đáp án. Trả về:
      {"correct": bool, "skill_gained": str|None, "correct_answer": str}
    """
    room = get_room(room_id)
    if not room or room.state != "running":
        return {"error": "room_not_running"}

    player = room.players.get(player_id)
    if not player:
        return {"error": "player_not_found"}

    if player.answered_current:
        return {"error": "already_answered"}

    q = room.current_question()
    if not q:
        return {"error": "no_question"}

    mult = 2 if room.current_q_index in room.double_rounds else 1  # vòng Double HP

    with room.lock:
        player.answered_current = True
        sel = (selected or "").upper()
        correct = (sel == q.answer.upper())
        skill_gained = None
        hp_gain = 0.0
        speed_bonus = 0.0
        speed_block = 0

        # Ghi nhận thống kê đáp án cho câu này
        stats = room.answer_stats.setdefault(
            room.current_q_index, {"A": 0, "B": 0, "C": 0, "D": 0, "correct": 0, "total": 0}
        )
        if sel in stats:
            stats[sel] += 1
        stats["total"] += 1

        if correct:
            stats["correct"] += 1
            # Tăng chuỗi trả lời đúng liên tiếp
            player.correct_streak += 1
            player.correct_count += 1
            # Mỗi vòng: tặng 3 kỹ năng ngẫu nhiên để chọn 1
            player.skill_options = random.sample(list(SKILLS.keys()), 3)
            skill_gained = None
            # Thưởng tốc độ theo block thời gian (xem _speed_bonus)
            speed_bonus, speed_block = _speed_bonus(room, player)
            # Cộng máu: (chuỗi×5 + thưởng tốc độ), rồi ×2 nếu vòng Double HP
            hp_gain = (player.correct_streak * 5.0 + speed_bonus) * mult
            player.hp = player.hp + hp_gain
        else:
            # Trừ HP khi sai (×2 nếu vòng Double HP)
            penalty = 5.0 * mult
            player.hp = max(0.0, player.hp - penalty)
            hp_gain = -penalty
            player.correct_streak = 0
            player.current_action = {"skill": "skip", "target": None}

    return {
        "correct": correct,
        "correct_answer": q.answer,
        "skill_options": [{**SKILLS[k], "skill": k} for k in player.skill_options],
        "hp_gain": hp_gain,
        "hp": round(player.hp, 1),
        "streak": player.correct_streak,
        "speed_bonus": speed_bonus,
        "speed_block": speed_block,
        "speed_blocks": speed_blocks(room, player),
        "is_double": mult == 2,
    }


def submit_action(room_id: str, player_id: str, skill: Optional[str], target_id: Optional[str]) -> dict:
    """
    Người chơi chọn dùng kỹ năng (hoặc bỏ qua).
    skill=None hoặc skill="skip" → bỏ qua.
    """
    room = get_room(room_id)
    if not room or room.state != "running":
        return {"error": "room_not_running"}

    player = room.players.get(player_id)
    if not player:
        return {"error": "player_not_found"}

    if player.current_action is not None:
        return {"error": "already_submitted_action"}

    with room.lock:
        if not skill or skill == "skip":
            player.current_action = {"skill": "skip", "target": None}
        else:
            # Kỹ năng phải nằm trong 3 lựa chọn được tặng vòng này
            if skill not in player.skill_options:
                return {"error": "skill_not_owned"}
            # Kiểm tra target nếu cần
            needs_target = skill in ("attack", "double", "balance", "time_steal")
            if needs_target and not target_id:
                return {"error": "target_required"}
            player.current_action = {"skill": skill, "target": target_id}
            # Áp dụng hiệu ứng NGAY + đẩy vào action_log để admin phát hoạt ảnh tức thời
            events = _apply_single_action(room, player, player.current_action)
            player.skill_options = []  # đã chọn → bỏ các lựa chọn còn lại
            room.current_round_events.extend(events)
            for ev in events:
                _push_action_log(room, ev)

        # Khi tất cả đã submit → kết thúc vòng → vào result_phase 2 giây
        if _all_alive_submitted(room):
            _finalize_round(room)
            room.result_phase = True
            room.result_phase_until = datetime.utcnow() + timedelta(seconds=2)

    return {"ok": True, "all_submitted": _all_alive_submitted_safe(room)}


def _all_alive_submitted(room: Room) -> bool:
    return all(p.current_action is not None for p in room.alive_players())


def _all_alive_submitted_safe(room: Room) -> bool:
    """Đọc an toàn ngoài lock."""
    try:
        return all(p.current_action is not None for p in room.alive_players())
    except Exception:
        return False


def _push_action_log(room: Room, ev: dict):
    """Đẩy 1 sự kiện vào dòng action_log (kèm seq + HP hiện tại) để admin phát hoạt ảnh ngay."""
    room._action_seq += 1
    entry = dict(ev)
    entry["seq"] = room._action_seq
    entry["round"] = room.current_q_index + 1
    entry["hp_after"] = {p.player_id: round(p.hp, 1) for p in room.players.values()}
    room.action_log.append(entry)
    if len(room.action_log) > 80:
        room.action_log = room.action_log[-80:]


def _apply_single_action(room: Room, player: "Player", action: dict) -> list:
    """
    Áp dụng NGAY hiệu ứng của MỘT hành động (giải quyết tuần tự theo thứ tự bấm).
    Trả về danh sách sự kiện đã phát sinh.
    """
    events = []
    skill = action["skill"]
    target_id = action.get("target")
    target = room.players.get(target_id) if target_id else None
    alive = room.alive_players()
    mult = 2 if room.current_q_index in room.double_rounds else 1  # vòng Double HP

    def deal_damage(attacker: "Player", tgt: "Player", dmg: float, skill_used: str):
        if tgt.hide_active:
            events.append({"type": "evade", "attacker": attacker.name, "target": tgt.name, "dmg": dmg})
            return
        if tgt.has_counter():
            tgt.counter_active = False  # phản đòn dùng 1 lần
            if attacker.hp > 0:
                attacker.hp = max(0.0, attacker.hp - dmg)
            events.append({"type": "counter", "attacker": attacker.name, "target": tgt.name, "dmg": dmg})
        else:
            if tgt.hp > 0:
                tgt.hp = max(0.0, tgt.hp - dmg)
            events.append({"type": "damage", "attacker": attacker.name, "target": tgt.name, "dmg": dmg, "skill": skill_used})

    if skill == "heal":
        player.hp = player.hp + 10.0 * mult
        events.append({"type": "heal", "player": player.name, "amount": 10 * mult})

    elif skill == "attack":
        if target and target.alive:
            deal_damage(player, target, 10.0 * mult, "attack")

    elif skill == "double":
        if target and target.alive:
            deal_damage(player, target, 15.0 * mult, "double")

    elif skill == "aoe":
        for other in alive:
            if other.player_id == player.player_id:
                continue
            deal_damage(player, other, 5.0 * mult, "aoe")

    elif skill == "balance":
        player.hp = player.hp + 5.0 * mult
        events.append({"type": "heal", "player": player.name, "amount": 5 * mult})
        if target and target.alive:
            deal_damage(player, target, 5.0 * mult, "balance")

    elif skill == "counter":
        player.counter_active = True
        events.append({"type": "set_counter", "player": player.name})

    elif skill == "eliminate":
        player.eliminate_next = True
        events.append({"type": "eliminate", "player": player.name})

    elif skill == "time_steal":
        if target and target.alive:
            # Vòng kế tiếp của mục tiêu sẽ bị hoãn hiện câu hỏi 15s (đếm lùi trên màn hình họ)
            target.pending_delay += 15.0
            target.pending_delay_from = player.name
            events.append({"type": "time_steal", "attacker": player.name, "target": target.name, "time_deducted": 15})

    elif skill == "time_bomb":
        bomb_amt = round(room.time_limit * 0.15, 1)
        for other in alive:
            if other.player_id != player.player_id:
                other.pending_delay += bomb_amt
                other.pending_delay_from = player.name
        events.append({
            "type": "time_bomb",
            "attacker": player.name,
            "affected_count": len([p for p in alive if p.player_id != player.player_id]),
            "time_deducted": bomb_amt,
            "percent": 15,
        })

    elif skill == "hide":
        player.hide_active = True
        player.hide_expires_at_round = room.current_q_index + 2
        events.append({"type": "hide", "player": player.name})

    # Chuẩn hóa HP (0% vẫn tiếp tục chơi)
    for p in room.players.values():
        if p.hp <= 0:
            p.hp = 0.0
        p.alive = True

    return events


def _finalize_round(room: Room):
    """Kết thúc vòng: gom sự kiện vào round_log (cho màn kết quả người chơi)."""
    hp_before = room.hp_at_round_start or {p.player_id: round(p.hp, 1) for p in room.players.values()}
    room.round_log.append({
        "round": room.current_q_index + 1,
        "events": list(room.current_round_events),
        "hp_before": hp_before,
        "hp_after": {p.player_id: round(p.hp, 1) for p in room.players.values()},
        "player_names": {p.player_id: p.name for p in room.players.values()},
    })


def _advance_round(room: Room):
    """Chuyển sang câu hỏi tiếp theo hoặc kết thúc game."""
    room.current_q_index += 1

    # Kiểm tra kết thúc
    if room.current_q_index >= len(room.questions):
        room.state = "finished"
        return

    room.question_start_time = datetime.utcnow()

    # Kích hoạt "trừ thời gian" = hoãn hiện câu hỏi cho người bị trừ ở vòng này
    for p in room.players.values():
        if p.pending_delay > 0:
            p.delay_until = room.question_start_time + timedelta(seconds=p.pending_delay)
            p.delay_from = p.pending_delay_from
        else:
            p.delay_until = None
            p.delay_from = ""
        p.pending_delay = 0.0
        p.pending_delay_from = ""

    _reset_round(room)

    # Sau khi reset, tính eliminate_options cho người có buff eliminate_next
    q = room.current_question()
    if q:
        wrong_opts = [k for k in q.options if k != q.answer]
        for p in room.players.values():
            if p.eliminate_next:
                p.eliminate_options = random.sample(wrong_opts, min(2, len(wrong_opts)))
                p.eliminate_next = False


# ==================================================================
# TẠM DỪNG / TIẾP TỤC (đóng băng đồng hồ cả phòng)
# ==================================================================

def pause_game(room_id: str) -> dict:
    room = get_room(room_id)
    if not room or room.state != "running":
        return {"error": "room_not_running"}
    if not room.paused:
        room.paused = True
        room.paused_at = datetime.utcnow()
    return {"ok": True, "paused": room.paused}


def resume_game(room_id: str) -> dict:
    room = get_room(room_id)
    if not room or room.state != "running":
        return {"error": "room_not_running"}
    if room.paused and room.paused_at:
        delta = datetime.utcnow() - room.paused_at
        # Dời mọi mốc thời gian để đồng hồ tiếp tục đúng chỗ đã dừng
        if room.question_start_time:
            room.question_start_time += delta
        if room.result_phase_until:
            room.result_phase_until += delta
        for p in room.players.values():
            if p.delay_until:
                p.delay_until += delta
    room.paused = False
    room.paused_at = None
    return {"ok": True, "paused": False}


# ==================================================================
# ÔN TẬP (xem lại câu hỏi + thống kê đáp án sau khi chơi)
# ==================================================================

def get_review(room_id: str) -> dict:
    room = get_room(room_id)
    if not room:
        return {"error": "room_not_found"}
    items = []
    for i, q in enumerate(room.questions):
        st = room.answer_stats.get(i, {"A": 0, "B": 0, "C": 0, "D": 0, "correct": 0, "total": 0})
        items.append({
            "index": i,
            "text": q.text,
            "options": q.options,
            "answer": q.answer,
            "html": q.is_html,
            "stats": st,
        })
    return {"questions": items}


# ==================================================================
# ADMIN FORCE ADVANCE (nếu cần bỏ qua người chơi mất kết nối)
# ==================================================================

def admin_force_advance(room_id: str) -> dict:
    """Admin ép chuyển vòng, bỏ qua người chưa submit."""
    room = get_room(room_id)
    if not room or room.state != "running":
        return {"error": "room_not_running"}
    with room.lock:
        if room.result_phase:
            # Đang hiển thị kết quả → bỏ qua, chuyển câu ngay
            room.result_phase = False
            room.result_phase_until = None
            _advance_round(room)
        else:
            # Force skip người chưa submit (hiệu ứng của người đã dùng skill đã áp dụng ngay từ trước)
            for p in room.alive_players():
                if p.current_action is None:
                    p.current_action = {"skill": "skip", "target": None}
            _finalize_round(room)
            # Vào result_phase rồi skip luôn chứ không đợi 2 giây
            room.result_phase = False
            room.result_phase_until = None
            _advance_round(room)
    return {"ok": True}


def check_timeout(room_id: str):
    """Kiểm tra timeout: hết giờ câu hỏi → vào result_phase; result_phase hết → chuyển câu."""
    room = get_room(room_id)
    if not room or room.state != "running":
        return
    if room.paused:   # đóng băng mọi đồng hồ khi tạm dừng
        return

    # 1. Nếu đang result_phase → kiểm tra hết 5 giây → chuyển câu
    if room.result_phase and room.result_phase_until:
        if datetime.utcnow() >= room.result_phase_until:
            with room.lock:
                if room.result_phase and room.result_phase_until and datetime.utcnow() >= room.result_phase_until:
                    room.result_phase = False
                    room.result_phase_until = None
                    _advance_round(room)
        return

    # 2. Kiểm tra hết giờ câu hỏi
    if room.time_limit <= 0 or not room.question_start_time:
        return
    elapsed = (datetime.utcnow() - room.question_start_time).total_seconds()
    if elapsed < room.time_limit:
        return
    with room.lock:
        if room.state != "running" or room.result_phase:
            return
        if room.question_start_time and (datetime.utcnow() - room.question_start_time).total_seconds() < room.time_limit:
            return
        for p in room.alive_players():
            if p.current_action is None:
                p.current_action = {"skill": "skip", "target": None}
        _finalize_round(room)
        room.result_phase = True
        room.result_phase_until = datetime.utcnow() + timedelta(seconds=2)


# ==================================================================
# LEADERBOARD
# ==================================================================

def get_leaderboard(room_id: str) -> list[dict]:
    room = get_room(room_id)
    if not room:
        return []
    players = sorted(room.players.values(), key=lambda p: p.hp, reverse=True)
    return [
        {"rank": i + 1, "name": p.name, "hp": round(p.hp, 1), "alive": p.alive}
        for i, p in enumerate(players)
    ]
