# 기본 에이전트 클래스
class Agent:
    # 초기화 메소드
    def __init__(self):
        pass

    # 행동을 선택하는 메소드
    def select_move(self, game_state):
        raise NotImplementedError()