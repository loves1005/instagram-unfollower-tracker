import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import threading
from logic import get_unfollowers_data, parse_instagram_json

# ─────────────────────────────────────────────
#  색상 팔레트 (인스타그램 그라디언트 느낌)
# ─────────────────────────────────────────────
BG          = "#0d0d0d"
CARD        = "#1a1a1a"
CARD2       = "#222222"
BORDER      = "#2d2d2d"
ACCENT      = "#e1306c"   # Instagram 핑크
ACCENT2     = "#833ab4"   # Instagram 퍼플
ACCENT3     = "#fd1d1d"   # Instagram 레드
GOLD        = "#f77f00"
GREEN       = "#25d366"
BLUE        = "#4fc3f7"
TEXT        = "#f5f5f5"
TEXT_SUB    = "#888888"
TEXT_DIM    = "#555555"
FONT_MAIN   = ("Segoe UI", 10)
FONT_BOLD   = ("Segoe UI", 10, "bold")
FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_SUB    = ("Segoe UI", 11)
FONT_LABEL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 10)


class HoverButton(tk.Label):
    """커서 올리면 색이 바뀌는 커스텀 버튼"""
    def __init__(self, parent, text, command=None, bg=CARD2, fg=TEXT,
                 hover_bg=ACCENT, hover_fg=TEXT, font=FONT_BOLD,
                 padx=16, pady=8, radius=8, **kw):
        super().__init__(parent, text=text, bg=bg, fg=fg, font=font,
                         padx=padx, pady=pady, cursor="hand2", **kw)
        self._bg = bg
        self._fg = fg
        self._hover_bg = hover_bg
        self._hover_fg = hover_fg
        self._cmd = command
        self.bind("<Enter>", lambda e: self.config(bg=self._hover_bg, fg=self._hover_fg))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg, fg=self._fg))
        self.bind("<Button-1>", lambda e: command() if command else None)


class FileDropZone(tk.Frame):
    """파일 드롭/클릭 가능한 카드 영역"""
    def __init__(self, parent, label, hint, command, **kw):
        super().__init__(parent, bg=CARD, highlightbackground=BORDER,
                         highlightthickness=1, **kw)
        self._command = command
        self._selected = False

        # 아이콘 줄
        self.icon_lbl = tk.Label(self, text="📂", bg=CARD, fg=TEXT_SUB,
                                 font=("Segoe UI Emoji", 24))
        self.icon_lbl.pack(pady=(14, 2))

        self.title_lbl = tk.Label(self, text=label, bg=CARD, fg=TEXT,
                                  font=FONT_BOLD)
        self.title_lbl.pack()

        self.hint_lbl = tk.Label(self, text=hint, bg=CARD, fg=TEXT_SUB,
                                 font=FONT_LABEL, wraplength=220)
        self.hint_lbl.pack(pady=(2, 4))

        self.status_lbl = tk.Label(self, text="클릭하여 파일 선택", bg=CARD,
                                   fg=TEXT_DIM, font=FONT_LABEL)
        self.status_lbl.pack(pady=(0, 14))

        # 전체 영역 클릭 가능
        for w in [self, self.icon_lbl, self.title_lbl, self.hint_lbl, self.status_lbl]:
            w.bind("<Button-1>", lambda e: self._command())
            w.bind("<Enter>", lambda e: self._on_hover(True))
            w.bind("<Leave>", lambda e: self._on_hover(False))
        self.config(cursor="hand2")

    def _on_hover(self, state):
        col = BORDER if state else BG
        self.config(highlightbackground=col if not self._selected else ACCENT)

    def set_file(self, filepath):
        self._selected = True
        name = os.path.basename(filepath)
        self.icon_lbl.config(text="✅", fg=GREEN)
        self.status_lbl.config(text=name, fg=GREEN)
        self.config(highlightbackground=GREEN)

    def reset(self):
        self._selected = False
        self.icon_lbl.config(text="📂", fg=TEXT_SUB)
        self.status_lbl.config(text="클릭하여 파일 선택", fg=TEXT_DIM)
        self.config(highlightbackground=BORDER)


class UserListFrame(tk.Frame):
    """유저 목록 + 검색 + 복사 버튼이 있는 카드"""
    def __init__(self, parent, title, color, **kw):
        super().__init__(parent, bg=CARD, highlightbackground=color,
                         highlightthickness=2, **kw)
        self._color = color
        self._users = []

        # 헤더
        hdr = tk.Frame(self, bg=CARD)
        hdr.pack(fill="x", padx=12, pady=(10, 4))

        self.count_lbl = tk.Label(hdr, text=title, bg=CARD, fg=color,
                                  font=FONT_BOLD)
        self.count_lbl.pack(side="left")

        HoverButton(hdr, "복사", command=self._copy_all, bg=CARD2,
                    fg=color, hover_bg=color, hover_fg="#000",
                    padx=8, pady=3, font=FONT_LABEL).pack(side="right")

        # 검색창
        search_frame = tk.Frame(self, bg=CARD2, highlightbackground=BORDER,
                                highlightthickness=1)
        search_frame.pack(fill="x", padx=12, pady=(0, 6))

        tk.Label(search_frame, text="🔍", bg=CARD2, fg=TEXT_SUB,
                 font=("Segoe UI Emoji", 10)).pack(side="left", padx=6)
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *a: self._filter())
        tk.Entry(search_frame, textvariable=self._search_var, bg=CARD2,
                 fg=TEXT, insertbackground=TEXT, relief="flat",
                 font=FONT_MAIN, bd=0).pack(side="left", fill="x",
                                            expand=True, pady=6)

        # 리스트
        list_frame = tk.Frame(self, bg=CARD)
        list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        scrollbar = tk.Scrollbar(list_frame, orient="vertical",
                                  bg=BORDER, troughcolor=CARD,
                                  activebackground=ACCENT)
        self._listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg=CARD, fg=TEXT,
            selectbackground=color, selectforeground="#000",
            font=FONT_MONO,
            relief="flat", bd=0,
            activestyle="none",
            highlightthickness=0,
        )
        scrollbar.config(command=self._listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self._listbox.pack(side="left", fill="both", expand=True)

        # 더블클릭 → 프로필 열기
        self._listbox.bind("<Double-Button-1>", self._open_profile)

        self._title = title

    def set_users(self, users):
        self._users = users
        self._filter()
        count = len(users)
        self.count_lbl.config(text=f"{self._title}  ({count}명)")

    def _filter(self):
        q = self._search_var.get().lower()
        self._listbox.delete(0, "end")
        for u in self._users:
            if q in u.lower():
                self._listbox.insert("end", f"  @{u}")

    def _copy_all(self):
        if not self._users:
            return
        text = "\n".join(self._users)
        self._listbox.clipboard_clear()
        self._listbox.clipboard_append(text)
        messagebox.showinfo("복사 완료", f"{len(self._users)}명의 유저명이 클립보드에 복사됐습니다!")

    def _open_profile(self, event):
        sel = self._listbox.curselection()
        if not sel:
            return
        raw = self._listbox.get(sel[0]).strip().lstrip("@")
        url = f"https://www.instagram.com/{raw}/"
        import webbrowser
        webbrowser.open(url)


class InstagramUnfollowerTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Unfollower Tracker")
        self.root.geometry("860x700")
        self.root.minsize(760, 580)
        self.root.configure(bg=BG)

        self.followers_path = ""
        self.following_path = ""
        self._last_results = None  # 저장 기능용

        self._build_ui()

    # ──────────────────────────────────────────
    #  UI 빌드
    # ──────────────────────────────────────────
    def _build_ui(self):
        # ── 헤더 ──
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill="x", padx=30, pady=(20, 0))

        tk.Label(hdr, text="📸 Instagram", bg=BG, fg=ACCENT,
                 font=FONT_TITLE).pack(side="left")
        tk.Label(hdr, text=" Unfollower Tracker", bg=BG, fg=TEXT,
                 font=FONT_TITLE).pack(side="left")

        btn_hdr_row = tk.Frame(hdr, bg=BG)
        btn_hdr_row.pack(side="right")
        HoverButton(btn_hdr_row, "🔬 진단", command=self._diagnose,
                    bg=CARD2, fg=BLUE, hover_bg=CARD,
                    hover_fg=TEXT, padx=10, pady=6,
                    font=FONT_LABEL).pack(side="left", padx=(0, 4))
        HoverButton(btn_hdr_row, "사용 방법 ❓", command=self._show_instructions,
                    bg=CARD2, fg=TEXT_SUB, hover_bg=CARD,
                    hover_fg=TEXT, padx=10, pady=6,
                    font=FONT_LABEL).pack(side="left")

        # ── 부제목 ──
        tk.Label(self.root,
                 text="Instagram 공식 데이터 내보내기로 언팔로워를 찾아보세요.",
                 bg=BG, fg=TEXT_SUB, font=FONT_SUB).pack(anchor="w", padx=30)

        # ── 구분선 ──
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=30, pady=12)

        # ── 파일 선택 영역 ──
        file_row = tk.Frame(self.root, bg=BG)
        file_row.pack(fill="x", padx=30)

        self._drop_followers = FileDropZone(
            file_row,
            label="followers_1.json",
            hint="나를 팔로우하는 사람 목록",
            command=self._select_followers,
        )
        self._drop_followers.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._drop_following = FileDropZone(
            file_row,
            label="following.json",
            hint="내가 팔로우하는 사람 목록",
            command=self._select_following,
        )
        self._drop_following.pack(side="left", fill="x", expand=True, padx=(8, 0))

        # ── 분석 버튼 ──
        btn_row = tk.Frame(self.root, bg=BG)
        btn_row.pack(pady=14)

        self._analyze_btn = tk.Label(
            btn_row,
            text="  🔍  분석 시작  ",
            bg=TEXT_DIM, fg="#000",
            font=("Segoe UI", 13, "bold"),
            padx=28, pady=12,
            cursor="arrow",
        )
        self._analyze_btn.pack(side="left", padx=6)

        HoverButton(btn_row, "↺  초기화", command=self._reset,
                    bg=CARD2, fg=TEXT_SUB, hover_bg=CARD,
                    hover_fg=TEXT, padx=14, pady=11,
                    font=FONT_BOLD).pack(side="left", padx=6)

        HoverButton(btn_row, "💾  결과 저장", command=self._save_results,
                    bg=CARD2, fg=GREEN, hover_bg=CARD,
                    hover_fg=GREEN, padx=14, pady=11,
                    font=FONT_BOLD).pack(side="left", padx=6)

        self._status_lbl = tk.Label(
            self.root, text="", bg=BG, fg=TEXT_SUB, font=FONT_LABEL
        )
        self._status_lbl.pack()

        # ── 요약 카드 ──
        self._summary_frame = tk.Frame(self.root, bg=BG)
        self._summary_frame.pack(fill="x", padx=30, pady=(0, 8))

        self._stat_labels = {}
        stats = [
            ("following",   "팔로잉",   BLUE),
            ("followers",   "팔로워",   ACCENT2),
            ("unfollowers", "언팔로워", ACCENT),
            ("fans",        "나만의 팬", GOLD),
            ("mutuals",     "맞팔",      GREEN),
        ]
        for key, label, color in stats:
            card = tk.Frame(self._summary_frame, bg=CARD,
                            highlightbackground=BORDER, highlightthickness=1)
            card.pack(side="left", fill="x", expand=True, padx=4)
            num = tk.Label(card, text="–", bg=CARD, fg=color,
                           font=("Segoe UI", 18, "bold"))
            num.pack(pady=(8, 0))
            tk.Label(card, text=label, bg=CARD, fg=TEXT_SUB,
                     font=FONT_LABEL).pack(pady=(0, 8))
            self._stat_labels[key] = num

        # ── 결과 탭 영역 ──
        result_container = tk.Frame(self.root, bg=BG)
        result_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self._unfollower_list = UserListFrame(
            result_container,
            title="언팔로워",
            color=ACCENT,
        )
        self._unfollower_list.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self._fan_list = UserListFrame(
            result_container,
            title="나만의 팬",
            color=GOLD,
        )
        self._fan_list.pack(side="left", fill="both", expand=True, padx=(6, 0))

    # ──────────────────────────────────────────
    #  파일 선택
    # ──────────────────────────────────────────
    def _select_followers(self):
        path = filedialog.askopenfilename(
            title="followers_1.json 선택",
            filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")]
        )
        if path:
            self.followers_path = path
            self._drop_followers.set_file(path)
            self._check_ready()

    def _select_following(self):
        path = filedialog.askopenfilename(
            title="following.json 선택",
            filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")]
        )
        if path:
            self.following_path = path
            self._drop_following.set_file(path)
            self._check_ready()

    def _check_ready(self):
        if self.followers_path and self.following_path:
            self._analyze_btn.config(
                bg=ACCENT, fg=TEXT, cursor="hand2"
            )
            self._analyze_btn.bind("<Button-1>", lambda e: self._analyze())
            self._analyze_btn.bind("<Enter>",
                lambda e: self._analyze_btn.config(bg=ACCENT2))
            self._analyze_btn.bind("<Leave>",
                lambda e: self._analyze_btn.config(bg=ACCENT))
        else:
            self._analyze_btn.config(bg=TEXT_DIM, fg="#000", cursor="arrow")
            self._analyze_btn.unbind("<Button-1>")

    # ──────────────────────────────────────────
    #  분석
    # ──────────────────────────────────────────
    def _analyze(self):
        self._analyze_btn.config(text="  ⏳  분석 중...  ", bg=TEXT_DIM,
                                  cursor="arrow")
        self._analyze_btn.unbind("<Button-1>")
        self._status_lbl.config(text="파일을 읽는 중입니다...", fg=TEXT_SUB)
        self.root.update()

        def run():
            try:
                results = get_unfollowers_data(
                    self.followers_path, self.following_path
                )
                self.root.after(0, lambda: self._show_results(results))
            except Exception as e:
                self.root.after(0, lambda: self._show_error(str(e)))

        threading.Thread(target=run, daemon=True).start()

    def _show_results(self, results):
        # 요약 카드 업데이트
        self._stat_labels["following"].config(text=str(results["following_count"]))
        self._stat_labels["followers"].config(text=str(results["followers_count"]))
        self._stat_labels["unfollowers"].config(text=str(len(results["unfollowers"])))
        self._stat_labels["fans"].config(text=str(len(results["fans"])))
        self._stat_labels["mutuals"].config(text=str(len(results["mutuals"])))

        # 결과 저장 (save 기능용)
        self._last_results = results

        # 리스트 업데이트
        self._unfollower_list.set_users(results["unfollowers"])
        self._fan_list.set_users(results["fans"])

        self._status_lbl.config(text="✅ 분석 완료!", fg=GREEN)
        self._analyze_btn.config(text="  🔍  분석 시작  ", bg=ACCENT, fg=TEXT,
                                  cursor="hand2")
        self._analyze_btn.bind("<Button-1>", lambda e: self._analyze())

    def _show_error(self, msg):
        self._analyze_btn.config(text="  🔍  분석 시작  ", bg=ACCENT, fg=TEXT,
                                  cursor="hand2")
        self._analyze_btn.bind("<Button-1>", lambda e: self._analyze())
        self._status_lbl.config(text="", fg=TEXT_SUB)
        messagebox.showerror(
            "분석 실패",
            f"❌ 파일을 읽지 못했습니다.\n\n{msg}\n\n"
            "올바른 Instagram 내보내기 JSON 파일인지 확인하세요."
        )

    # ──────────────────────────────────────────
    #  초기화
    # ──────────────────────────────────────────
    def _reset(self):
        self.followers_path = ""
        self.following_path = ""
        self._drop_followers.reset()
        self._drop_following.reset()
        self._check_ready()
        self._status_lbl.config(text="")
        for lbl in self._stat_labels.values():
            lbl.config(text="–")
        self._unfollower_list.set_users([])
        self._fan_list.set_users([])

    # ──────────────────────────────────────────
    #  진단
    # ──────────────────────────────────────────
    def _diagnose(self):
        """선택된 파일의 파싱 상태를 팝업으로 보여줍니다."""
        win = tk.Toplevel(self.root)
        win.title("🔬 파일 진단")
        win.geometry("520x420")
        win.configure(bg=BG)
        win.grab_set()

        tk.Label(win, text="🔬  파일 파싱 진단",
                 bg=BG, fg=BLUE, font=("Segoe UI", 13, "bold")).pack(
                     pady=(20, 10), padx=20, anchor="w")

        txt = tk.Text(win, bg=CARD, fg=TEXT, font=FONT_MONO,
                      relief="flat", bd=0, padx=12, pady=8,
                      highlightthickness=0)
        txt.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        def run_diag():
            lines = []
            for label, path in [("📂 followers_1.json", self.followers_path),
                                 ("📂 following.json",   self.following_path)]:
                lines.append(f"{label}")
                if not path:
                    lines.append("  ❌ 파일이 선택되지 않았습니다.\n")
                    continue
                lines.append(f"  경로: {path}")
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        raw = json.load(f)
                    top_type = type(raw).__name__
                    lines.append(f"  최상위 타입: {top_type}")
                    if isinstance(raw, dict):
                        lines.append(f"  최상위 키: {list(raw.keys())}")
                        for k, v in raw.items():
                            if isinstance(v, list):
                                lines.append(f"  키 '{k}' → 리스트 {len(v)}개")
                                if v:
                                    first = v[0]
                                    lines.append(f"  첫 항목 키: {list(first.keys()) if isinstance(first, dict) else type(first).__name__}")
                    elif isinstance(raw, list):
                        lines.append(f"  리스트 항목 수: {len(raw)}")
                        if raw:
                            first = raw[0]
                            lines.append(f"  첫 항목 키: {list(first.keys()) if isinstance(first, dict) else type(first).__name__}")

                    users = parse_instagram_json(path)
                    lines.append(f"  ✅ 파싱된 유저 수: {len(users)}명")
                    if users:
                        sample = list(users)[:3]
                        lines.append(f"  샘플: {sample}")
                    else:
                        lines.append("  ⚠️ 유저를 하나도 파싱하지 못했습니다!")
                except Exception as e:
                    lines.append(f"  ❌ 오류: {e}")
                lines.append("")
            win.after(0, lambda: _update(lines))

        def _update(lines):
            txt.config(state="normal")
            txt.delete("1.0", "end")
            txt.insert("end", "\n".join(lines))
            txt.config(state="disabled")

        threading.Thread(target=run_diag, daemon=True).start()
        HoverButton(win, "닫기", command=win.destroy,
                    bg=CARD2, fg=TEXT_SUB, hover_bg=CARD,
                    padx=16, pady=7).pack(pady=(0, 14))

    # ──────────────────────────────────────────
    #  결과 저장
    # ──────────────────────────────────────────
    def _save_results(self):
        if not self._last_results:
            messagebox.showwarning("결과 없음", "먼저 분석을 실행하세요.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile="instagram_unfollowers.txt",
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        if not path:
            return
        r = self._last_results
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("=== Instagram Unfollower 분석 결과 ===\n\n")
                f.write(f"팔로잉: {r['following_count']}명\n")
                f.write(f"팔로워: {r['followers_count']}명\n")
                f.write(f"맞팔:   {len(r['mutuals'])}명\n\n")
                f.write(f"--- 언팔로워 ({len(r['unfollowers'])}명) ---\n")
                f.write("\n".join(r['unfollowers']) or "(없음)")
                f.write("\n\n")
                f.write(f"--- 나만의 팬 ({len(r['fans'])}명) ---\n")
                f.write("\n".join(r['fans']) or "(없음)")
                f.write("\n")
            messagebox.showinfo("저장 완료", f"결과가 저장됐습니다:\n{path}")
        except Exception as e:
            messagebox.showerror("저장 실패", str(e))

    # ──────────────────────────────────────────
    #  사용 방법
    # ──────────────────────────────────────────
    def _show_instructions(self):
        win = tk.Toplevel(self.root)
        win.title("사용 방법")
        win.geometry("480x500")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="📖  Instagram 데이터 다운로드 방법",
                 bg=BG, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(
                     pady=(20, 10), padx=20, anchor="w")

        steps = [
            ("Step 1", "Instagram 앱 → 프로필 → 메뉴(☰) → 설정 및 개인정보 → 계정 센터"),
            ("Step 2", "내 정보 및 권한 → 내 정보 다운로드 → 정보 다운로드"),
            ("Step 3", "'일부 정보 선택' → '팔로워 및 팔로잉'만 체크"),
            ("Step 4", "형식: JSON  /  화질: 낮음  /  기간: 전체 기간 선택 후 요청"),
            ("Step 5", "이메일로 온 링크에서 ZIP 파일 다운로드 후 압축 해제"),
            ("Step 6", "connections/followers_and_following/ 폴더 안의\n"
                       "followers_1.json 과 following.json 파일을 선택"),
        ]
        for badge, desc in steps:
            row = tk.Frame(win, bg=CARD, highlightbackground=BORDER,
                           highlightthickness=1)
            row.pack(fill="x", padx=20, pady=4)

            tk.Label(row, text=badge, bg=ACCENT, fg=TEXT,
                     font=FONT_LABEL, padx=8, pady=6).pack(side="left")
            tk.Label(row, text=desc, bg=CARD, fg=TEXT,
                     font=FONT_LABEL, justify="left",
                     wraplength=380, padx=10).pack(side="left", pady=6)

        tk.Label(win,
                 text="⚠️ 데이터 요청 후 이메일 수신까지 최대 48시간 소요될 수 있습니다.",
                 bg=BG, fg=GOLD, font=FONT_LABEL, wraplength=440).pack(
                     pady=12, padx=20)

        HoverButton(win, "닫기", command=win.destroy,
                    bg=ACCENT, fg=TEXT, hover_bg=ACCENT2,
                    padx=20, pady=8).pack(pady=(0, 16))


if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramUnfollowerTracker(root)
    root.mainloop()
