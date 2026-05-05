import math
import random
import tkinter as tk
from tkinter import ttk


WIN_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


class TicTacToeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.geometry("520x680")
        self.root.minsize(520, 680)
        self.root.configure(bg="#0B1020")

        self.board = [""] * 9
        self.player_symbol = "X"
        self.computer_symbol = "O"
        self.game_over = False
        self.current_turn = "player"
        self.pending_ai_job: str | None = None
        self.difficulty = tk.StringVar(value="Medium")
        self.scores = {"player": 0, "computer": 0, "draw": 0}

        self.buttons: list[tk.Button] = []
        self.status_var = tk.StringVar(value="Your turn")
        self.player_score_var = tk.StringVar(value="0")
        self.computer_score_var = tk.StringVar(value="0")
        self.draw_score_var = tk.StringVar(value="0")

        self._setup_styles()
        self._build_ui()
        self.new_round()

    def _setup_styles(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure(
            "Modern.TCombobox",
            fieldbackground="#0F172A",
            background="#0F172A",
            foreground="#E2E8F0",
            arrowcolor="#E2E8F0",
            bordercolor="#334155",
            lightcolor="#334155",
            darkcolor="#334155",
            insertcolor="#E2E8F0",
        )
        style.map(
            "Modern.TCombobox",
            fieldbackground=[("readonly", "#0F172A")],
            selectbackground=[("readonly", "#1E293B")],
            selectforeground=[("readonly", "#E2E8F0")],
            foreground=[("readonly", "#E2E8F0")],
        )

    def _build_ui(self) -> None:
        container = tk.Frame(self.root, bg="#0B1020")
        container.pack(expand=True, fill="both", padx=22, pady=22)

        title = tk.Label(
            container,
            text="TIC TAC TOE",
            font=("Segoe UI Semibold", 30),
            fg="#F8FAFC",
            bg="#0B1020",
        )
        title.pack(anchor="w", pady=(0, 6))

        subtitle = tk.Label(
            container,
            text="Play against computer AI",
            font=("Segoe UI", 12),
            fg="#94A3B8",
            bg="#0B1020",
        )
        subtitle.pack(anchor="w", pady=(0, 16))

        card = tk.Frame(container, bg="#111827", bd=0, highlightthickness=0)
        card.pack(fill="both", expand=True)

        controls = tk.Frame(card, bg="#111827")
        controls.pack(fill="x", padx=18, pady=(18, 12))

        diff_label = tk.Label(
            controls,
            text="Difficulty",
            font=("Segoe UI Semibold", 11),
            fg="#CBD5E1",
            bg="#111827",
        )
        diff_label.grid(row=0, column=0, sticky="w", padx=(0, 10))

        diff_combo = ttk.Combobox(
            controls,
            textvariable=self.difficulty,
            state="readonly",
            values=("Very Easy", "Easy", "Medium", "Hard", "Impossible"),
            width=12,
            font=("Segoe UI", 11),
            style="Modern.TCombobox",
        )
        diff_combo.grid(row=0, column=1, sticky="w")
        diff_combo.bind("<<ComboboxSelected>>", lambda _: self.new_round())

        new_btn = tk.Button(
            controls,
            text="New Round",
            command=self.new_round,
            font=("Segoe UI Semibold", 10),
            fg="#FFFFFF",
            bg="#2563EB",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
        )
        new_btn.grid(row=0, column=2, padx=(14, 8))

        reset_btn = tk.Button(
            controls,
            text="Reset Score",
            command=self.reset_scores,
            font=("Segoe UI Semibold", 10),
            fg="#D1D5DB",
            bg="#1F2937",
            activebackground="#374151",
            activeforeground="#F8FAFC",
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
        )
        reset_btn.grid(row=0, column=3)

        controls.grid_columnconfigure(4, weight=1)

        self.status_label = tk.Label(
            card,
            textvariable=self.status_var,
            font=("Segoe UI", 13),
            fg="#E2E8F0",
            bg="#111827",
        )
        self.status_label.pack(anchor="w", padx=18, pady=(0, 12))

        board_frame = tk.Frame(card, bg="#111827")
        board_frame.pack(padx=18, pady=(0, 14))

        for row in range(3):
            board_frame.grid_rowconfigure(row, weight=1)
            board_frame.grid_columnconfigure(row, weight=1)

        for idx in range(9):
            button = tk.Button(
                board_frame,
                text="",
                font=("Segoe UI Semibold", 35),
                width=3,
                height=1,
                fg="#E2E8F0",
                bg="#1E293B",
                activeforeground="#E2E8F0",
                activebackground="#334155",
                relief="flat",
                bd=0,
                highlightthickness=0,
                cursor="hand2",
                command=lambda i=idx: self.on_player_move(i),
            )
            button.grid(row=idx // 3, column=idx % 3, padx=7, pady=7, ipadx=8, ipady=12)
            button.bind("<Enter>", lambda _, i=idx: self.on_hover(i, True))
            button.bind("<Leave>", lambda _, i=idx: self.on_hover(i, False))
            self.buttons.append(button)

        score_frame = tk.Frame(card, bg="#111827")
        score_frame.pack(fill="x", padx=18, pady=(4, 18))

        self._score_box(score_frame, "You", self.player_score_var, "#38BDF8", 0)
        self._score_box(score_frame, "Computer", self.computer_score_var, "#FB923C", 1)
        self._score_box(score_frame, "Draws", self.draw_score_var, "#A78BFA", 2)

    def _score_box(
        self, parent: tk.Widget, label: str, value_var: tk.StringVar, accent: str, column: int
    ) -> None:
        box = tk.Frame(parent, bg="#0F172A", bd=0, highlightthickness=1, highlightbackground="#1E293B")
        box.grid(row=0, column=column, sticky="nsew", padx=6, ipadx=12, ipady=6)
        parent.grid_columnconfigure(column, weight=1)

        title = tk.Label(
            box,
            text=label,
            font=("Segoe UI", 10),
            fg="#94A3B8",
            bg="#0F172A",
        )
        title.pack()

        value = tk.Label(
            box,
            textvariable=value_var,
            font=("Segoe UI Semibold", 20),
            fg=accent,
            bg="#0F172A",
        )
        value.pack()

    def on_hover(self, index: int, enter: bool) -> None:
        if self.game_over or self.board[index]:
            return
        self.buttons[index].configure(bg="#334155" if enter else "#1E293B")

    def new_round(self) -> None:
        if self.pending_ai_job is not None:
            self.root.after_cancel(self.pending_ai_job)
            self.pending_ai_job = None

        self.board = [""] * 9
        self.game_over = False
        for button in self.buttons:
            button.configure(
                text="",
                bg="#1E293B",
                fg="#E2E8F0",
                disabledforeground="#E2E8F0",
                state="normal",
                cursor="hand2",
            )

        self.current_turn = random.choice(("player", "computer"))
        if self.current_turn == "player":
            self.status_var.set("Your turn. You start.")
            return

        self.status_var.set("Computer starts...")
        self._schedule_computer_move(delay_ms=450)

    def reset_scores(self) -> None:
        self.scores = {"player": 0, "computer": 0, "draw": 0}
        self._refresh_score_labels()
        self.new_round()

    def on_player_move(self, index: int) -> None:
        if self.game_over or self.current_turn != "player" or self.board[index]:
            return

        self._place_symbol(index, self.player_symbol)
        if self._resolve_round(last_actor="player"):
            return

        self.current_turn = "computer"
        self.status_var.set("Computer is thinking...")
        self._schedule_computer_move()

    def on_computer_move(self) -> None:
        self.pending_ai_job = None
        if self.game_over or self.current_turn != "computer":
            return
        move = self._select_move()
        if move is None:
            return
        self._place_symbol(move, self.computer_symbol)
        if self._resolve_round(last_actor="computer"):
            return
        self.current_turn = "player"

    def _schedule_computer_move(self, delay_ms: int = 350) -> None:
        if self.pending_ai_job is not None:
            self.root.after_cancel(self.pending_ai_job)
        self.pending_ai_job = self.root.after(delay_ms, self.on_computer_move)

    def _place_symbol(self, index: int, symbol: str) -> None:
        self.board[index] = symbol
        color = "#38BDF8" if symbol == self.player_symbol else "#FB923C"
        self.buttons[index].configure(
            text=symbol,
            fg=color,
            disabledforeground=color,
            bg="#0F172A",
            state="disabled",
            cursor="arrow",
        )

    def _resolve_round(self, last_actor: str) -> bool:
        winner, winning_line = self._winner_and_line(self.board)
        if winner:
            self.game_over = True
            if winning_line:
                for idx in winning_line:
                    self.buttons[idx].configure(bg="#14532D")
            if winner == self.player_symbol:
                self.scores["player"] += 1
                self.status_var.set("You win this round!")
            else:
                self.scores["computer"] += 1
                self.status_var.set("Computer wins this round.")
            self._refresh_score_labels()
            self._lock_board()
            return True

        if self._is_draw(self.board):
            self.game_over = True
            self.scores["draw"] += 1
            self.status_var.set("Draw. No winner this round.")
            self._refresh_score_labels()
            self._lock_board()
            return True

        if last_actor == "player":
            self.status_var.set("Computer is thinking...")
        else:
            self.status_var.set("Your turn")
        return False

    def _lock_board(self) -> None:
        for idx, button in enumerate(self.buttons):
            if not self.board[idx]:
                button.configure(state="disabled", cursor="arrow")

    def _refresh_score_labels(self) -> None:
        self.player_score_var.set(str(self.scores["player"]))
        self.computer_score_var.set(str(self.scores["computer"]))
        self.draw_score_var.set(str(self.scores["draw"]))

    def _select_move(self) -> int | None:
        moves = self._available_moves(self.board)
        if not moves:
            return None

        difficulty = self.difficulty.get()
        if difficulty == "Very Easy":
            return random.choice(moves)
        if difficulty == "Easy":
            return self._easy_move()
        if difficulty == "Medium":
            return self._medium_move()
        if difficulty == "Hard":
            return self._hard_move(mistake_chance=0.18)
        return self._hard_move()

    def _easy_move(self) -> int:
        moves = self._available_moves(self.board)
        if not moves:
            raise ValueError("No moves available for easy AI.")

        if random.random() < 0.70:
            return random.choice(moves)

        winning = self._find_winning_move(self.board, self.computer_symbol)
        if winning is not None and random.random() < 0.70:
            return winning

        block = self._find_winning_move(self.board, self.player_symbol)
        if block is not None and random.random() < 0.45:
            return block

        if 4 in moves and random.random() < 0.45:
            return 4

        corners = [m for m in moves if m in (0, 2, 6, 8)]
        if corners and random.random() < 0.50:
            return random.choice(corners)

        return random.choice(moves)

    def _medium_move(self) -> int:
        moves = self._available_moves(self.board)
        if not moves:
            raise ValueError("No moves available for medium AI.")

        if random.random() > 0.72:
            return random.choice(moves)

        winning = self._find_winning_move(self.board, self.computer_symbol)
        if winning is not None:
            return winning

        block = self._find_winning_move(self.board, self.player_symbol)
        if block is not None:
            return block

        if 4 in moves:
            return 4

        corners = [m for m in moves if m in (0, 2, 6, 8)]
        if corners:
            return random.choice(corners)

        return random.choice(moves)

    def _hard_move(self, mistake_chance: float = 0.0) -> int:
        scored_moves = self._scored_moves()
        if not scored_moves:
            raise ValueError("Hard AI failed to evaluate any move.")

        best_score = scored_moves[0][1]
        best_moves = [move for move, score in scored_moves if score == best_score]
        best_move = random.choice(best_moves)

        if mistake_chance > 0 and random.random() < mistake_chance:
            alternatives = [move for move, score in scored_moves if move != best_move and score >= best_score - 2]
            if alternatives:
                return random.choice(alternatives)

        return best_move

    def _scored_moves(self) -> list[tuple[int, int]]:
        scored_moves: list[tuple[int, int]] = []
        for move in self._available_moves(self.board):
            self.board[move] = self.computer_symbol
            score = self._minimax(self.board, False, -math.inf, math.inf, 0)
            self.board[move] = ""
            scored_moves.append((move, score))
        scored_moves.sort(key=lambda item: item[1], reverse=True)
        return scored_moves

    def _minimax(
        self, board: list[str], is_maximizing: bool, alpha: float, beta: float, depth: int
    ) -> int:
        winner, _ = self._winner_and_line(board)
        if winner == self.computer_symbol:
            return 10 - depth
        if winner == self.player_symbol:
            return depth - 10
        if self._is_draw(board):
            return 0

        if is_maximizing:
            best = -math.inf
            for move in self._available_moves(board):
                board[move] = self.computer_symbol
                score = self._minimax(board, False, alpha, beta, depth + 1)
                board[move] = ""
                best = max(best, score)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
            return int(best)

        best = math.inf
        for move in self._available_moves(board):
            board[move] = self.player_symbol
            score = self._minimax(board, True, alpha, beta, depth + 1)
            board[move] = ""
            best = min(best, score)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return int(best)

    @staticmethod
    def _available_moves(board: list[str]) -> list[int]:
        return [idx for idx, value in enumerate(board) if not value]

    @staticmethod
    def _find_winning_move(board: list[str], symbol: str) -> int | None:
        for move in TicTacToeApp._available_moves(board):
            board[move] = symbol
            winner, _ = TicTacToeApp._winner_and_line(board)
            board[move] = ""
            if winner == symbol:
                return move
        return None

    @staticmethod
    def _winner_and_line(board: list[str]) -> tuple[str | None, tuple[int, int, int] | None]:
        for a, b, c in WIN_LINES:
            if board[a] and board[a] == board[b] == board[c]:
                return board[a], (a, b, c)
        return None, None

    @staticmethod
    def _is_draw(board: list[str]) -> bool:
        return all(square != "" for square in board)


def main() -> None:
    root = tk.Tk()
    TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
