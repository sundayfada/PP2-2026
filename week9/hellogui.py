"""
=============================================================================
[AI 사용 주석 - 학교 제출 양식 필수 준수]
- 사용 AI 종류: Google Gemini (개인 AI collaborator)
- 사용 목적: 2026-2 프로그래밍 II 지정 프로젝트 모듈 2 비즈니스 로직(CRUD, BMI, 통계) 구현 지원
- 사용 프롬프트: "PDF 요구사항(생년, 성별, 비만도 상태, 식별번호 자동생성)을 반영하고,
                카드마술 비유를 곁들인 상세 주석을 단 파이썬 코드를 작성해줘."
- 작성자 / 작성일: 전재균 (2026년 11월)
=============================================================================
"""

import math
import os


class HealthRecord:
  """[1번 마술 도구: 관객 한 명의 '특별한 카드']
  사람 한 명의 인적 사항과 키, 몸무게, BMI 정보를 담고 있는 카드 한 장입니다.
  """

  def __init__(self, record_id, name, birth_year, gender, height, weight):
    self.record_id = record_id  # 관객 식별 번호 (예: P2026-0001)
    self.name = name  # 관객 이름
    self.birth_year = birth_year  # 태어난 연도
    self.gender = gender  # 성별 (남/여)
    self.height = height  # 키 (cm)
    self.weight = weight  # 몸무게 (kg)
    self.bmi = self.calculate_bmi()  # 카드가 만들어질 때 자동으로 BMI 계산!
    self.status = self.evaluate_status()  # 자동으로 비만도 상태 판정!

  def calculate_bmi(self):
    """키와 몸무게를 이용해 BMI 지수를 계산하는 마법의 공식"""
    if self.height <= 0:
      return 0.0
    height_m = self.height / 100.0  # cm를 m 단위로 변환
    return round(self.weight / (height_m ** 2), 2)  # 소수점 둘째 자리까지 반올림

  def evaluate_status(self):
    """계산된 BMI 숫자를 보고 비만도 상태 도장을 찍어주는 메서드"""
    if self.bmi == 0:
      return "알 수 없음"
    elif self.bmi < 18.5:
      return "저체중"
    elif 18.5 <= self.bmi < 23:
      return "정상"
    elif 23 <= self.bmi < 25:
      return "과체중"
    else:
      return "비만"

  def to_dict(self):
    """나중에 파일에 저장하기 위해 데이터를 딕셔너리 형태로 변환"""
    return {
        "id": self.record_id,
        "name": self.name,
        "birth_year": self.birth_year,
        "gender": self.gender,
        "height": self.height,
        "weight": self.weight,
        "bmi": self.bmi,
        "status": self.status,
    }

  def __str__(self):
    """카드를 화면에 보기 좋은 문자열 형태로 보여줌"""
    return (
        f"ID: {self.record_id} | 이름: {self.name} | 생년: {self.birth_year}"
        f" | 성별: {self.gender} | 키: {self.height}cm | 몸무게:"
        f" {self.weight}kg | BMI: {self.bmi} ({self.status})"
    )


class HealthManager:
  """[2번 마술 도구: 마술사의 손과 '카드 덱 박스']
  화면과 직접 소통하지 않고, 메모리 안에서 카드들을 모아두고
  추가·검색·수정·삭제·통계 마술을 부리는 총괄 매니저입니다.
  """

  def __init__(self):
    self.records = []  # 카드들을 안전하게 모아두는 덱 상자 (리스트)
    self._sequence = 1  # 관객 번호표를 차례대로 발급하기 위한 숫자

  def generate_id(self):
    """덱에 카드가 들어올 때마다 P2026-0001 형태로 고유 번호를 자동 발급"""
    new_id = f"P2026-{self._sequence:04d}"
    self._sequence += 1
    return new_id

  def check_duplicate(self, name, birth_year):
    """이름과 생년이 똑같은 관객이 이미 덱에 있는지 검사 (중복 체크)"""
    for r in self.records:
      if r.name == name and r.birth_year == birth_year:
        return True  # 이미 존재함 (중복)
    return False  # 처음 온 관객임

  def add_record(self, name, birth_year, gender, height, weight):
    """새로운 관객 카드를 만들어 덱 상자에 추가하는 메서드"""
    # 중복 체크 먼저 수행
    if self.check_duplicate(name, birth_year):
      return None, "이미 등록된 사용자(이름과 생년 일치)입니다."

    record_id = self.generate_id()
    record = HealthRecord(
        record_id, name, birth_year, gender, height, weight
    )
    self.records.append(record)  # 덱에 카드 추가
    return record, "성공적으로 등록되었습니다."

  def get_all_records(self):
    """덱에 있는 모든 카드 목록을 반환"""
    return self.records

  def get_record_by_id(self, record_id):
    """특정 ID 번호를 가진 카드를 덱 속에서 찾아냄"""
    for r in self.records:
      if r.record_id == record_id:
        return r
    return None

  def update_record(self, record_id, name, birth_year, gender, height, weight):
    """특정 카드의 정보를 수정하고 BMI와 비만도 상태를 즉시 재계산"""
    r = self.get_record_by_id(record_id)
    if r:
      r.name = name
      r.birth_year = birth_year
      r.gender = gender
      r.height = height
      r.weight = weight
      r.bmi = r.calculate_bmi()  # 수정된 키/몸무게로 BMI 다시 계산
      r.status = r.evaluate_status()  # 비만도 상태도 다시 판정
      return True
    return False

  def delete_record(self, record_id):
    """특정 ID 카드를 덱 상자에서 빼내어 버림 (삭제)"""
    r = self.get_record_by_id(record_id)
    if r:
      self.records.remove(r)
      return True
    return False

  def calculate_statistics(self):
    """덱에 있는 모든 카드의 키, 몸무게, BMI 평균과 표준편차를 계산"""
    count = len(self.records)
    if count == 0:
      return None

    heights = [r.height for r in self.records]
    weights = [r.weight for r in self.records]
    bmis = [r.bmi for r in self.records]

    def mean(lst):
      return sum(lst) / len(lst)

    def std_dev(lst, m):
      if len(lst) <= 1:
        return 0.0
      variance = sum((x - m) ** 2 for x in lst) / len(lst)
      return math.sqrt(variance)

    h_mean = mean(heights)
    w_mean = mean(weights)
    b_mean = mean(bmis)

    return {
        "count": count,
        "height_mean": round(h_mean, 2),
        "height_std": round(std_dev(heights, h_mean), 2),
        "weight_mean": round(w_mean, 2),
        "weight_std": round(std_dev(weights, w_mean), 2),
        "bmi_mean": round(b_mean, 2),
        "bmi_std": round(std_dev(bmis, b_mean), 2),
    }


def main():
  """[3번 마술쇼 진행 무대: 콘솔 인터페이스(TUI) 메인 함수]
  관객(사용자)과 직접 마이크를 잡고 대화하며 메뉴를 보여주는 조종 장치입니다.
  """
  manager = HealthManager()  # 마술사 매니저 고용!

  while True:  # 0번(종료)을 누르기 전까지 쇼를 계속 진행하는 반복문
    print("\n  =========================================")
    print("      000 건강정보 관리 시스템 (모듈 2)      ")
    print("  =========================================")
    print("  1. 건강정보 등록 (중복체크 및 ID자동생성)")
    print("  2. 전체 목록 조회")
    print("  3. 상세 검색 (ID 조회)")
    print("  4. 정보 수정 (BMI 자동 재계산)")
    print("  5. 레코드 삭제")
    print("  6. 통계 정보 조회")
    print("  0. 프로그램 종료")
    print("  -----------------------------------------")

    choice = input("  메뉴 선택: ").strip()

    if choice == "1":
      print("\n[1. 건강정보 등록 마술]")
      name = input("이름: ").strip()
      try:
        birth_year = int(input("생년 (예: 1995): "))
        gender = input("성별 (남/여): ").strip()
        height = float(input("키(cm): "))
        weight = float(input("몸무게(kg): "))

        rec, msg = manager.add_record(
            name, birth_year, gender, height, weight
        )
        print(f"-> {msg}")
        if rec:
          print(f"   [발급된 카드 정보] {rec}")
      except ValueError:
        print("-> 오류: 생년, 키, 몸무게는 올바른 숫자로 입력해주세요.")

    elif choice == "2":
      print("\n[2. 전체 목록 조회 마술]")
      records = manager.get_all_records()
      if not records:
        print("-> 등록된 데이터가 없습니다.")
      else:
        for r in records:
          print(f"  - {r}")

    elif choice == "3":
      print("\n[3. 상세 검색 마술]")
      r_id = input("조회할 환자 식별번호 입력 (예: P2026-0001): ").strip()
      r = manager.get_record_by_id(r_id)
      if r:
        print(f"\n  [상세 정보]")
        print(f"  - 식별번호: {r.record_id}")
        print(f"  - 이름: {r.name} ({r.birth_year}년생, {r.gender})")
        print(f"  - 신체정보: 키 {r.height}cm / 몸무게 {r.weight}kg")
        print(f"  - 건강상태: BMI {r.bmi} [{r.status}]")
      else:
        print("-> 해당 식별번호를 가진 데이터를 찾을 수 없습니다.")

    elif choice == "4":
      print("\n[4. 정보 수정 마술]")
      r_id = input("수정할 환자 식별번호 입력: ").strip()
      r = manager.get_record_by_id(r_id)
      if not r:
        print("-> 해당 식별번호의 데이터를 찾을 수 없습니다.")
        continue

      print(f"기존 정보 -> {r}")
      try:
        name = input("새로운 이름: ").strip()
        birth_year = int(input("새로운 생년: "))
        gender = input("새로운 성별 (남/여): ").strip()
        height = float(input("새로운 키(cm): "))
        weight = float(input("새로운 몸무게(kg): "))

        if manager.update_record(
            r_id, name, birth_year, gender, height, weight
        ):
          print("-> 수정 및 BMI 자동 재계산이 완료되었습니다.")
        else:
          print("-> 수정 실패")
      except ValueError:
        print("-> 오류: 올바른 숫자 형식을 입력해주세요.")

    elif choice == "5":
      print("\n[5. 레코드 삭제 마술]")
      r_id = input("삭제할 환자 식별번호 입력: ").strip()
      confirm = input(f"정말 {r_id}번 기록을 삭제하시겠습니까? (y/n): ").strip().lower()
      if confirm == "y":
        if manager.delete_record(r_id):
          print("-> 삭제가 완료되었습니다.")
        else:
          print("-> 삭제 실패: 해당하는 ID가 없습니다.")
      else:
        print("-> 삭제가 취소되었습니다.")

    elif choice == "6":
      print("\n[6. 통계 정보 산출 마술]")
      stats = manager.calculate_statistics()
      if not stats:
        print("-> 통계를 계산할 데이터가 없습니다.")
      else:
        print(f"  - 총 등록 인원: {stats['count']}명")
        print(
            f"  - 평균 키: {stats['height_mean']} cm (표준편차:"
            f" {stats['height_std']})"
        )
        print(
            f"  - 평균 몸무게: {stats['weight_mean']} kg (표준편차:"
            f" {stats['weight_std']})"
        )
        print(
            f"  - 평균 BMI: {stats['bmi_mean']} (표준편차: {stats['bmi_std']})"
        )

    elif choice == "0":
      print("\n마술쇼를 종료합니다. 수고하셨습니다!")
      break  # 쇼를 끝내는 탈출구
    else:
      print("\n-> 올바른 메뉴 번호를 선택해주세요.")


if __name__ == "__main__":
  main()