#!/usr/bin/env python3
"""
Agent Avengers - Custom Exceptions
커스텀 예외 클래스 정의
"""


class AvengersError(Exception):
    """Avengers 기본 예외 클래스"""
    pass


class MissionNotFoundError(AvengersError):
    """미션을 찾을 수 없을 때 발생"""
    pass


class PlanNotFoundError(AvengersError):
    """실행 계획을 찾을 수 없을 때 발생"""
    pass


class InvalidMissionError(AvengersError):
    """유효하지 않은 미션 데이터일 때 발생"""
    pass
