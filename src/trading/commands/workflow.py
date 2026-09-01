"""Workflow CLI command handler."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from trading.workflow.authoring import (
    ClearSafetyAssessmentRequest,
    CreateChangeRequest,
    CreateWorkflowRequest,
    EvolveWorkflowRequest,
    OpenSafetyAssessmentRequest,
    WorkflowAuthoringError,
    WorkflowRepository,
)
from trading.workflow.control_state import (
    WorkflowControlStateResult,
    evaluate_workflow_control_state,
)
from trading.workflow.studies import WorkflowStudyService


def register_parser(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register the tracked workflow command tree."""
    workflow = subparsers.add_parser(
        "workflow", help="Validate and transition tracked research workflow definitions"
    )
    workflow.add_argument(
        "--root", type=Path, default=Path("workflows"), help="Tracked workflow registry root"
    )
    commands = workflow.add_subparsers(dest="workflow_command", required=True)
    create = commands.add_parser("create", help="Create an initial workflow-family draft")
    create.add_argument("--request", type=Path, required=True)
    create.add_argument("--dry-run", action="store_true")
    evolve = commands.add_parser("evolve", help="Build the next draft from accepted changes")
    evolve.add_argument("--request", type=Path, required=True)
    evolve.add_argument("--dry-run", action="store_true")
    validate = commands.add_parser("validate", help="Validate tracked workflow evidence")
    validate.add_argument("path", type=Path, nargs="?")
    validate.add_argument("--all", action="store_true")
    commands.add_parser("sync", help="Regenerate workflow indexes")

    change = commands.add_parser("change", help="Create or transition a workflow change")
    change_commands = change.add_subparsers(dest="workflow_change_command", required=True)
    transition_change = change_commands.add_parser("transition")
    transition_change.add_argument("path", type=Path)
    transition_change.add_argument(
        "--to",
        dest="status",
        required=True,
        choices=("proposed", "accepted", "rejected", "deferred", "withdrawn"),
    )
    transition_change.add_argument("--approved-by")
    create_change = change_commands.add_parser("create")
    create_change.add_argument("--request", type=Path, required=True)
    create_change.add_argument("--dry-run", action="store_true")

    version = commands.add_parser("version", help="Transition a workflow version")
    version_commands = version.add_subparsers(dest="workflow_version_command", required=True)
    transition_version = version_commands.add_parser("transition")
    transition_version.add_argument("path", type=Path)
    transition_version.add_argument(
        "--to", dest="status", required=True, choices=("abandoned", "retired")
    )
    transition_version.add_argument("--approved-by")
    version_state = version_commands.add_parser(
        "state", help="Report the A1-2 control state for one exact workflow version"
    )
    version_state.add_argument("path", type=Path)
    version_state.add_argument("--json", dest="json_output", action="store_true")

    study = commands.add_parser("study", help="Operate workflow studies")
    study_commands = study.add_subparsers(dest="workflow_study_command", required=True)
    initialize = study_commands.add_parser("init")
    initialize.add_argument("path", type=Path)
    initialize.add_argument("--slug", required=True)
    initialize.add_argument("--title", required=True)
    initialize.add_argument("--created-by", required=True)
    initialize.add_argument(
        "--route",
        choices=(
            "clean-historical",
            "retrospective-confirmatory",
            "study-time-retrospective",
            "fixed-calendar-retrospective",
        ),
    )
    initialize.add_argument("--revisits")
    preregister = study_commands.add_parser("preregister")
    preregister.add_argument("path", type=Path)
    preregister.add_argument("--approved-by", required=True)
    transition_study = study_commands.add_parser("transition")
    transition_study.add_argument("path", type=Path)
    transition_study.add_argument(
        "--to",
        dest="status",
        required=True,
        choices=("running", "paused", "awaiting-review", "cancelled"),
    )
    transition_study.add_argument("--by", dest="actor", required=True)
    transition_study.add_argument("--approved-by")
    transition_study.add_argument("--reason")
    freeze = study_commands.add_parser("freeze-candidate")
    freeze.add_argument("path", type=Path)
    freeze.add_argument("--selection", type=Path, required=True)
    freeze.add_argument("--approved-by", required=True)
    complete = study_commands.add_parser("complete")
    complete.add_argument("path", type=Path)
    complete.add_argument(
        "--outcome",
        required=True,
        choices=("pass", "fail", "insufficient-evidence", "indeterminate"),
    )
    complete.add_argument("--reviewed-by", required=True)
    complete.add_argument(
        "--disposition",
        choices=(
            "retrospectively-supported",
            "development-selection-failed",
            "retrospective-screen-failed",
        ),
    )
    complete.add_argument(
        "--decision-stage",
        choices=(
            "development",
            "candidate-freeze",
            "retrospective-evaluation",
            "independent-review",
        ),
    )
    release = commands.add_parser("release", help="Prepare a workflow release declaration")
    release.add_argument("path", type=Path)
    release.add_argument("--approved-by", required=True)
    activate = commands.add_parser("activate", help="Activate one prepared workflow release")
    activate.add_argument("path", type=Path)
    activate.add_argument("--approved-by", required=True)
    activation = commands.add_parser(
        "activation", help="Manage legacy workflow activation attestations"
    )
    activation_commands = activation.add_subparsers(
        dest="workflow_activation_command", required=True
    )
    attest = activation_commands.add_parser(
        "attest", help="Attest a grandfathered active workflow release"
    )
    attest.add_argument("path", type=Path)
    attest.add_argument("--approved-by", required=True)
    attest.add_argument("--required-from", required=True)

    safety = commands.add_parser(
        "safety", help="Persist guarded workflow release-safety assessments"
    )
    safety_commands = safety.add_subparsers(dest="workflow_safety_command", required=True)
    assess = safety_commands.add_parser(
        "assess", help="Open one immutable assessment for an active/draft version pair"
    )
    assess.add_argument("path", type=Path, help="Draft successor workflow version")
    assess.add_argument("--request", type=Path, required=True)
    assess.add_argument("--by", dest="actor", required=True)
    clear = safety_commands.add_parser(
        "clear", help="Close one assessment with immutable resolution evidence"
    )
    clear.add_argument("path", type=Path, help="Exact saNNN assessment directory")
    clear.add_argument("--request", type=Path, required=True)
    clear.add_argument("--approved-by", required=True)


def cmd_workflow(args: argparse.Namespace) -> None:
    """Dispatch tracked workflow authoring, validation, and study operations."""
    repository = WorkflowRepository(args.root)
    try:
        if args.workflow_command == "create":
            request = CreateWorkflowRequest.from_path(args.request)
            plan = repository.plan_create(request)
            if args.dry_run:
                print(json.dumps(plan.preview(), ensure_ascii=False, indent=2))
            else:
                result = repository.apply(plan)
                print(f"workflow created: {result.workflow}@{result.version}")
                print(f"  path: {result.target}")
        elif args.workflow_command == "evolve":
            request = EvolveWorkflowRequest.from_path(args.request)
            plan = repository.plan_evolve(request)
            if args.dry_run:
                print(json.dumps(plan.preview(), ensure_ascii=False, indent=2))
            else:
                result = repository.apply(plan)
                print(f"workflow draft evolved: {result.workflow}@{result.version}")
                print(f"  path: {result.target}")
        elif args.workflow_command == "validate":
            if args.all and args.path is not None:
                raise WorkflowAuthoringError("validate accepts a path or --all, not both")
            issues = (
                repository.validate_all()
                if args.all or args.path is None
                else repository.validate_path(args.path)
            )
            if issues:
                for issue in issues:
                    print(f"FAIL {issue}")
                raise SystemExit(f"workflow validation failed: {len(issues)} issue(s)")
            print("workflow validation passed")
        elif args.workflow_command == "sync":
            repository.sync()
            print("workflow indexes synchronized")
        elif args.workflow_command == "change":
            if args.workflow_change_command == "create":
                request = CreateChangeRequest.from_path(args.request)
                plan = repository.plan_change(request)
                if args.dry_run:
                    print(json.dumps(plan.preview(), ensure_ascii=False, indent=2))
                else:
                    result = repository.apply(plan)
                    identity = result.target.name.rsplit("--", 1)[-1].upper()
                    print(f"workflow change created: {identity}")
                    print(f"  path: {result.target}")
            elif args.workflow_change_command == "transition":
                repository.transition_change(
                    args.path,
                    args.status,
                    approved_by=args.approved_by,
                )
                print(f"workflow change transitioned to {args.status}: {args.path}")
        elif args.workflow_command == "version":
            if args.workflow_version_command == "transition":
                repository.transition_version(
                    args.path,
                    args.status,
                    approved_by=args.approved_by,
                )
                print(f"workflow version transitioned to {args.status}: {args.path}")
            elif args.workflow_version_command == "state":
                result = evaluate_workflow_control_state(repository, args.path)
                _print_control_state(result, json_output=args.json_output)
                if result.result in {"invalid", "indeterminate"}:
                    raise SystemExit(2)
        elif args.workflow_command == "study":
            studies = WorkflowStudyService(args.root)
            if args.workflow_study_command == "init":
                path = studies.initialize(
                    args.path,
                    study_slug=args.slug,
                    title=args.title,
                    created_by=args.created_by,
                    revisits=args.revisits,
                    route=args.route,
                )
                print(f"workflow study initialized: {path}")
            elif args.workflow_study_command == "preregister":
                registration = studies.preregister(args.path, approved_by=args.approved_by)
                print(f"workflow study preregistered: {registration['study_id']}")
            elif args.workflow_study_command == "transition":
                studies.transition(
                    args.path,
                    args.status,
                    actor=args.actor,
                    reason=args.reason,
                    approved_by=args.approved_by,
                )
                print(f"workflow study transitioned to {args.status}: {args.path}")
            elif args.workflow_study_command == "freeze-candidate":
                freeze = studies.freeze_candidate(
                    args.path,
                    selection_path=args.selection,
                    approved_by=args.approved_by,
                )
                print(f"workflow candidate frozen: {freeze['study_id']}")
            elif args.workflow_study_command == "complete":
                completion = studies.complete(
                    args.path,
                    outcome=args.outcome,
                    reviewed_by=args.reviewed_by,
                    disposition=args.disposition,
                    decision_stage=args.decision_stage,
                )
                print(
                    f"workflow study completed: {completion['study_id']} ({completion['outcome']})"
                )
        elif args.workflow_command == "release":
            release = repository.release(args.path, approved_by=args.approved_by)
            print(f"workflow release prepared: {release['workflow']}@{release['version']}")
            _registry, _slug, _version, record = repository._registered_version(args.path)
            if record.get("status") == "prepared":
                print("  use `trading workflow activate` to make this release effective")
            else:
                print("  becomes effective only after merge to the canonical branch")
        elif args.workflow_command == "activate":
            activation = repository.activate(args.path, approved_by=args.approved_by)
            print(f"workflow release activated: {activation['workflow']}@{activation['version']}")
        elif args.workflow_command == "activation":
            if args.workflow_activation_command == "attest":
                activation = repository.attest_activation(
                    args.path,
                    approved_by=args.approved_by,
                    activation_required_from=args.required_from,
                )
                print(
                    f"workflow activation attested: "
                    f"{activation['workflow']}@{activation['version']}"
                )
        elif args.workflow_command == "safety":
            if args.workflow_safety_command == "assess":
                request = OpenSafetyAssessmentRequest.from_path(args.request)
                assessment = repository.open_safety_assessment(
                    args.path,
                    request,
                    opened_by=args.actor,
                )
                print(f"workflow safety assessment opened: {assessment['assessment_id']}")
            elif args.workflow_safety_command == "clear":
                request = ClearSafetyAssessmentRequest.from_path(args.request)
                clearance = repository.clear_safety_assessment(
                    args.path,
                    request,
                    approved_by=args.approved_by,
                )
                print(f"workflow safety assessment cleared: {clearance['assessment_id']}")
    except WorkflowAuthoringError as exc:
        raise SystemExit(f"workflow error: {exc}") from exc


def _print_control_state(
    result: WorkflowControlStateResult,
    *,
    json_output: bool,
) -> None:
    if json_output:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    label = result.control_state or result.result
    print(f"workflow control state: {label}")
    print(f"  path: {result.path}")
    if result.workflow is not None and result.version is not None:
        print(f"  identity: {result.workflow}@{result.version}")
    if result.registry_status is not None:
        print(f"  registry status: {result.registry_status}")
    for reason in result.reasons:
        print(f"  reason: {reason}")
    for issue in result.issues:
        print(f"  issue: {issue}")
