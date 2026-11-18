"""
=============================================================================
[AI 사용 주석 - 학교 제출 양식 필수 준수]
- 사용 AI 종류: Google Gemini (개인 AI collaborator)
- 사용 목적: 2026-2 프로그래밍 II 지정 프로젝트 모듈 2 비즈니스 로직(CRUD, BMI, 통계) 구현 지원
- 사용 프롬프트: "PDF 요구사항(생년, 성별, 비만도 상태, 식별번호 자동생성)을 반영하여
                초등학생도 이해할 수 있도록 주석을 상세히 단 파이썬 코드를 작성해줘."
- 작성자 / 작성일: 전재균 (2026년 11월)
=============================================================================
"""

import math
import os


class HealthRecord:
  """[데이터 모델 클래스]
  사람 한 명의 인적 사항과 건강 정보를 담는 '알록달록한 이름표 카드' 같은 역할입니다.
  """

  def __init__(self, record_id, name, birth_year, gender, height, weight):
    self.record_id = record_id  # 환자 식별번호 (예: P2026-0001)
    self.name = name  # 이름
    self.birth_year = birth_year  # 생년 (출생 연도)
    self.gender = gender  # 성별 (남/여)
    self.height = height  # 키 (cm)
    self.weight = weight  # 몸무게 (kg)
    self.bmi = self.calculate_bmi()  # BMI 수치 자동 계산
    self.status = self.evaluate_status()  # 비만도 상태 자동 판정

  def calculate_bmi(self):
    """키와 몸무게를 이용해 BMI 지수를 계산하는 공식 메서드"""
    if self.height <= 0:
      return 0.0
    height_m = self.height / 100.0  # cm를 m로 변환
    return round(self.weight / (height_m ** 2), 2)  # 소수점 둘째 자리까지 반올림

  def evaluate_status(self):
    """계산된 BMI 수치를 바탕으로 비만도 상태를 판정하는 메서드"""
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
    """파일 저장 등을 위해 데이터를 딕셔너리 형태로 변환하는 메서드"""
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
    """객체를 출력할 때 보기 좋은 문자열 형태로 반환"""
    return (
        f"ID: {self.record_id} | 이름: {self.name} | 생년: {self.birth_year}"
        f" | 성별: {self.gender} | 키: {self.height}cm | 몸무게:"
        f" {self.weight}kg | BMI: {self.bmi} ({self.status})"
    )


class HealthManager:
  """[비즈니스 로직 및 데이터 관리 클래스]
  GUI나 콘솔 화면과 직접 소통하지 않고, 오직 메모리 안에서 데이터(카드들)를
  추가, 조회, 수정, 삭제, 통계 계산하는 '총괄 매니저' 역할입니다.
  """

  def __init__(self):
    self.records = []  # 건강 정보 카드들을 모아두는 빈 리스트 상자
    self._sequence = 1  # 환자 식별번호를 순서대로 만들기 위한 번호표

  def generate_id(self):
    """고유한 환자 식별번호(예: P2026-0001 형식)를 자동으로 생성하는 메서드"""
    new_id = f"P2026-{self._sequence:04d}"
    self._sequence += 1
    return new_id

  def check_duplicate(self, name, birth_year):
    """이름과 생년이 같은 사람이 이미 존재하는지 검사하는 중복 체크 메서드"""
    for r in self.records:
      if r.name == name and r.birth_year == birth_year:
        return True  # 중복 있음
    return False  # 중복 없음

  def add_record(self, name, birth_year, gender, height, weight):
    """신규 건강 정보 레코드를 생성하여 리스트에 추가하는 메서드"""
    # 중복 체크 로직
    if self.check_duplicate(name, birth_year):
      return None, "이미 등록된 사용자(이름과 생년 일치)입니다."

    record_id = self.generate_id()
    record = HealthRecord(
        record_id, name, birth_year, gender, height, weight
    )
    self.records.append(record)
    return record, "성공적으로 등록되었습니다."

  def get_all_records(self):
    """등록된 모든 건강 정보 목록을 반환"""
    return self.records

  def get_record_by_id(self, record_id):
    """특정 식별번호(ID)를 가진 레코드를 검색하여 반환"""
    for r in self.records:
      if r.record_id == record_id:
        return r
    return None

  def update_record(self, record_id, name, birth_year, gender, height, weight):
    """특정 레코드의 정보를 수정하고 BMI 및 비만도 상태를 자동 재계산"""
    r = self.get_record_by_id(record_id)
    if r:
      r.name = name
      r.birth_year = birth_year
      r.gender = gender
      r.height = height
      r.weight = weight
      r.bmi = r.calculate_bmi()  # 키/몸무게 변경 시 BMI 자동 재계산
      r.status = (
          r.evaluate_status()
      )  # BMI 변경에 따른 비만도 상태 자동 재계산
      return True
    return False

  def delete_record(self, record_id):
    """특정 식별번호의 레코드를 삭제"""
    r = self.get_record_by_id(record_id)
    if r:
      self.records.remove(r)
      return True
    return False

  def calculate_statistics(self):
    """전체 인원수, 키/몸무게/BMI 평균 및 표준편차를 연산하는 통계 메서드"""
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
  """[콘솔 인터페이스(TUI) 메인 함수]
  사용자와 직접 상호작용하며 메뉴를 보여주고 입력을 받는 조종 장치 역할입니다.
  """
  manager = HealthManager()

  while True:
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
      print("\n[1. 건강정보 등록]")
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
      print("\n[2. 전체 목록 조회]")
      records = manager.get_all_records()
      if not records:
        print("-> 등록된 데이터가 없습니다.")
      else:
        for r in records:
          print(f"  - {r}")

    elif choice == "3":
      print("\n[3. 상세 검색]")
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
      print("\n[4. 정보 수정]")
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
      print("\n[5. 레코드 삭제]")
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
      print("\n[6. 통계 정보 조회]")
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
      print("\n프로그램을 종료합니다. 수고하셨습니다!")
      break
    else:
      print("\n-> 올바른 메뉴 번호를 선택해주세요.")


if __name__ == "__main__":
  main()