import datetime
import json

import pytest

from bitbucket_webhooks_router import event_schemas
from bitbucket_webhooks_router import hooks
from bitbucket_webhooks_router import router


def test_no_handler_available() -> None:
    assert router.route("random:event", {}) is None


def test_num_handlers() -> None:
    assert len(router._HANDLER_MAP) == 10


@hooks.repo_push
def _repo_push_handler_1(event: event_schemas.RepoPush) -> str:
    assert event.repository.name == "webhook-test-project"
    return "repo_pushed_1"


@hooks.repo_push
def _repo_push_handler_2(event: event_schemas.RepoPush) -> str:
    assert event.repository.name == "webhook-test-project"
    return "repo_pushed_2"


def test_repo_push_router() -> None:
    with open("tests/sample_data/repo_push.json") as f:
        data = json.load(f)
    assert router.route("repo:push", data) == ["repo_pushed_1", "repo_pushed_2"]


@hooks.pr_created
def _pr_created_handler(event: event_schemas.PullRequestCreated) -> str:
    assert event.pullrequest.title == "PR title"
    assert event.pullrequest.description == "PR description"
    assert event.pullrequest.source.branch.name == "feature-branch"
    assert event.pullrequest.destination.branch.name == "master"
    return "pr_created"


def test_pr_created_router() -> None:
    with open("tests/sample_data/pull_request_created.json") as f:
        data = json.load(f)
    assert router.route("pullrequest:created", data) == ["pr_created"]


@hooks.pr_approved
def _pr_approved_handler(event: event_schemas.PullRequestApproved) -> str:
    assert event.approval.user.display_name == "Mukund Muralikrishnan"
    assert event.approval.date == datetime.datetime(
        2020,
        3,
        27,
        21,
        5,
        8,
        156574,
        tzinfo=datetime.timezone(datetime.timedelta(0), "+0000"),
    )
    assert event.pullrequest.closed_by is None
    assert event.pullrequest.state == "OPEN"
    return "pr_approved"


def test_pr_approved_router() -> None:
    with open("tests/sample_data/pull_request_approved.json") as f:
        data = json.load(f)
    assert router.route("pullrequest:approved", data) == ["pr_approved"]


@hooks.pr_merged
def _pr_merged_handler(event: event_schemas.PullRequestMerged) -> str:
    assert event.pullrequest.state == "MERGED"
    assert event.pullrequest.merge_commit.hash == "19bdde53bbf1"
    assert event.pullrequest.closed_by.nickname == "mukundvis"
    return "pr_merged"


def test_pr_merged_router() -> None:
    with open("tests/sample_data/pull_request_merged.json") as f:
        data = json.load(f)
    assert router.route("pullrequest:fulfilled", data) == ["pr_merged"]
