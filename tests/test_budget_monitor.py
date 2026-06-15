"""Tests for budget monitor."""

from acquisition_helper.control.budget_monitor import BudgetMonitor
from acquisition_helper.control.profiles import ControlProfileName, get_profile


def test_budget_monitor_ceiling_from_profile():
    monitor = BudgetMonitor(profile=get_profile(ControlProfileName.CONSERVATIVE))
    assert monitor.ceiling == 200_000


def test_budget_monitor_exceeds_ceiling():
    monitor = BudgetMonitor(profile=get_profile(ControlProfileName.CONSERVATIVE))
    monitor.record(total=250_000)
    assert monitor.exceeds_ceiling()
    assert monitor.requires_hitl()


def test_budget_preflight():
    monitor = BudgetMonitor(profile=get_profile(ControlProfileName.CONSERVATIVE))
    assert monitor.preflight_ok(100_000)
    assert not monitor.preflight_ok(300_000)


def test_budget_monitor_unlimited_default():
    monitor = BudgetMonitor(profile=get_profile(ControlProfileName.STANDARD))
    assert monitor.ceiling is None
    assert monitor.is_unlimited
    monitor.record(total=10_000_000)
    assert not monitor.exceeds_ceiling()
    assert not monitor.requires_hitl()
    assert monitor.preflight_ok(10_000_000)
