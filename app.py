# -*- coding: utf-8 -*-
"""
App Học Tập Lớp 1 - Kết Nối Tri Thức
Flask Application
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import secrets
from data import SUBJECTS, GENERATORS
import attack_defense_game as adg
import question_sets as qs_module
import team_battle_game as tbg

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route("/")
def index():
    """Trang chủ - chọn môn học"""
    return render_template("index.html", subjects=SUBJECTS)


@app.route("/mon/<subject_id>")
def subject(subject_id):
    """Trang môn học - chọn kì và chủ đề"""
    if subject_id not in SUBJECTS:
        return render_template("404.html"), 404
    subj = SUBJECTS[subject_id]
    return render_template("subject.html", subject_id=subject_id, subject=subj)


@app.route("/luyen-tap/<subject_id>/<topic_id>")
def exercise(subject_id, topic_id):
    """Trang làm bài tập"""
    if subject_id not in SUBJECTS:
        return render_template("404.html"), 404

    # Tìm topic trong semesters
    subj = SUBJECTS[subject_id]
    topic_info = None
    for sem_key, sem_data in subj["semesters"].items():
        if topic_id in sem_data["topics"]:
            topic_info = sem_data["topics"][topic_id]
            break

    if not topic_info:
        return render_template("404.html"), 404

    # Tạo câu hỏi
    generator = GENERATORS.get(subject_id)
    if not generator:
        return render_template("404.html"), 404

    # Xác định chế độ: choice (trắc nghiệm) hoặc fill (tự luận)
    mode = request.args.get("mode", "choice")
    difficulty = min(5, max(1, int(request.args.get("difficulty", 3))))

    if mode == "fill":
        # Tự luận: tạo nhiều câu rồi lọc fill, lấy 10 câu
        raw = generator(topic_id, num_questions=60, difficulty=difficulty)
        fill_qs = [q for q in raw if q.get("type") == "fill"]
        if len(fill_qs) < 10:
            extra = generator(topic_id, num_questions=60, difficulty=difficulty)
            fill_qs += [q for q in extra if q.get("type") == "fill"]
        sorted_questions = fill_qs[:10]
        num_choice = 0
        num_fill = len(sorted_questions)
    else:
        # Trắc nghiệm: tạo nhiều câu rồi lọc choice, lấy 20 câu
        raw = generator(topic_id, num_questions=60, difficulty=difficulty)
        choice_qs = [q for q in raw if q.get("type") != "fill"]
        if len(choice_qs) < 20:
            extra = generator(topic_id, num_questions=60, difficulty=difficulty)
            choice_qs += [q for q in extra if q.get("type") != "fill"]
        sorted_questions = choice_qs[:20]
        num_choice = len(sorted_questions)
        num_fill = 0

    # Lưu đáp án vào session
    session["answers"] = [q["answer"] for q in sorted_questions]
    session["answer_types"] = [q.get("type", "choice") for q in sorted_questions]
    session["subject_id"] = subject_id
    session["topic_id"] = topic_id

    return render_template(
        "exercise.html",
        subject_id=subject_id,
        subject=subj,
        topic_id=topic_id,
        topic=topic_info,
        questions=sorted_questions,
        num_choice=num_choice,
        num_fill=num_fill,
        mode=mode,
        difficulty=difficulty
    )


@app.route("/kiem-tra", methods=["POST"])
def check_answers():
    """Kiểm tra đáp án"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    user_answers = data.get("answers", [])
    correct_answers = session.get("answers", [])
    answer_types = session.get("answer_types", ["choice"] * len(correct_answers))

    results = []
    score = 0
    for i, (user_ans, correct_ans) in enumerate(zip(user_answers, correct_answers)):
        qtype = answer_types[i] if i < len(answer_types) else "choice"
        if qtype == "fill":
            # So sánh không phân biệt hoa thường, bỏ khoảng trắng thừa
            u = (user_ans or "").strip().lower()
            c = correct_ans.strip().lower()
            is_correct = (u == c)
        else:
            is_correct = (user_ans == correct_ans)
        if is_correct:
            score += 1
        results.append({
            "question_num": i + 1,
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct
        })

    total = len(correct_answers)
    return jsonify({
        "score": score,
        "total": total,
        "percentage": round(score / total * 100) if total > 0 else 0,
        "results": results
    })


@app.route("/da-bong/<subject_id>/<topic_id>")
def football_game(subject_id, topic_id):
    """Game đá bóng - sút penalty bằng cách trả lời đúng"""
    if subject_id not in SUBJECTS:
        return render_template("404.html"), 404

    subj = SUBJECTS[subject_id]
    topic_info = None
    for sem_key, sem_data in subj["semesters"].items():
        if topic_id in sem_data["topics"]:
            topic_info = sem_data["topics"][topic_id]
            break

    if not topic_info:
        return render_template("404.html"), 404

    generator = GENERATORS.get(subject_id)
    if not generator:
        return render_template("404.html"), 404

    # Trắc nghiệm 20 câu (chỉ choice)
    difficulty = min(5, max(1, int(request.args.get("difficulty", 3))))
    raw = generator(topic_id, num_questions=60, difficulty=difficulty)
    choice_qs = [q for q in raw if q.get("type") != "fill"]
    if len(choice_qs) < 20:
        extra = generator(topic_id, num_questions=60, difficulty=difficulty)
        choice_qs += [q for q in extra if q.get("type") != "fill"]
    questions = choice_qs[:20]

    return render_template(
        "football_game.html",
        subject_id=subject_id,
        subject=subj,
        topic_id=topic_id,
        topic=topic_info,
        questions=questions,
        difficulty=difficulty
    )


@app.route("/ban-sung/<subject_id>/<topic_id>")
def gunny_game(subject_id, topic_id):
    """Game bắn súng Gunny - trả lời đúng để bắn quái vật"""
    if subject_id not in SUBJECTS:
        return render_template("404.html"), 404

    subj = SUBJECTS[subject_id]
    topic_info = None
    for sem_key, sem_data in subj["semesters"].items():
        if topic_id in sem_data["topics"]:
            topic_info = sem_data["topics"][topic_id]
            break

    if not topic_info:
        return render_template("404.html"), 404

    generator = GENERATORS.get(subject_id)
    if not generator:
        return render_template("404.html"), 404

    # Trắc nghiệm 20 câu (chỉ choice)
    difficulty = min(5, max(1, int(request.args.get("difficulty", 3))))
    raw = generator(topic_id, num_questions=60, difficulty=difficulty)
    choice_qs = [q for q in raw if q.get("type") != "fill"]
    if len(choice_qs) < 20:
        extra = generator(topic_id, num_questions=60, difficulty=difficulty)
        choice_qs += [q for q in extra if q.get("type") != "fill"]
    questions = choice_qs[:20]

    return render_template(
        "gunny_game.html",
        subject_id=subject_id,
        subject=subj,
        topic_id=topic_id,
        topic=topic_info,
        questions=questions,
        difficulty=difficulty
    )


@app.route("/hoc-tu-vung/<subject_id>/<topic_id>")
def flashcards(subject_id, topic_id):
    """Trang học từ vựng (flashcards) cho Tiếng Anh"""
    if subject_id not in SUBJECTS:
        return render_template("404.html"), 404

    subj = SUBJECTS[subject_id]
    topic_info = None
    for sem_key, sem_data in subj["semesters"].items():
        if topic_id in sem_data["topics"]:
            topic_info = sem_data["topics"][topic_id]
            break

    if not topic_info:
        return render_template("404.html"), 404

    from data import ENGLISH_VOCAB
    vocab_data = ENGLISH_VOCAB.get(topic_id, {})
    words = vocab_data.get("words", vocab_data.get("sentences", []))

    return render_template(
        "flashcards.html",
        subject_id=subject_id,
        subject=subj,
        topic_id=topic_id,
        topic=topic_info,
        words=words
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# ==================================================================
# ATTACK & DEFENSE GAME ROUTES
# ==================================================================

@app.route("/attack-defense")
def attack_defense_home():
    """Admin: trang tạo game Attack & Defense."""
    return render_template("attack_defense_admin.html")


@app.route("/attack-defense/play/<room_id>")
def attack_defense_play(room_id):
    """Trang người chơi tham gia."""
    room = adg.get_room(room_id)
    if not room:
        return render_template("404.html"), 404
    return render_template("attack_defense_player.html", room_id=room_id)


@app.route("/attack-defense/api/create", methods=["POST"])
def ad_create():
    """Upload file câu hỏi hoặc chọn bộ câu sẵn và tạo phòng game."""
    questions = None
    
    # Check if using question set or file upload
    if request.is_json:
        data = request.get_json() or {}
        question_set_id = data.get("question_set_id")
        
        if question_set_id:
            # Load questions from saved question set
            question_set = qs_module.get_question_set(question_set_id)
            if not question_set:
                return jsonify({"error": "Bộ câu hỏi không tồn tại"}), 400
            questions_data = question_set.get("questions", [])
            if not questions_data:
                return jsonify({"error": "Bộ câu hỏi không có câu nào"}), 400
            
            # Convert question dicts to Question objects (uppercase keys)
            questions = []
            for q_data in questions_data:
                try:
                    # Convert lowercase option keys to uppercase
                    options_upper = {}
                    for key in ['a', 'b', 'c', 'd']:
                        if key in q_data.get("options", {}):
                            options_upper[key.upper()] = q_data["options"][key]
                    
                    q_obj = adg.Question(
                        text=q_data.get("question", ""),
                        options=options_upper,
                        answer=q_data.get("answer", "").upper(),
                        is_html=False
                    )
                    questions.append(q_obj)
                except Exception as e:
                    return jsonify({"error": f"Lỗi khi xử lý câu hỏi: {str(e)}"}), 400
        else:
            return jsonify({"error": "Chưa chọn bộ câu hỏi"}), 400
        
        try:
            time_limit = int(data.get("time_limit", 0))
        except (ValueError, TypeError):
            time_limit = 0
    else:
        # File upload mode (original behavior)
        if "file" not in request.files:
            return jsonify({"error": "Chưa chọn file"}), 400
        f = request.files["file"]
        try:
            questions = adg.parse_questions_from_file(f)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        try:
            time_limit = int(request.form.get("time_limit", 0))
        except (ValueError, TypeError):
            time_limit = 0
    
    if not questions:
        return jsonify({"error": "Không có câu hỏi nào để tạo game"}), 400
    
    room = adg.create_room(questions, time_limit=time_limit)
    return jsonify({"room_id": room.room_id, "total_questions": len(room.questions)})


@app.route("/attack-defense/api/join", methods=["POST"])
def ad_join():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    player_id = data.get("player_id")
    if not name and not player_id:
        return jsonify({"error": "Tên không được để trống"}), 400
    result = adg.join_room(data.get("room_id", ""), name, player_id,
                           data.get("avatar", ""))
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/attack-defense/api/ready", methods=["POST"])
def ad_ready():
    data = request.get_json() or {}
    ok = adg.set_player_ready(data.get("room_id", ""), data.get("player_id", ""))
    return jsonify({"ok": ok})


@app.route("/attack-defense/api/start", methods=["POST"])
def ad_start():
    data = request.get_json() or {}
    ok = adg.start_game(data.get("room_id", ""))
    if not ok:
        return jsonify({"error": "Không thể bắt đầu game"}), 400
    return jsonify({"ok": True})


@app.route("/attack-defense/api/state")
def ad_state():
    room_id = request.args.get("room_id", "")
    player_id = request.args.get("player_id", "")
    room = adg.get_room(room_id)
    if not room:
        return jsonify({"error": "room_not_found"}), 404
    # Tự động chuyển vòng nếu hết giờ
    adg.check_timeout(room_id)
    if player_id:
        return jsonify(room.private_state(player_id))
    return jsonify(room.admin_state())


@app.route("/attack-defense/api/answer", methods=["POST"])
def ad_answer():
    data = request.get_json() or {}
    result = adg.submit_answer(
        data.get("room_id", ""),
        data.get("player_id", ""),
        data.get("answer", "")
    )
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/attack-defense/api/action", methods=["POST"])
def ad_action():
    data = request.get_json() or {}
    result = adg.submit_action(
        data.get("room_id", ""),
        data.get("player_id", ""),
        data.get("skill"),
        data.get("target_id")
    )
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/attack-defense/api/force-advance", methods=["POST"])
def ad_force_advance():
    try:
        data = request.get_json() or {}
        result = adg.admin_force_advance(data.get("room_id", ""))
        if "error" in result:
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        print(f"Force advance error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/attack-defense/api/pause", methods=["POST"])
def ad_pause():
    data = request.get_json() or {}
    result = adg.pause_game(data.get("room_id", ""))
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/attack-defense/api/resume", methods=["POST"])
def ad_resume():
    data = request.get_json() or {}
    result = adg.resume_game(data.get("room_id", ""))
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/attack-defense/api/review")
def ad_review():
    result = adg.get_review(request.args.get("room_id", ""))
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


# ==================================================================
# TEAM BATTLE GAME ROUTES (module ĐỘC LẬP - không ảnh hưởng Attack & Defense)
# ==================================================================

@app.route("/team-battle")
def team_battle_home():
    """Admin: trang tạo game Đấu Trường Đồng Đội."""
    return render_template("team_battle_admin.html")


@app.route("/team-battle/play/<room_id>")
def team_battle_play(room_id):
    """Trang người chơi tham gia."""
    room = tbg.get_room(room_id)
    if not room:
        return render_template("404.html"), 404
    return render_template("team_battle_player.html", room_id=room_id)


def _tb_build_questions_from_set(question_set_id):
    """Chuyển bộ câu hỏi đã lưu thành danh sách Question."""
    question_set = qs_module.get_question_set(question_set_id)
    if not question_set:
        return None, "Bộ câu hỏi không tồn tại"
    questions_data = question_set.get("questions", [])
    if not questions_data:
        return None, "Bộ câu hỏi không có câu nào"
    questions = []
    for q_data in questions_data:
        options_upper = {}
        for key in ["a", "b", "c", "d"]:
            if key in q_data.get("options", {}):
                options_upper[key.upper()] = q_data["options"][key]
        questions.append(tbg.Question(
            text=q_data.get("question", ""),
            options=options_upper,
            answer=q_data.get("answer", "").upper(),
            is_html=False,
        ))
    return questions, None


@app.route("/team-battle/api/create", methods=["POST"])
def tb_create():
    """Tạo phòng chơi đồng đội từ file upload hoặc bộ câu hỏi có sẵn."""
    questions = None

    if request.is_json:
        data = request.get_json() or {}
        question_set_id = data.get("question_set_id")
        if not question_set_id:
            return jsonify({"error": "Chưa chọn bộ câu hỏi"}), 400
        questions, err = _tb_build_questions_from_set(question_set_id)
        if err:
            return jsonify({"error": err}), 400
        try:
            time_limit = int(data.get("time_limit", 0))
        except (ValueError, TypeError):
            time_limit = 0
    else:
        if "file" not in request.files:
            return jsonify({"error": "Chưa chọn file"}), 400
        try:
            questions = tbg.parse_questions_from_file(request.files["file"])
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        try:
            time_limit = int(request.form.get("time_limit", 0))
        except (ValueError, TypeError):
            time_limit = 0

    if not questions:
        return jsonify({"error": "Không có câu hỏi nào để tạo game"}), 400

    room = tbg.create_room(questions, time_limit=time_limit)
    return jsonify({"room_id": room.room_id, "total_questions": len(room.questions)})


@app.route("/team-battle/api/join", methods=["POST"])
def tb_join():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    player_id = data.get("player_id")
    if not name and not player_id:
        return jsonify({"error": "Tên không được để trống"}), 400
    result = tbg.join_room(data.get("room_id", ""), name, player_id,
                           data.get("avatar", ""))
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/team-battle/api/ready", methods=["POST"])
def tb_ready():
    data = request.get_json() or {}
    ok = tbg.set_player_ready(data.get("room_id", ""), data.get("player_id", ""))
    return jsonify({"ok": ok})


@app.route("/team-battle/api/start", methods=["POST"])
def tb_start():
    """Chia đội ngẫu nhiên theo số đội admin chọn rồi bắt đầu."""
    data = request.get_json() or {}
    try:
        team_count = int(data.get("team_count")) if data.get("team_count") else None
    except (ValueError, TypeError):
        team_count = None
    result = tbg.start_game(data.get("room_id", ""), team_count)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/team-battle/api/state")
def tb_state():
    room_id = request.args.get("room_id", "")
    player_id = request.args.get("player_id", "")
    room = tbg.get_room(room_id)
    if not room:
        return jsonify({"error": "room_not_found"}), 404
    tbg.check_timeout(room_id)
    if player_id:
        return jsonify(room.private_state(player_id))
    return jsonify(room.admin_state())


@app.route("/team-battle/api/answer", methods=["POST"])
def tb_answer():
    data = request.get_json() or {}
    result = tbg.submit_answer(
        data.get("room_id", ""), data.get("player_id", ""), data.get("answer", ""))
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/team-battle/api/action", methods=["POST"])
def tb_action():
    data = request.get_json() or {}
    result = tbg.submit_action(
        data.get("room_id", ""), data.get("player_id", ""),
        data.get("skill"), data.get("target_id"))
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/team-battle/api/force-advance", methods=["POST"])
def tb_force_advance():
    data = request.get_json() or {}
    result = tbg.admin_force_advance(data.get("room_id", ""))
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/team-battle/api/pause", methods=["POST"])
def tb_pause():
    data = request.get_json() or {}
    result = tbg.pause_game(data.get("room_id", ""))
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/team-battle/api/resume", methods=["POST"])
def tb_resume():
    data = request.get_json() or {}
    result = tbg.resume_game(data.get("room_id", ""))
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/team-battle/api/review")
def tb_review():
    result = tbg.get_review(request.args.get("room_id", ""))
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


@app.route("/team-battle/api/leaderboard")
def tb_leaderboard():
    return jsonify(tbg.get_team_leaderboard(request.args.get("room_id", "")))

# ============================================================
# QUESTION SET MANAGEMENT
# ============================================================

@app.route("/question-sets")
def question_sets_manage():
    """Trang quản lý bộ câu hỏi"""
    question_sets = qs_module.list_question_sets()
    message = request.args.get("message", "")
    return render_template("question_sets.html", question_sets=question_sets, message=message)


@app.route("/question-sets/upload", methods=["POST"])
def upload_question_set():
    """Upload file (CSV, TXT, DOC, DOCX) và tạo bộ câu hỏi"""
    set_name = request.form.get("set_name", "").strip()
    subject = request.form.get("subject", "").strip()
    question_file = request.files.get("question_file")
    
    # Kiểm tra dữ liệu
    if not set_name:
        return redirect(url_for("question_sets_manage", message="❌ Vui lòng nhập tên bộ câu hỏi"))
    
    if not subject:
        return redirect(url_for("question_sets_manage", message="❌ Vui lòng chọn môn học"))
    
    if not question_file or question_file.filename == "":
        return redirect(url_for("question_sets_manage", message="❌ Vui lòng chọn file câu hỏi"))
    
    # Kiểm tra định dạng file
    filename = question_file.filename.lower()
    allowed_extensions = ('.csv', '.txt', '.doc', '.docx')
    if not filename.endswith(allowed_extensions):
        return redirect(url_for("question_sets_manage", 
                              message=f"❌ Định dạng không hỗ trợ. Chỉ chấp nhận: {', '.join(allowed_extensions)}"))
    
    # Parse file
    try:
        questions, error = qs_module.parse_question_file(question_file, question_file.filename)
        
        if error:
            return redirect(url_for("question_sets_manage", message=f"❌ {error}"))
        
        # Tạo bộ câu hỏi
        success, msg = qs_module.create_question_set(set_name, subject, questions)
        
        if success:
            return redirect(url_for("question_sets_manage", message=msg))
        else:
            return redirect(url_for("question_sets_manage", message=f"❌ {msg}"))
    
    except Exception as e:
        return redirect(url_for("question_sets_manage", message=f"❌ Lỗi: {str(e)}"))


@app.route("/question-sets/<set_id>")
def view_question_set(set_id):
    """Xem chi tiết bộ câu hỏi"""
    question_set = qs_module.get_question_set(set_id)
    
    if not question_set:
        return render_template("404.html"), 404
    
    return render_template("view_question_set.html", question_set=question_set)


@app.route("/question-sets/<set_id>/edit")
def edit_question_set(set_id):
    """Chỉnh sửa bộ câu hỏi - xem trước và edit"""
    question_set = qs_module.get_question_set(set_id)
    
    if not question_set:
        return render_template("404.html"), 404
    
    return render_template("edit_question_set.html", question_set=question_set)


@app.route("/question-sets/<set_id>/update", methods=["POST"])
def update_question_set(set_id):
    """Lưu thay đổi bộ câu hỏi"""
    try:
        import json
        questions_json = request.form.get("questions_json")
        if not questions_json:
            return redirect(url_for("question_sets_manage", message="❌ Dữ liệu câu hỏi không hợp lệ"))
        
        questions = json.loads(questions_json)
        
        # Validate questions
        if not questions or len(questions) < 1:
            return redirect(url_for("edit_question_set", set_id=set_id))
        
        # Update question set
        success, msg = qs_module.update_question_set(set_id, questions=questions)
        
        if success:
            return redirect(url_for("view_question_set", set_id=set_id))
        else:
            return redirect(url_for("edit_question_set", set_id=set_id))
    
    except Exception as e:
        return redirect(url_for("edit_question_set", set_id=set_id))


@app.route("/question-sets/<set_id>/delete", methods=["GET", "POST"])
def delete_question_set(set_id):
    """Xóa bộ câu hỏi"""
    success, msg = qs_module.delete_question_set(set_id)
    
    if success:
        return redirect(url_for("question_sets_manage", message=f"✅ {msg}"))
    else:
        return redirect(url_for("question_sets_manage", message=f"❌ {msg}"))


@app.route("/api/question-sets")
def api_get_question_sets():
    """API: Lấy danh sách bộ câu hỏi (JSON)"""
    subject = request.args.get("subject")
    question_sets = qs_module.list_question_sets(subject)
    return jsonify(question_sets)


@app.route("/api/question-sets/<set_id>")
def api_get_question_set(set_id):
    """API: Lấy chi tiết bộ câu hỏi (JSON)"""
    question_set = qs_module.get_question_set(set_id)
    
    if not question_set:
        return jsonify({"error": "not_found"}), 404
    
    return jsonify(question_set)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
