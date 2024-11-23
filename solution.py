import kociemba

def solve_rubik(state):
    """
    Giải Rubik bằng thư viện kociemba.
    """
    try:
        solution = kociemba.solve(state)
        return solution
    except Exception as e:
        print(f"Lỗi khi giải Rubik: {e}")
        return None