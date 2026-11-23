# AI 종류: ChatGPT
# AI 사용 목적: 9팀 항공편 맞춤 공항 안내 프로그램의 설계 및 구현
# 사용한 AI 프롬프트: 이거 팀프로젝트 발표인데 8페이지에 나와있는 12주차 13주차 완성해야하는데 팀원을 역할 분담해서 각자 맡을 코드(파이썬으로만)를 주고 구현 까지 할 수 있는 코드를 짜주고 팀원(전재균,김기범,최민호,장태현)에게 각각 코드를 줘 그리고 우리 팀 깃허브의 커밋해서 통합하는 방법까지 알려줘
# 추가 AI 사용 목적: 기존 팀 화면에 T1 실시간 조회 버튼과 오류 표시 추가
# 추가 AI 프롬프트: 기존 공항 API를 우리 팀 Python 코드에 추가해서 다시 제공해 줘.
# 추가 AI 프롬프트: 그럼 시설 추천도 넣어줘 우리 팀프로젝트 파악해서 코드 다시 짜줘
# 추가 AI 사용 목적: 추천 시설의 종류와 위치를 표시하고 시연 데이터임을 안내
# AI 요청자: 장태현
# AI 사용 날짜: 2026-11-23

"""전재균 담당 — Tkinter 화면과 조회 버튼."""
from queue import Empty, Queue
from threading import Thread
import tkinter as tk
from tkinter import messagebox

from airport_api import fetch_t1_queues
from flights import find_flight
from recommendations import congestion_level, recommended_facilities


class AirportGuideApp:
    def __init__(self, root, flights, save_search):
        self.root = root
        self.flights = flights
        self.save_search = save_search
        root.title("항공편 맞춤 공항 안내")
        root.minsize(520, 430)

        frame = tk.Frame(root, padx=18, pady=14)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(9, weight=1)

        tk.Label(frame, text="항공편 맞춤 공항 안내",
                 font=("", 17, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w")
        tk.Label(frame, text="시연용 샘플 데이터 · 입력 예시 KE123").grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(2, 12))
        tk.Label(frame, text="항공편명").grid(row=2, column=0, sticky="w")
        self.entry = tk.Entry(frame)
        self.entry.grid(row=2, column=1, sticky="ew", padx=8)
        self.entry.bind("<Return>", self.search)
        self.entry.focus_set()
        tk.Button(frame, text="항공편 조회", command=self.search).grid(
            row=2, column=2, sticky="e")

        self.results = {}
        labels = ["항공편", "항공사 · 목적지", "이용 터미널",
                  "보안검색대", "예상 대기시간"]
        for row, label in enumerate(labels, start=3):
            tk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=2)
            value = tk.StringVar(value="—")
            tk.Label(frame, textvariable=value).grid(
                row=row, column=1, columnspan=2, sticky="w", padx=8)
            self.results[label] = value

        tk.Label(frame, text="15분 이상 대기 시 주변 시설 추천 (시연용)").grid(
            row=8, column=0, columnspan=3, sticky="w", pady=(8, 2))
        self.facility_list = tk.Listbox(frame, height=4)
        self.facility_list.grid(row=9, column=0, columnspan=3, sticky="nsew")

        tk.Label(
            frame, text="탑승 시간과 공항 안내를 확인한 뒤 시설을 이용하세요.",
            wraplength=440, justify="left"
        ).grid(row=10, column=0, columnspan=3, sticky="w", pady=(4, 0))

        self.live_button = tk.Button(
            frame, text="T1 실시간 대기 인원 조회", command=self.load_live_queues)
        self.live_button.grid(row=11, column=0, columnspan=3, sticky="w", pady=(10, 2))
        self.live_status = tk.StringVar(value="실시간 조회 버튼을 눌러 주세요.")
        tk.Label(frame, textvariable=self.live_status, wraplength=430,
                 justify="left").grid(row=12, column=0, columnspan=3, sticky="w")

    def load_live_queues(self):
        self.live_button.config(state="disabled")
        self.live_status.set("T1 실시간 대기 인원 조회 중…")
        results = Queue()

        def request():
            try:
                rows = fetch_t1_queues()
                results.put(" · ".join(f"{gate}: {count}명" for gate, count in rows))
            except ValueError as error:
                results.put(str(error))

        def show_result():
            try:
                message = results.get_nowait()
            except Empty:
                self.root.after(100, show_result)
                return
            self.live_status.set(message)
            self.live_button.config(state="normal")

        Thread(target=request, daemon=True).start()
        self.root.after(100, show_result)


    def search(self, event=None):
        for value in self.results.values():
            value.set("—")
        self.facility_list.delete(0, tk.END)

        number = self.entry.get().strip()
        if not number:
            messagebox.showwarning("입력 확인", "항공편명을 입력하세요.")
            return

        flight = find_flight(self.flights, number)
        if flight is None:
            messagebox.showwarning("조회 결과 없음", "샘플 목록에 없는 항공편입니다.")
            return

        level = congestion_level(flight.wait_time)
        facilities = recommended_facilities(flight)
        self.results["항공편"].set(flight.number)
        self.results["항공사 · 목적지"].set(f"{flight.airline} · {flight.destination}")
        self.results["이용 터미널"].set(flight.terminal)
        self.results["보안검색대"].set(flight.checkpoint)
        self.results["예상 대기시간"].set(f"{flight.wait_time}분 · {level} (시연용)")

        if facilities:
            for number, facility in enumerate(facilities, start=1):
                self.facility_list.insert(tk.END, f"{number}. {facility}")
        elif flight.wait_time >= 15:
            self.facility_list.insert(tk.END, "등록된 주변 시설이 없습니다.")
        else:
            self.facility_list.insert(tk.END, "대기시간이 15분 미만입니다.")

        try:
            self.save_search(flight, level, facilities)
        except (OSError, ValueError) as error:
            messagebox.showerror("기록 저장 실패", str(error))
