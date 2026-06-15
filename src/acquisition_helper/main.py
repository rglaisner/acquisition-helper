#!/usr/bin/env python
"""CLI entry point for Acquisition Helper."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from acquisition_helper.env import OUTPUT_DIR, REPORT_FILENAME, ensure_output_dir, validate_environment
from acquisition_helper.flow.acquisition_flow import run_flow
from acquisition_helper.models.intake import ControlProfileName, TierName, UserRequirements
from acquisition_helper.reporting.markdown_report import capture_console, configure_console_encoding, save_report


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Acquisition Helper — M&A research pipeline")
    parser.add_argument(
        "--tier",
        choices=[t.value for t in TierName],
        help="Agent tier (skips tier prompt in wizard)",
    )
    parser.add_argument(
        "--profile",
        choices=[p.value for p in ControlProfileName],
        help="Control profile",
    )
    parser.add_argument(
        "--skip-wizard",
        action="store_true",
        help="Use defaults.yaml without interactive intake",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Skip HITL approval gates (CI / automation)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Alias for --skip-wizard --non-interactive",
    )
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.yes:
        args.skip_wizard = True
        args.non_interactive = True

    log_buffer: list[str] = []
    script_path = Path(__file__).resolve()
    ensure_output_dir()
    report_path = OUTPUT_DIR / REPORT_FILENAME

    try:
        configure_console_encoding()
        validate_environment()

        prebuilt: UserRequirements | None = None
        if args.tier or args.profile:
            from acquisition_helper.config.loader import load_defaults

            defaults = load_defaults()
            defaults_block = defaults.get("defaults") or {}
            prebuilt = UserRequirements(
                strategic_intent=str(defaults.get("strategic_intent", "")).strip(),
                sector=str(defaults_block.get("sector", "")),
                geography=str(defaults_block.get("geography", "")),
                financial_constraints=str(defaults_block.get("financial_constraints", "")),
                candidate_count=int(defaults_block.get("candidate_count", 12)),
                tier=TierName(args.tier) if args.tier else TierName(str(defaults_block.get("tier", "standard"))),
                control_profile=(
                    ControlProfileName(args.profile)
                    if args.profile
                    else ControlProfileName(str(defaults_block.get("control_profile", "standard")))
                ),
            )

        with capture_console(log_buffer):
            state = run_flow(
                requirements=prebuilt,
                skip_wizard=args.skip_wizard or prebuilt is not None,
                non_interactive=args.non_interactive,
            )

        if state.cancelled:
            print("Run cancelled by user.", file=sys.stderr)
            return 130

        tier_label = state.requirements.tier.value if state.requirements else None
        save_report(
            report_path,
            log_buffer,
            state.crew_output,
            script_path=script_path,
            tier=tier_label,
            error_message=state.error_message,
        )
        print(f"Report saved to: {report_path}")
        if state.workflow_plan:
            print(f"Workflow plan: {OUTPUT_DIR / 'workflow_plan.md'}")
        return 0

    except KeyboardInterrupt:
        error_message = "Execution interrupted by user."
        print(f"\n{error_message}", file=sys.stderr)
        if log_buffer:
            save_report(
                report_path,
                log_buffer,
                None,
                script_path=script_path,
                error_message=error_message,
            )
        return 130

    except Exception as error:
        error_message = str(error)
        print(f"Fatal error: {error_message}", file=sys.stderr)
        if log_buffer:
            save_report(
                report_path,
                log_buffer,
                None,
                script_path=script_path,
                error_message=error_message,
            )
        return 1


if __name__ == "__main__":
    sys.exit(run())
