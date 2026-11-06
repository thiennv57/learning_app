# -*- coding: utf-8 -*-
"""
Team Battle Game - Logic Backend (ĐỘC LẬP HOÀN TOÀN với attack_defense_game.py)

Chế độ chơi ĐỒNG ĐỘI:
  1. Admin tạo phòng (upload file hoặc chọn bộ câu hỏi) → room_id
  2. Người chơi vào phòng qua link /team-battle/play/<room_id>
  3. Admin chọn SỐ ĐỘI rồi nhấn Bắt đầu
     → người chơi được chia NGẪU NHIÊN vào các đội, số thành viên chênh nhau tối đa 1
  4. HP của đội = TỔNG HP các thành viên
  5. Tấn công vẫn nhắm vào TỪNG THÀNH VIÊN, nhưng CẤM đánh đồng đội
  6. Xếp hạng theo HP của ĐỘI

Module này KHÔNG sửa và KHÔNG ảnh hưởng tới attack_defense_game.py.
Chỉ dùng lại (read-only) bộ parser câu hỏi để tránh trùng lặp code.
"""

import uuid
import random
import threading
from datetime import datetime, timedelta
from typing import Optional

# Dùng lại parser câu hỏi (read-only, không sửa module cũ)
from attack_defense_game import Question, parse_questions_from_file  # noqa: F401

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


ROOM_TTL_SECONDS = 4 * 3600   # Phòng tự xóa sau 4 giờ
RESULT_PHASE_SECONDS = 2

# Bộ nhận diện đội (tên / màu / biểu tượng)
TEAM_PRESETS = [
    {"name": "Đội Đỏ",         "color": "#f85149", "emoji": "🔴"},
    {"name": "Đội Xanh Dương", "color": "#58a6ff", "emoji": "🔵"},
    {"name": "Đội Xanh Lá",    "color": "#3fb950", "emoji": "🟢"},
    {"name": "Đội Vàng",       "color": "#f0c050", "emoji": "🟡"},
    {"name": "Đội Tím",        "color": "#a371f7", "emoji": "🟣"},
    {"name": "Đội Cam",        "color": "#ff8c42", "emoji": "🟠"},
    {"name": "Đội Hồng",       "color": "#ff7eb6", "emoji": "🩷"},
    {"name": "Đội Ngọc",       "color": "#39c5cf", "emoji": "🩵"},
    {"name": "Đội Chàm",       "color": "#7c83fd", "emoji": "🔷"},
    {"name": "Đội Bạc",        "color": "#b1bac4", "emoji": "⚪"},
]

SKILLS = {
    "attack":     {"name": "⚔️ Tấn công",          "desc": "Chọn 1 thành viên đội khác, -10 điểm"},
    "heal":       {"name": "💊 Tăng máu",           "desc": "+10 điểm cho bản thân (tăng điểm đội)"},
    "counter":    {"name": "🛡️ Phản đòn",          "desc": "Phản lại đòn đánh vào mình trong vòng này"},
    "double":     {"name": "💥 Tấn công mạnh hơn",  "desc": "Chọn 1 thành viên đội khác, -15 điểm"},
    "aoe":        {"name": "🌪️ Tấn công toàn bộ",  "desc": "Toàn bộ thành viên các đội khác -5 điểm"},
    "balance":    {"name": "⚡ Công thủ toàn diện", "desc": "+5 điểm bản thân, đánh 1 người đội khác -5 điểm"},
    "eliminate":  {"name": "🔮 Loại bỏ gợi ý",     "desc": "Loại bỏ 2 phương án sai ở câu tiếp theo"},
    "time_steal": {"name": "⏱️ Cướp thời gian",    "desc": "Chọn 1 người đội khác, hoãn câu kế 15s"},
    "time_bomb":  {"name": "💣 Bom thời gian",     "desc": "Mọi thành viên đội khác bị hoãn câu kế"},
    "hide":       {"name": "👻 Ẩn mình",            "desc": "Ẩn khỏi tấn công ở vòng sau"},
}

TARGETED_SKILLS = ("attack", "double", "balance", "time_steal")


# ==================================================================
# CHIA ĐỘI
# ==================================================================

def suggest_team_count(n: int) -> int:
    """
    Gợi ý số đội TỐI ĐA mà mọi đội có số thành viên BẰNG NHAU (mỗi đội ≥ 2 người).
    n = 10 → 5 đội × 2 ; n = 9 → 3 đội × 3 ; n = 7 (nguyên tố) → 3 đội (3/2/2).
    """
    if n < 4:
        return 2 if n >= 2 else 1
    for size in range(2, n // 2 + 1):
        if n % size == 0:
            return n // size
    # n nguyên tố → không chia đều tuyệt đối được, lấy số đội lớn nhất với tối thiểu 2 người
    return max(2, n // 2)


def team_count_options(n: int) -> list[dict]:
    """Danh sách số đội hợp lệ kèm mô tả cách chia, cho admin chọn."""
    opts = []
    for k in range(2, n + 1):
        base, rem = divmod(n, k)
        if base < 1:
            break
        sizes = [base + 1] * rem + [base] * (k - rem)
        opts.append({
            "count": k,
            "sizes": sizes,
            "even": rem == 0,
            "label": f"{k} đội" + (f" × {base} người" if rem == 0
                                   else " (" + " / ".join(map(str, sizes)) + ")"),
        })
    return opts


def _split_player_ids(player_ids: list, team_count: int) -> list:
    """Xáo trộn rồi chia round-robin → số thành viên chênh nhau tối đa 1."""
    ids = list(player_ids)
    random.shuffle(ids)
    buckets = [[] for _ in range(team_count)]
    for i, pid in enumerate(ids):
        buckets[i % team_count].append(pid)
    return buckets


# ==================================================================
# DATA MODELS
# ==================================================================

class Team:
    def __init__(self, team_id: str, preset: dict):
        self.team_id = team_id
        self.name = preset["name"]
        self.color = preset["color"]
        self.emoji = preset["emoji"]
        self.member_ids: list = []

    def hp(self, room: "TeamRoom") -> float:
        return sum(room.players[pid].hp for pid in self.member_ids if pid in room.players)

    def max_hp(self) -> float:
        """HP khởi điểm của đội = 100 × số thành viên (mốc để vẽ thanh HP)."""
        return 100.0 * max(1, len(self.member_ids))

    def to_dict(self, room: "TeamRoom") -> dict:
        members = [room.players[pid] for pid in self.member_ids if pid in room.players]
        members.sort(key=lambda p: p.hp, reverse=True)
        total = sum(p.hp for p in members)
        return {
            "team_id": self.team_id,
            "name": self.name,
            "color": self.color,
            "emoji": self.emoji,
            "hp": round(total, 1),
            "max_hp": round(self.max_hp(), 1),
            "member_count": len(members),
            "avg_hp": round(total / len(members), 1) if members else 0.0,
            "members": [p.to_public_dict(room) for p in members],
        }


class Player:
    def __init__(self, player_id: str, name: str):
        self.player_id = player_id
        self.name = name
        self.hp = 100.0
        self.ready = False
        self.team_id: Optional[str] = None
        # 3 kỹ năng ngẫu nhiên được tặng mỗi vòng khi trả lời đúng
        self.skill_options: list = []
        self.counter_active: bool = False
        self.current_action: Optional[dict] = None
        self.answered_current: bool = False
        self.alive: bool = True
        self.eliminate_next: bool = False
        self.eliminate_options: list = []
        self.avatar: str = "boy_short"   # Nhân vật người chơi tự chọn
        self.correct_streak: int = 0
        self.correct_count: int = 0   # Tổng số câu đúng = số rào đã nhảy qua
        self.hide_active: bool = False
        self.hide_expires_at_round: Optional[int] = None
        self.pending_delay: float = 0.0
        self.pending_delay_from: str = ""
        self.delay_until: Optional[datetime] = None
        self.delay_from: str = ""

    def to_public_dict(self, room: "TeamRoom" = None):
        d = {
            "player_id": self.player_id,
            "name": self.name,
            "avatar": self.avatar,
            "hp": round(self.hp, 1),
            "alive": self.alive,
            "ready": self.ready,
            "hide_active": self.hide_active,
            "correct_streak": self.correct_streak,
            "correct_count": self.correct_count,
            "team_id": self.team_id,
            "team_name": "",
            "team_color": "#8b949e",
            "team_emoji": "",
        }
        if room and self.team_id and self.team_id in room.teams:
            t = room.teams[self.team_id]
            d["team_name"] = t.name
            d["team_color"] = t.color
            d["team_emoji"] = t.emoji
        return d

    def to_private_dict(self, room: "TeamRoom"):
        return {
            **self.to_public_dict(room),
            "skills": [{**SKILLS[k], "skill": k} for k in self.skill_options],
            "current_action": self.current_action,
            "answered_current": self.answered_current,
            "eliminate_options": self.eliminate_options,
            "delay_remaining": (
                max(0.0, round((self.delay_until - datetime.utcnow()).total_seconds(), 1))
                if self.delay_until else 0.0
            ),
            "delay_from": self.delay_from,
        }

    def has_counter(self) -> bool:
        return self.counter_active


class TeamRoom:
    def __init__(self, room_id: str, questions: list, time_limit: int = 0):
        self.room_id = room_id
        self.questions = questions
        self.players: dict = {}
        self.teams: dict = {}
        self.team_order: list = []
        self.state = "lobby"          # lobby | running | finished
        self.current_q_index = -1
        self.lock = threading.Lock()
        self.created_at = datetime.utcnow()
        self.time_limit = time_limit
        self.question_start_time: Optional[datetime] = None
        self.round_log: list = []
        self.action_log: list = []
        self._action_seq: int = 0
        self.current_round_events: list = []
        self.hp_at_round_start: dict = {}
        self.result_phase: bool = False
        self.result_phase_until: Optional[datetime] = None
        self.time_penalties: dict = {}
        self.double_rounds: set = set()
        self.answer_stats: dict = {}
        self.paused: bool = False
        self.paused_at: Optional[datetime] = None

    # ------ helpers ------

    def alive_players(self) -> list:
        return [p for p in self.players.values() if p.alive]

    def enemies_of(self, player: Player) -> list:
        """Các người chơi còn sống KHÔNG cùng đội."""
        return [p for p in self.alive_players()
                if p.player_id != player.player_id and p.team_id != player.team_id]

    def same_team(self, a: Player, b: Player) -> bool:
        return a.team_id is not None and a.team_id == b.team_id

    def current_question(self):
        if 0 <= self.current_q_index < len(self.questions):
            return self.questions[self.current_q_index]
        return None

    def _now(self) -> datetime:
        return self.paused_at if (self.paused and self.paused_at) else datetime.utcnow()

    def get_time_remaining(self, player_id: str) -> Optional[float]:
        if not self.time_limit > 0 or not self.question_start_time \
                or self.state != "running" or self.result_phase:
            return None
        elapsed = (self._now() - self.question_start_time).total_seconds()
        penalty = self.time_penalties.get(player_id, 0.0)
        return max(0.0, round(self.time_limit - elapsed + penalty, 1))

    def teams_ranked(self) -> list:
        """Bảng xếp hạng ĐỘI theo tổng HP (cao → thấp)."""
        rows = [self.teams[tid].to_dict(self) for tid in self.team_order]
        rows.sort(key=lambda t: t["hp"], reverse=True)
        for i, r in enumerate(rows):
            r["rank"] = i + 1
        return rows

    def _base_state(self, include_answer: bool = False, player_id: str = None) -> dict:
        q = self.current_question()
        if player_id:
            time_remaining = self.get_time_remaining(player_id)
        else:
            time_remaining = None
            if not self.result_phase and self.time_limit > 0 \
                    and self.question_start_time and self.state == "running":
                elapsed = (self._now() - self.question_start_time).total_seconds()
                time_remaining = max(0.0, round(self.time_limit - elapsed, 1))
        alive = self.alive_players()
        return {
            "room_id": self.room_id,
            "mode": "team",
            "state": self.state,
            "current_q_index": self.current_q_index,
            "total_questions": len(self.questions),
            "question": (q.to_admin_dict() if include_answer else q.to_dict()) if q else None,
            "players": [p.to_public_dict(self) for p in self.players.values()],
            "teams": self.teams_ranked(),
            "team_count": len(self.teams),
            "round_log": self.round_log[-10:],
            "time_limit": self.time_limit,
            "time_remaining": time_remaining,
            "result_phase": self.result_phase,
            "pending_count": sum(1 for p in alive if p.current_action is None),
            "action_status": {p.player_id: (p.current_action is not None) for p in alive},
            "is_double": self.current_q_index in self.double_rounds,
            "paused": self.paused,
        }

    def admin_state(self) -> dict:
        base = self._base_state(include_answer=True)
        base["action_log"] = self.action_log[-40:]
        base["answer_stats"] = {str(k): v for k, v in self.answer_stats.items()}
        base["suggested_team_count"] = suggest_team_count(len(self.players))
        base["team_options"] = team_count_options(len(self.players))
        return base

    def private_state(self, player_id: str) -> dict:
        base = self._base_state(include_answer=False, player_id=player_id)
        base["round_log"] = _scrub_attackers(base.get("round_log"))
        player = self.players.get(player_id)
        if player:
            me = player.to_private_dict(self)
            if me.get("delay_from"):
                me["delay_from"] = ANON_ATTACKER
            if player.delay_until:
                me["delay_remaining"] = max(
                    0.0, round((player.delay_until - self._now()).total_seconds(), 1))
            base["me"] = me
            # Danh sách mục tiêu hợp lệ (chỉ đội khác, còn sống, không ẩn mình)
            base["valid_targets"] = [
                p.to_public_dict(self) for p in self.enemies_of(player) if not p.hide_active
            ]
            base["my_team"] = (self.teams[player.team_id].to_dict(self)
                               if player.team_id in self.teams else None)
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
# ROOM REGISTRY (in-memory, tách riêng với phòng của game cũ)
# ==================================================================

_rooms: dict = {}
_rooms_lock = threading.Lock()


def get_room(room_id: str) -> Optional[TeamRoom]:
    room = _rooms.get(room_id)
    if room is None:
        return None
    if (datetime.utcnow() - room.created_at).total_seconds() > ROOM_TTL_SECONDS:
        delete_room(room_id)
        return None
    return room


def create_room(questions: list, time_limit: int = 0) -> TeamRoom:
    room_id = "T" + uuid.uuid4().hex[:7].upper()
    room = TeamRoom(room_id, questions, time_limit=time_limit)
    with _rooms_lock:
        _rooms[room_id] = room
    return room


def delete_room(room_id: str):
    with _rooms_lock:
        _rooms.pop(room_id, None)


# ==================================================================
# PLAYER MANAGEMENT
# ==================================================================

def join_room(room_id: str, name: str, player_id: Optional[str] = None,
              avatar: str = "") -> dict:
    room = get_room(room_id)
    if not room:
        return {"error": "Phòng không tồn tại"}

    if player_id and player_id in room.players:
        p = room.players[player_id]
        if avatar:
            p.avatar = _clean_avatar(avatar)
        return {"player_id": p.player_id, "name": p.name, "avatar": p.avatar, "rejoin": True}

    name = (name or "").strip()
    if not name:
        return {"error": "Tên không được để trống"}

    existing = next((p for p in room.players.values() if p.name.lower() == name.lower()), None)
    if existing:
        if room.state != "lobby":
            return {"player_id": existing.player_id, "name": existing.name,
                    "avatar": existing.avatar, "rejoin": True}
        return {"error": f"Tên '{name}' đã được sử dụng. Vui lòng chọn tên khác."}

    if room.state != "lobby":
        return {"error": "Phòng đang trong game, không thể tham gia"}

    with room.lock:
        new_id = uuid.uuid4().hex[:12]
        p = Player(new_id, name)
        p.avatar = _clean_avatar(avatar)
        room.players[new_id] = p
    return {"player_id": new_id, "name": name, "avatar": p.avatar, "rejoin": False}


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
# CHIA ĐỘI + BẮT ĐẦU
# ==================================================================

def assign_teams(room: TeamRoom, team_count: int) -> dict:
    """Chia ngẫu nhiên người chơi vào team_count đội (chênh lệch ≤ 1 người)."""
    n = len(room.players)
    if n < 2:
        return {"error": "Cần ít nhất 2 người chơi để chia đội"}
    team_count = max(2, min(int(team_count), n, len(TEAM_PRESETS)))

    room.teams = {}
    room.team_order = []
    buckets = _split_player_ids(list(room.players.keys()), team_count)
    for i, bucket in enumerate(buckets):
        tid = f"T{i + 1}"
        team = Team(tid, TEAM_PRESETS[i % len(TEAM_PRESETS)])
        team.member_ids = bucket
        room.teams[tid] = team
        room.team_order.append(tid)
        for pid in bucket:
            room.players[pid].team_id = tid
    return {"ok": True, "team_count": team_count}


def start_game(room_id: str, team_count: Optional[int] = None) -> dict:
    room = get_room(room_id)
    if not room:
        return {"error": "Phòng không tồn tại"}
    if room.state != "lobby":
        return {"error": "Phòng đã bắt đầu"}
    if len(room.players) < 2:
        return {"error": "Cần ít nhất 2 người chơi để chia đội"}

    if team_count is None:
        team_count = suggest_team_count(len(room.players))

    with room.lock:
        res = assign_teams(room, team_count)
        if "error" in res:
            return res
        room.state = "running"
        room.current_q_index = 0
        room.question_start_time = datetime.utcnow()
        room.double_rounds = {i for i in range(len(room.questions)) if random.random() < 0.25}
        _reset_round(room)

    return {"ok": True, "teams": room.teams_ranked()}


def _reset_round(room: TeamRoom):
    for p in room.players.values():
        if p.hide_expires_at_round is not None and room.current_q_index >= p.hide_expires_at_round:
            p.hide_active = False
            p.hide_expires_at_round = None
    room.current_round_events = []
    room.hp_at_round_start = {p.player_id: round(p.hp, 1) for p in room.players.values()}
    for p in room.alive_players():
        p.current_action = None
        p.answered_current = False
        p.eliminate_options = []
        p.skill_options = []
        p.counter_active = False


# ==================================================================
# TRẢ LỜI CÂU HỎI
# ==================================================================

def submit_answer(room_id: str, player_id: str, selected: str) -> dict:
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

    mult = 2 if room.current_q_index in room.double_rounds else 1

    with room.lock:
        player.answered_current = True
        sel = (selected or "").upper()
        correct = (sel == q.answer.upper())
        speed_bonus = 0.0
        speed_block = 0

        stats = room.answer_stats.setdefault(
            room.current_q_index, {"A": 0, "B": 0, "C": 0, "D": 0, "correct": 0, "total": 0})
        if sel in stats:
            stats[sel] += 1
        stats["total"] += 1

        if correct:
            stats["correct"] += 1
            player.correct_streak += 1
            player.correct_count += 1
            player.skill_options = random.sample(list(SKILLS.keys()), 3)
            speed_bonus, speed_block = _speed_bonus(room, player)
            hp_gain = (player.correct_streak * 5.0 + speed_bonus) * mult
            player.hp += hp_gain
        else:
            penalty = 5.0 * mult
            player.hp = max(0.0, player.hp - penalty)
            hp_gain = -penalty
            player.correct_streak = 0
            player.current_action = {"skill": "skip", "target": None}

    team = room.teams.get(player.team_id)
    return {
        "correct": correct,
        "correct_answer": q.answer,
        "skill_options": [{**SKILLS[k], "skill": k} for k in player.skill_options],
        "hp_gain": hp_gain,
        "hp": round(player.hp, 1),
        "team_hp": round(team.hp(room), 1) if team else 0.0,
        "team_name": team.name if team else "",
        "streak": player.correct_streak,
        "speed_bonus": speed_bonus,
        "speed_block": speed_block,
        "speed_blocks": speed_blocks(room, player),
        "is_double": mult == 2,
    }


# ==================================================================
# DÙNG KỸ NĂNG
# ==================================================================

def submit_action(room_id: str, player_id: str, skill: Optional[str],
                  target_id: Optional[str]) -> dict:
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
            if skill not in player.skill_options:
                return {"error": "skill_not_owned"}
            if skill in TARGETED_SKILLS:
                if not target_id:
                    return {"error": "target_required"}
                target = room.players.get(target_id)
                if not target or not target.alive:
                    return {"error": "invalid_target"}
                # CẤM đánh đồng đội
                if room.same_team(player, target):
                    return {"error": "cannot_target_teammate"}
            player.current_action = {"skill": skill, "target": target_id}
            events = _apply_single_action(room, player, player.current_action)
            player.skill_options = []
            room.current_round_events.extend(events)
            for ev in events:
                _push_action_log(room, ev)

        if _all_alive_submitted(room):
            _finalize_round(room)
            room.result_phase = True
            room.result_phase_until = datetime.utcnow() + timedelta(seconds=RESULT_PHASE_SECONDS)

    return {"ok": True, "all_submitted": _all_alive_submitted_safe(room)}


def _all_alive_submitted(room: TeamRoom) -> bool:
    return all(p.current_action is not None for p in room.alive_players())


def _all_alive_submitted_safe(room: TeamRoom) -> bool:
    try:
        return all(p.current_action is not None for p in room.alive_players())
    except Exception:
        return False


def _push_action_log(room: TeamRoom, ev: dict):
    room._action_seq += 1
    entry = dict(ev)
    entry["seq"] = room._action_seq
    entry["round"] = room.current_q_index + 1
    entry["hp_after"] = {p.player_id: round(p.hp, 1) for p in room.players.values()}
    entry["team_hp_after"] = {t["team_id"]: t["hp"] for t in room.teams_ranked()}
    room.action_log.append(entry)
    if len(room.action_log) > 80:
        room.action_log = room.action_log[-80:]


def _team_name_of(room: TeamRoom, p: Player) -> str:
    t = room.teams.get(p.team_id)
    return t.name if t else ""


def _apply_single_action(room: TeamRoom, player: Player, action: dict) -> list:
    """Áp dụng NGAY hiệu ứng của một hành động. Tấn công chỉ nhắm vào ĐỘI KHÁC."""
    events = []
    skill = action["skill"]
    target_id = action.get("target")
    target = room.players.get(target_id) if target_id else None
    enemies = room.enemies_of(player)
    mult = 2 if room.current_q_index in room.double_rounds else 1

    def deal_damage(attacker: Player, tgt: Player, dmg: float, skill_used: str):
        if room.same_team(attacker, tgt):
            return  # chốt chặn cuối: không bao giờ sát thương đồng đội
        base = {
            "attacker": attacker.name, "attacker_team": _team_name_of(room, attacker),
            "target": tgt.name, "target_team": _team_name_of(room, tgt), "dmg": dmg,
        }
        if tgt.hide_active:
            events.append({"type": "evade", **base})
            return
        if tgt.has_counter():
            tgt.counter_active = False
            attacker.hp = max(0.0, attacker.hp - dmg)
            events.append({"type": "counter", **base})
        else:
            tgt.hp = max(0.0, tgt.hp - dmg)
            events.append({"type": "damage", **base, "skill": skill_used})

    if skill == "heal":
        player.hp += 10.0 * mult
        events.append({"type": "heal", "player": player.name,
                       "player_team": _team_name_of(room, player), "amount": 10 * mult})

    elif skill == "attack":
        if target and target.alive:
            deal_damage(player, target, 10.0 * mult, "attack")

    elif skill == "double":
        if target and target.alive:
            deal_damage(player, target, 15.0 * mult, "double")

    elif skill == "aoe":
        for other in enemies:
            deal_damage(player, other, 5.0 * mult, "aoe")

    elif skill == "balance":
        player.hp += 5.0 * mult
        events.append({"type": "heal", "player": player.name,
                       "player_team": _team_name_of(room, player), "amount": 5 * mult})
        if target and target.alive:
            deal_damage(player, target, 5.0 * mult, "balance")

    elif skill == "counter":
        player.counter_active = True
        events.append({"type": "set_counter", "player": player.name,
                       "player_team": _team_name_of(room, player)})

    elif skill == "eliminate":
        player.eliminate_next = True
        events.append({"type": "eliminate", "player": player.name,
                       "player_team": _team_name_of(room, player)})

    elif skill == "time_steal":
        if target and target.alive and not room.same_team(player, target):
            target.pending_delay += 15.0
            target.pending_delay_from = player.name
            events.append({"type": "time_steal", "attacker": player.name,
                           "attacker_team": _team_name_of(room, player),
                           "target": target.name, "target_team": _team_name_of(room, target),
                           "time_deducted": 15})

    elif skill == "time_bomb":
        bomb_amt = round(room.time_limit * 0.15, 1) if room.time_limit > 0 else 10.0
        for other in enemies:
            other.pending_delay += bomb_amt
            other.pending_delay_from = player.name
        events.append({"type": "time_bomb", "attacker": player.name,
                       "attacker_team": _team_name_of(room, player),
                       "affected_count": len(enemies),
                       "time_deducted": bomb_amt, "percent": 15})

    elif skill == "hide":
        player.hide_active = True
        player.hide_expires_at_round = room.current_q_index + 2
        events.append({"type": "hide", "player": player.name,
                       "player_team": _team_name_of(room, player)})

    for p in room.players.values():
        if p.hp <= 0:
            p.hp = 0.0
        p.alive = True   # HP 0% vẫn tiếp tục chơi (giống game cũ)

    return events


def _finalize_round(room: TeamRoom):
    hp_before = room.hp_at_round_start or {p.player_id: round(p.hp, 1)
                                           for p in room.players.values()}
    room.round_log.append({
        "round": room.current_q_index + 1,
        "events": list(room.current_round_events),
        "hp_before": hp_before,
        "hp_after": {p.player_id: round(p.hp, 1) for p in room.players.values()},
        "player_names": {p.player_id: p.name for p in room.players.values()},
        "teams": room.teams_ranked(),
    })


def _advance_round(room: TeamRoom):
    room.current_q_index += 1
    if room.current_q_index >= len(room.questions):
        room.state = "finished"
        return

    room.question_start_time = datetime.utcnow()
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

    q = room.current_question()
    if q:
        wrong_opts = [k for k in q.options if k != q.answer]
        for p in room.players.values():
            if p.eliminate_next:
                p.eliminate_options = random.sample(wrong_opts, min(2, len(wrong_opts)))
                p.eliminate_next = False


# ==================================================================
# TẠM DỪNG / TIẾP TỤC
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
# ÔN TẬP / ĐIỀU KHIỂN / TIMEOUT
# ==================================================================

def get_review(room_id: str) -> dict:
    room = get_room(room_id)
    if not room:
        return {"error": "room_not_found"}
    items = []
    for i, q in enumerate(room.questions):
        st = room.answer_stats.get(i, {"A": 0, "B": 0, "C": 0, "D": 0, "correct": 0, "total": 0})
        items.append({"index": i, "text": q.text, "options": q.options,
                      "answer": q.answer, "html": q.is_html, "stats": st})
    return {"questions": items}


def admin_force_advance(room_id: str) -> dict:
    room = get_room(room_id)
    if not room or room.state != "running":
        return {"error": "room_not_running"}
    with room.lock:
        if room.result_phase:
            room.result_phase = False
            room.result_phase_until = None
            _advance_round(room)
        else:
            for p in room.alive_players():
                if p.current_action is None:
                    p.current_action = {"skill": "skip", "target": None}
            _finalize_round(room)
            room.result_phase = False
            room.result_phase_until = None
            _advance_round(room)
    return {"ok": True}


def check_timeout(room_id: str):
    room = get_room(room_id)
    if not room or room.state != "running" or room.paused:
        return

    if room.result_phase and room.result_phase_until:
        if datetime.utcnow() >= room.result_phase_until:
            with room.lock:
                if room.result_phase and room.result_phase_until \
                        and datetime.utcnow() >= room.result_phase_until:
                    room.result_phase = False
                    room.result_phase_until = None
                    _advance_round(room)
        return

    if room.time_limit <= 0 or not room.question_start_time:
        return
    if (datetime.utcnow() - room.question_start_time).total_seconds() < room.time_limit:
        return
    with room.lock:
        if room.state != "running" or room.result_phase:
            return
        if room.question_start_time and \
                (datetime.utcnow() - room.question_start_time).total_seconds() < room.time_limit:
            return
        for p in room.alive_players():
            if p.current_action is None:
                p.current_action = {"skill": "skip", "target": None}
        _finalize_round(room)
        room.result_phase = True
        room.result_phase_until = datetime.utcnow() + timedelta(seconds=RESULT_PHASE_SECONDS)


def get_team_leaderboard(room_id: str) -> list:
    room = get_room(room_id)
    if not room:
        return []
    return room.teams_ranked()
