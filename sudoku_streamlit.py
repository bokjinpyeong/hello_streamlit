# -*- coding: utf-8 -*-
import streamlit as st
import random
import time
import pandas as pd

# st.session_state: 사용자의 행동에 따라 계속 바뀌는 '상태'를 저장합니다.
if 'board' not in st.session_state:
    st.session_state.board = None
    st.session_state.solution = None
    st.session_state.initial_board = None
    st.session_state.start_time = None
    st.session_state.message = ""
    st.session_state.all_attempts = {} # 모든 플레이어의 시도 기록을 저장 {'이름': [시간1, 시간2...]}
    st.session_state.top_rankings = [] # 상위 랭킹 표시용 리스트
    st.session_state.selected_player_for_graph = None # 그래프를 표시할 플레이어 이름

# --- 게임 로직 및 데이터 로딩 함수 ---

@st.cache_data
def get_base_board():
    """
    @st.cache_data: 앱 실행 중 변하지 않는 데이터를 캐시에 저장합니다.
    """
    base = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2], [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7], [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1], [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4], [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9]
    ]
    return base

def new_game(difficulty):
    """새로운 스도쿠 게임판을 생성하는 함수"""
    base = get_base_board()
    nums = random.sample(range(1, 10), 9)
    st.session_state.solution = [[nums[d-1] for d in row] for row in base]
    
    puzzle = [row[:] for row in st.session_state.solution]
    for i in range(9):
        for j in range(9):
            if random.random() < difficulty:
                puzzle[i][j] = 0
    
    st.session_state.board = puzzle
    st.session_state.initial_board = [row[:] for row in puzzle]
    st.session_state.start_time = time.time()
    st.session_state.message = ""

def update_top_rankings():
    """all_attempts에서 각 플레이어의 최고 기록을 뽑아 top_rankings를 업데이트합니다."""
    ranking_data = []
    for name, attempts in st.session_state.all_attempts.items():
        if attempts:
            best_time = min(attempts)
            ranking_data.append({'name': name, 'time': best_time})
    
    ranking_data.sort(key=lambda x: x['time'])
    st.session_state.top_rankings = ranking_data[:10]

def add_attempt(name, time_taken):
    """플레이어의 시도 기록을 추가하고 랭킹을 업데이트합니다."""
    if name not in st.session_state.all_attempts:
        st.session_state.all_attempts[name] = []
    st.session_state.all_attempts[name].append(time_taken)
    st.session_state.message = ""
    update_top_rankings()

# --- Streamlit UI 구성 ---

st.title("스도쿠 게임")

with st.sidebar:
    st.header("게임 설정")
    difficulty = st.slider("난이도 (빈 칸 비율)", 0.0, 0.9, 0.5, 0.1)
    if st.button("새 게임 시작"):
        new_game(difficulty)

    st.header("랭킹 (최고 기록)")
    if not st.session_state.top_rankings:
        st.write("아직 랭킹이 없습니다.")
    else:
        for i, record in enumerate(st.session_state.top_rankings):
            st.write(f"{i+1}. {record['name']} - {record['time']}초")
            
    st.header("기록 그래프 조회")
    player_names = list(st.session_state.all_attempts.keys())
    if player_names:
        selected_player = st.selectbox(
            "플레이어를 선택하세요.",
            options=["선택"] + player_names
        )
        st.session_state.selected_player_for_graph = selected_player
    else:
        st.write("조회할 기록이 없습니다.")

if st.session_state.board:
    st.header("게임판")
    for i in range(9):
        cols = st.columns(9)
        for j in range(9):
            cell_key = f"{i}-{j}"
            if st.session_state.initial_board[i][j] != 0:
                with cols[j]:
                    st.write(f"<p style='text-align: center; font-weight: bold; font-size: 20px;'>{st.session_state.board[i][j]}</p>", unsafe_allow_html=True)
            else:
                with cols[j]:
                    options = [""] + list(range(1, 10))
                    current_val = st.session_state.board[i][j]
                    default_index = options.index(current_val) if current_val in options else 0

                    user_input = st.selectbox(
                        "", options, index=default_index, key=cell_key, 
                        label_visibility="collapsed"
                    )
                    if user_input != "":
                        st.session_state.board[i][j] = int(user_input)
                    else:
                        st.session_state.board[i][j] = 0

    st.write("---")

    if st.button("정답 확인"):
        if any(0 in row for row in st.session_state.board):
            st.session_state.message = ("error", "아직 빈 칸이 남아있습니다.")
        elif st.session_state.board == st.session_state.solution:
            elapsed_time = round(time.time() - st.session_state.start_time)
            st.session_state.message = ("success", elapsed_time)
        else:
            st.session_state.message = ("error", "틀렸습니다. 다시 확인해보세요.")
            
    if st.session_state.message:
        msg_type, msg_payload = st.session_state.message
        if msg_type == "error":
            st.error(msg_payload)
        elif msg_type == "success":
            elapsed_time = msg_payload
            st.success(f"축하합니다! 정답입니다! 기록: {elapsed_time}초")
            
            name = st.text_input("랭킹에 등록할 이름을 입력하세요:")
            if st.button("랭킹 등록"):
                if name:
                    add_attempt(name, elapsed_time)
                    st.rerun()
                else:
                    st.warning("이름을 입력해야 등록할 수 있습니다.")

    # 기록 그래프 표시
    selected_player = st.session_state.get('selected_player_for_graph')
    if selected_player and selected_player != "선택":
        attempts = st.session_state.all_attempts.get(selected_player, [])
        if attempts:
            st.write("---")
            st.header(f"'{selected_player}'님의 기록 변화")
            chart_data = pd.DataFrame({
                '기록(초)': attempts
            })
            # x축을 1부터 시작하는 정수 인덱스로 설정
            chart_data.index = range(1, len(attempts) + 1)
            chart_data.index.name = "시도"
            
            st.line_chart(chart_data)

else:
    st.info("왼쪽 사이드바에서 '새 게임 시작' 버튼을 눌러 게임을 시작하세요.")

