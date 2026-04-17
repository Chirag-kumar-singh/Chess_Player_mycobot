from stockfish import Stockfish

engine = Stockfish(path="/usr/games/stockfish")
engine.set_skill_level(1)  # 0=easiest, 20=strongest
engine.set_fen_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

def show_board():
    fen = engine.get_fen_position()
    board = fen.split()[0]
    ranks = board.split("/")
    print()
    for i, rank in enumerate(ranks):
        row = f"  {8-i} "
        for c in rank:
            if c.isdigit():
                row += " . " * int(c)
            else:
                row += f" {c}"
        print(row)
    print("    a  b  c  d  e  f  g  h\n")

print("\nCHESS - You are WHITE, Engine is BLACK")
print("Engine Strength: 1 (0=easiest, 20=strongest)")
print("Type 'skill NUMBER' to change (e.g., skill 5)\n")
show_board()

while True:
    fen = engine.get_fen_position()
    is_white = fen.split()[1] == "w"
    
    if is_white:
        move = input("Your move: ").strip().lower()
        if move == "quit":
            break
        if move.startswith("skill "):
            try:
                skill = int(move.split()[1])
                if 0 <= skill <= 20:
                    engine.set_skill_level(skill)
                    print(f"Engine strength set to {skill}\n")
                else:
                    print("Skill must be 0-20\n")
            except:
                print("Usage: skill 5\n")
            continue
        if not engine.is_move_legal(move):
            print("Illegal!\n")
            continue
        engine.make_moves_from_current_position([move])
        print()
    else:
        best = engine.get_best_move()
        if not best:
            print("GAME OVER - No legal moves\n")
            break
        engine.make_moves_from_current_position([best])
        print(f"Engine: {best}\n")
    
    show_board()
