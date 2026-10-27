from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from uagents_core.contrib.protocols.chat import MetadataContent, TextContent

from resourcepilot import cards
from resourcepilot.intake import describe_window, upcoming_days

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 21, 10, 0, tzinfo=ZoneInfo("America/Los_Angeles"))
LINE = {
    "item_id": "libcal-1-2-3",
    "name": "HSSE 2101",
    "capacity": 6,
    "slot_start": "2026-10-22T18:00:00+00:00",
    "slot_end": "2026-10-22T19:00:00+00:00",
    "slot_label": "Thu Oct 22 · 2:00 PM\u20133:00 PM",
    "location_label": "HSSE Library",
    "handoff_url": "https://calendar.lib.purdue.edu/space/3",
    "live_times": True,
    "source_label": "LibCal",
    "school_name": "Purdue University",
    "available": True,
    "unavailable_reason": "",
    "policy": "Free. ResourcePilot re-checks this room but cannot reserve it.",
}
PAGE_LINE = {
    **LINE,
    "item_id": "booking-page",
    "name": "Book on Purdue University's LibCal",
    "capacity": 0,
    "slot_label": "",
    "location_label": "Live times unavailable right now",
    "handoff_url": "https://calendar.lib.purdue.edu/reserve",
    "live_times": False,
}
OPTION = {"option_id": "opt_0123456789", "label": "Earliest opening", "lines": [LINE]}
PAGE_OPTION = {"option_id": "opt_abcdef0123", "label": "Booking page", "lines": [PAGE_LINE]}
ROOM_BRIEF = {
    "service": "rooms",
    "school_domain": "purdue.edu",
    "day": "2026-10-22",
    "window": "afternoon",
    "duration_minutes": 60,
    "hours": 1.0,
    "group_size": 2,
    "timezone": "America/Indiana/Indianapolis",
    "window_start": "2026-10-22T16:00:00+00:00",
    "window_end": "2026-10-22T21:00:00+00:00",
}
SCHOOL = {"school_name": "Purdue University", "city": "West Lafayette", "state": "IN"}
HOUSING = {
    "school": SCHOOL,
    "housing": {
        "facts": [("On-campus housing", "Yes"), ("Dorm beds", "16,056")],
        "facts_source": "IPEDS 2022 via Urban Institute Education Data API",
        "office_url": "https://housing.purdue.edu/",
        "portal_url": "https://housing.purdue.edu/apply",
        "portal_label": "Apply for housing",
    },
}
BOOKED = {
    "workflow_id": "workflow-1",
    "status": "booked",
    "option": OPTION,
    "data": {"brief": ROOM_BRIEF, "school": SCHOOL},
}
PAYMENT_WORDS = re.compile(
    r"\b(?:bundles?|pay(?:ment|s)?|paid|escrow|stripe|fet|demo\s+shops?|deposits?|holds?)\b", re.I
)


HALL = {
    "option_id": "hall_0123456789",
    "name": "Earhart",
    "url": "https://housing.purdue.edu/earhart",
    "style": "traditional",
    "who": ["first_year"],
    "rooms": ["double"],
    "features": ["ac"],
    "photo": "",
}
PHOTO_HALL = {
    **HALL,
    "option_id": "hall_abcdef0123",
    "name": "Hillenbrand",
    "photo": "https://housing.purdue.edu/images/hillenbrand.jpg",
}
HALLS = {**HOUSING, "halls": [HALL, PHOTO_HALL], "all_halls": [HALL, PHOTO_HALL]}
PREVIEW = {
    "to": "\u2022\u2022\u2022\u2022 0142",
    "opening": "Hello, this is a ResourcePilot demo drill, not a real emergency.",
    "rows": [("Calling", "Your demo contact (\u2022\u2022\u2022\u2022 0142), not 911")],
}
CALL = {"to": "\u2022\u2022\u2022\u2022 0142", "conversation_id": "conv_1"}
CALL_STATUS = {
    "status_label": "Call ended",
    "duration": "1:15",
    "summary": "Reported a fainting.",
    "transcript": [{"speaker": "Dispatcher", "message": "What is your location?"}],
}
EVENT_PHOTO = "https://localist-images.azureedge.net/photos/1/huge/x.jpg"
WELLNESS = {
    "school": {"school_name": "Test U"},
    "options": [OPTION],
    "wellness": {
        "status": "found",
        "events": [
            {
                "title": "Flu clinic",
                "when": "Mon",
                "url": "https://events.x.edu/1",
                "photo": EVENT_PHOTO,
            },
            {"title": "Yoga", "when": "Tue", "url": "https://events.x.edu/2", "photo": ""},
        ],
    },
}


def _metadata(message):
    return next(item.metadata for item in message.content if isinstance(item, MetadataContent))


FACTORIES = [
    (cards.welcome_card, "carousel"),
    (cards.school_card, "custom"),
    (lambda: cards.service_overview_card("rooms"), "detail"),
    (lambda: cards.service_overview_card("wellness"), "detail"),
    (lambda: cards.service_overview_card("housing"), "detail"),
    (lambda: cards.service_overview_card("emergency"), "detail"),
    (lambda: cards.rooms_form(upcoming_days(NOW)), "form"),
    (lambda: cards.wellness_form(upcoming_days(NOW)), "form"),
    (cards.housing_form, "form"),
    (cards.emergency_form, "form"),
    (lambda: cards.service_form("rooms"), "form"),
    (lambda: cards.service_form("housing"), "form"),
    (lambda: cards.room_link_card("workflow-1", "MIT"), "custom"),
    (lambda: cards.progress_card("workflow-1", "researcher", ("intake", "researcher")), "custom"),
    (lambda: cards.progress_card("workflow-1", "recheck"), "custom"),
    (lambda: cards.progress_card("workflow-1", "call"), "custom"),
    (lambda: cards.progress_card("workflow-1", "somewhere-new"), "custom"),
    (lambda: cards.rooms_carousel("workflow-1", [OPTION, PAGE_OPTION], "Purdue"), "carousel"),
    (lambda: cards.room_detail("workflow-1", OPTION), "detail"),
    (lambda: cards.room_detail("workflow-1", PAGE_OPTION), "detail"),
    (lambda: cards.room_link_receipt(OPTION), "detail"),
    (lambda: cards.room_link_receipt(PAGE_OPTION), "detail"),
    (lambda: cards.housing_card(HOUSING), "detail"),
    (lambda: cards.housing_card({}), "detail"),
    (lambda: cards.bookings_card([]), "detail"),
    (lambda: cards.bookings_card([BOOKED]), "carousel"),
    (lambda: cards.error_card("Something failed", service="rooms"), "custom"),
    (lambda: cards.error_card("Something failed"), "custom"),
    (lambda: cards.notice_card("Saved", "Your link was checked.", badge="Done"), "custom"),
    (
        lambda: cards.status_card(
            "Planner", "Ranks open rooms", "agent1qorch", image=cards.agent_art("planner")
        ),
        "custom",
    ),
    (lambda: cards.room_detail("workflow-1", OPTION, wellness=True), "detail"),
    (lambda: cards.housing_carousel("workflow-1", HALLS), "carousel"),
    (lambda: cards.housing_detail("workflow-1", HALL, HALLS), "detail"),
    (lambda: cards.housing_detail("workflow-1", PHOTO_HALL, HALLS), "detail"),
    (lambda: cards.no_housing_match_card("workflow-1", HALLS), "custom"),
    (lambda: cards.housing_unlock_card("workflow-1", HALLS, ["$1.00"]), "custom"),
    (lambda: cards.housing_payment_card("workflow-1", ["$1.00"]), "custom"),
    (lambda: cards.wellness_card("workflow-1", {"school": {"school_name": "Test U"}}), "custom"),
    (lambda: cards.wellness_card("workflow-1", WELLNESS), "custom"),
    (lambda: cards.wellness_events_card("workflow-1", WELLNESS), "custom"),
    (
        lambda: cards.wellness_event_detail("workflow-1", WELLNESS["wellness"]["events"][0]),
        "detail",
    ),
    (lambda: cards.emergency_review_card("workflow-1", PREVIEW), "review"),
    (lambda: cards.emergency_call_card("workflow-1", CALL), "custom"),
    (lambda: cards.emergency_call_card("workflow-1", CALL, CALL_STATUS), "custom"),
]


def test_ui_exercises_every_official_card_kind() -> None:
    assert {kind for _, kind in FACTORIES} == cards.CARD_KINDS


@pytest.mark.parametrize(
    "factory",
    [
        lambda: cards.housing_unlock_card("workflow-1", HALLS, ["$1.00"]),
        lambda: cards.housing_payment_card("workflow-1", ["$1.00"]),
    ],
)
def test_every_payment_card_says_what_the_money_buys(factory) -> None:
    text = json.dumps(factory()[1])
    assert cards.MATCH_NOT_HOUSING in text and cards.TEST_MONEY in text


@pytest.mark.parametrize(("factory", "kind"), FACTORIES)
def test_every_card_uses_the_current_wire_format(factory, kind) -> None:
    actual_kind, payload = factory()
    assert actual_kind == kind
    message = cards.card_message("Readable fallback", actual_kind, payload)
    metadata = _metadata(message)
    assert metadata["card_protocol_version"] == "1"
    assert metadata["requires_card_interaction"] == "true"
    assert metadata["card_kind"] == kind
    assert all(isinstance(value, str) for value in metadata.values())
    assert len(metadata["card_payload"].encode()) <= cards.CARD_LIMIT_BYTES
    assert json.loads(metadata["card_payload"]) == payload
    assert "is_terminal" not in metadata
    assert any(isinstance(item, TextContent) for item in message.content)
    if kind == "custom":
        assert cards._custom_tree_depth(payload["root"]) <= cards.CUSTOM_CARD_MAX_DEPTH


def _labels(value):
    """Yield button, badge, field, and option labels; summary rows may wrap, so skip them."""
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "summary_rows":
                continue
            if key == "label" and isinstance(item, str):
                yield item
            yield from _labels(item)
    elif isinstance(value, list):
        for item in value:
            yield from _labels(item)


def _selections(value):
    """Yield every selection a card can send back, from CTAs, buttons, and carousel items."""
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "selection" and isinstance(item, dict):
                yield item
            else:
                yield from _selections(item)
    elif isinstance(value, list):
        for item in value:
            yield from _selections(item)


@pytest.mark.parametrize(("factory", "kind"), FACTORIES)
def test_labels_are_mobile_safe(factory, kind) -> None:
    _, payload = factory()
    assert all(len(label) <= 24 for label in _labels(payload))


@pytest.mark.parametrize(("factory", "kind"), FACTORIES)
def test_every_selection_uses_a_known_action(factory, kind) -> None:
    _, payload = factory()
    actions = [selection["action"] for selection in _selections(payload)]
    if payload.get("root", {}).get("title") == "Planner":
        assert not actions  # profile status uses a safe markdown link, not an undocumented redirect
        return
    assert actions
    assert set(actions) <= set(cards.KNOWN_ACTIONS)


def test_terminal_flag_is_a_string() -> None:
    informational = ("custom", {"root": {"type": "text", "value": "All done"}})
    message = cards.card_message("Done", *informational, terminal=True)
    assert _metadata(message)["is_terminal"] == "true"


def test_visible_links_are_repeated_as_clickable_markdown() -> None:
    kind, receipt = cards.room_link_receipt(OPTION)
    message = cards.card_message("Your verified link.", kind, receipt)
    text = next(item.text for item in message.content if isinstance(item, TextContent))
    assert f"]({LINE['handoff_url']})" in text
    assert cards.card_links(receipt)

    unsafe = {
        "title": "Sources",
        "summary_rows": [
            {"label": "Apply", "value": "https://housing.example.edu/apply"},
            {"label": "Sources", "value": "Failed: https://evil.example.com"},
        ],
        "ctas": [],
    }
    links = cards.card_links(unsafe)
    assert ("Apply", "https://housing.example.edu/apply") in links
    assert not any(url == "https://evil.example.com" for _, url in links)


def test_link_labels_cannot_inject_markdown() -> None:
    payload = {
        "title": "x",
        "summary_rows": [
            {"label": "Hall", "value": "[Evil](https://bad.example) **x**: https://ok.edu/a"},
            {"label": "Sources", "value": "Dropped links: https://dead.edu"},
        ],
    }
    text = cards.with_links("", payload)
    assert "https://dead.edu" not in text
    assert "](https://ok.edu/a)" in text
    assert "\\[Evil\\]" in text and "\\*\\*" in text


@pytest.mark.parametrize(
    "factory",
    [
        cards.rooms_form,
        cards.wellness_form,
        cards.housing_form,
        cards.emergency_form,
        lambda: cards.room_link_card("workflow-1", "MIT"),
        lambda: cards.emergency_review_card("workflow-1", PREVIEW),
        lambda: cards.room_link_receipt(OPTION),
        lambda: ("form", {"title": "x", "fields": [], "submit_cta": {"label": "Go"}}),
    ],
)
def test_a_card_that_expects_input_is_never_terminal(factory) -> None:
    kind, payload = factory()
    with pytest.raises(ValueError, match="never be terminal"):
        cards.card_message("x", kind, payload, terminal=True)


@pytest.mark.parametrize(
    ("kind", "payload", "message"),
    [
        ("carousel", {"title": "x", "items": [], "style": "dense"}, "carousel card"),
        ("carousel", {"items": [{"id": "1", "title": "x", "price": "$1"}]}, "items"),
        ("carousel", {"items": [{"id": 1, "title": "x"}]}, "string id"),
        ("detail", {"title": "x", "ctas": [{"label": "Go", "selection": {}, "icon": "x"}]}, "ctas"),
        ("review", {"title": "x", "approve_cta": {"label": "Go", "style": "red"}}, "CTA"),
        ("detail", {"title": "x", "summary_rows": [{"label": "Seats", "value": 4}]}, "strings"),
        ("form", {"title": "x", "fields": [{"name": "a", "kind": "text", "hint": "x"}]}, "fields"),
        (
            "custom",
            {"root": {"type": "button", "label": "Go", "action": {}, "color": "red"}},
            "button",
        ),
        ("custom", {"root": {"type": "table", "rows": []}}, "unsupported custom element"),
    ],
)
def test_undocumented_fields_are_rejected_before_sending(kind, payload, message) -> None:
    with pytest.raises(ValueError, match=message):
        cards.card_message("x", kind, payload)


@pytest.mark.parametrize(
    ("kind", "payload", "message"),
    [
        (
            "form",
            {"title": "x", "fields": [{"name": "a", "kind": "select", "label": "A"}]},
            "non-empty options",
        ),
        (
            "custom",
            {
                "root": {
                    "type": "input",
                    "name": "a",
                    "kind": "select",
                    "label": "A",
                    "options": [],
                }
            },
            "non-empty options",
        ),
        (
            "custom",
            {"root": {"type": "choice_grid", "name": "a", "choices": [], "multi": False}},
            "non-empty choices",
        ),
    ],
)
def test_selectors_require_choices(kind, payload, message) -> None:
    with pytest.raises(ValueError, match=message):
        cards.card_message("x", kind, payload)


def test_card_rejects_oversize_payload() -> None:
    with pytest.raises(ValueError, match="64KB"):
        cards.card_message("too big", "custom", {"root": {"type": "text", "value": "x" * 70_000}})


def _nested(depth: int) -> dict:
    node = {"type": "text", "value": "leaf"}
    for _ in range(depth - 1):
        node = {"type": "group", "children": [node]}
    return {"root": node}


def test_custom_card_depth_limit() -> None:
    cards.card_message("ok", "custom", _nested(8))
    with pytest.raises(ValueError, match="8-level"):
        cards.card_message("too deep", "custom", _nested(9))
    with pytest.raises(ValueError, match="typed root"):
        cards.card_message("bad", "custom", {"root": {"children": []}})
    with pytest.raises(ValueError, match="unsupported"):
        cards.card_message("bad", "table", {})
    bad_action = {
        "root": {
            "type": "button",
            "label": "Go",
            "action": {
                "selection": {"action": "start_over"},
                "redirect": "https://asi1.ai/",
            },
        }
    }
    with pytest.raises(ValueError, match="only a selection"):
        cards.card_message("bad", "custom", bad_action)


def test_services_menu_offers_four_services_and_bookings() -> None:
    kind, menu = cards.welcome_card("purdue.edu")
    assert kind == "carousel"
    assert [item["id"] for item in menu["items"]] == [
        "service-rooms",
        "service-wellness",
        "service-housing",
        "service-emergency",
        "service-bookings",
        "change-school",
    ]
    assert list(_selections(menu)) == [
        {"action": "open_service", "service": "rooms"},
        {"action": "open_service", "service": "wellness"},
        {"action": "open_service", "service": "housing"},
        {"action": "open_service", "service": "emergency"},
        {"action": "show_bookings"},
        {"action": "change_school"},
    ]
    text = json.dumps(menu).lower()
    assert "study rooms" in text
    assert "campus housing" in text
    assert "my bookings" in text
    assert not PAYMENT_WORDS.findall(text)
    assert cards.CRISIS_TEXT in json.dumps(menu, ensure_ascii=False)


@pytest.mark.parametrize("service", ["rooms", "wellness", "housing", "emergency"])
def test_service_overview_bridges_menu_to_native_form(service) -> None:
    kind, overview = cards.service_overview_card(service, "purdue.edu")
    assert kind == "detail"
    assert overview["hero_image"] == cards.art(f"svc-{service}")
    assert overview["summary_rows"][0] == {"label": "School", "value": "purdue.edu"}
    assert [cta["selection"] for cta in overview["ctas"]] == [
        {"action": "open_form", "service": service},
        {"action": "start_over"},
    ]
    if service == "wellness":
        assert cards.CRISIS_TEXT in json.dumps(overview, ensure_ascii=False)
    if service == "emergency":
        assert cards.DEMO_NOTICE in json.dumps(overview, ensure_ascii=False)


@pytest.mark.parametrize("service", ["rooms", "wellness", "housing", "emergency"])
def test_every_form_submits_its_own_service(service) -> None:
    kind, form = cards.service_form(service)
    assert kind == "form"
    fields = cards.card_inputs(form)
    assert fields and all("kind" in field and "type" not in field for field in fields)
    for field in fields:
        if field["kind"] == "select":
            assert field["options"]
    assert cards.card_buttons(form) == [
        (form_label(service), {"action": "submit_form", "service": service})
    ]
    # The school was set once on the menu; service forms never ask for it again.
    assert not [field for field in fields if field["name"] == "email"]
    assert not [field for field in fields if "phone" in field["name"]]


def test_school_card_keeps_the_email_out_of_service_forms() -> None:
    kind, school = cards.school_card()
    assert kind == "custom"
    assert [field["name"] for field in cards.card_inputs(school)] == ["email"]
    assert cards.card_buttons(school) == [("Save my school", {"action": "set_school"})]
    _, change = cards.school_card("purdue.edu")
    assert cards.card_buttons(change)[-1] == cards.MAIN_MENU


def form_label(service: str) -> str:
    return {
        "rooms": "Find open rooms",
        "wellness": "Find rooms and events",
        "housing": "Find housing",
        "emergency": "Review the demo call",
    }[service]


def test_rooms_form_offers_days_windows_durations_and_group_size() -> None:
    _, form = cards.rooms_form(upcoming_days(NOW))
    fields = {field["name"]: field for field in cards.card_inputs(form)}
    assert list(fields) == ["day", "window", "duration", "group_size"]
    assert fields["day"]["options"][0] == {"value": "2026-10-21", "label": "Today"}
    assert [option["value"] for option in fields["window"]["options"]] == [
        "morning",
        "afternoon",
        "evening",
        "any",
    ]
    assert [option["value"] for option in fields["duration"]["options"]] == [
        "30",
        "60",
        "90",
        "120",
    ]
    assert len(fields["group_size"]["options"]) == 12


def test_room_link_card_checks_a_pasted_link_without_skipping() -> None:
    _, link = cards.room_link_card("workflow-1", "MIT")
    root = link["root"]
    assert root["title"] == "Where does MIT book study rooms?"
    inputs = [child for child in root["children"] if child["type"] == "input"]
    assert [field["name"] for field in inputs] == ["booking_link"]
    assert list(_selections(link)) == [
        {"action": "submit_link", "workflow_id": "workflow-1"},
        {"action": "start_over"},
    ]
    assert "skip" not in json.dumps(link).lower()


def test_rooms_carousel_items_carry_stable_option_ids() -> None:
    _, carousel = cards.rooms_carousel("workflow-1", [OPTION, PAGE_OPTION], "Purdue")
    assert carousel["title"] == "Open study rooms at Purdue"
    first, second = carousel["items"]
    assert first["id"] == "opt_0123456789"
    assert first["primary_cta"]["selection"] == {
        "action": "view_room",
        "workflow_id": "workflow-1",
        "option_id": "opt_0123456789",
    }
    assert [badge["label"] for badge in first["badges"]] == ["Earliest", "Live · LibCal"]
    assert "seats 6" in first["secondary_text"]
    assert second["id"] == "opt_abcdef0123"
    assert second["primary_cta"]["selection"]["option_id"] == "opt_abcdef0123"
    assert [badge["label"] for badge in second["badges"]] == ["Link only"]
    assert "seats not listed" in second["secondary_text"]


def test_room_detail_rechecks_by_option_and_shows_the_link() -> None:
    _, detail = cards.room_detail("workflow-1", OPTION)
    assert detail["title"] == "HSSE 2101"
    assert [cta["selection"] for cta in detail["ctas"]] == [
        {"action": "recheck_room", "workflow_id": "workflow-1", "option_id": "opt_0123456789"},
        {"action": "show_results", "workflow_id": "workflow-1"},
    ]
    assert detail["ctas"][0]["primary"] is True
    rows = {row["label"]: row["value"] for row in detail["summary_rows"]}
    assert rows["Book here"] == LINE["handoff_url"]
    assert rows["When"] == LINE["slot_label"]
    assert rows["Seats"] == "6"
    assert rows["Price"] == "Free"
    assert rows["Times"] == "Live from LibCal"
    _, page = cards.room_detail("workflow-1", PAGE_OPTION)
    page_rows = {row["label"]: row["value"] for row in page["summary_rows"]}
    assert "When" not in page_rows
    assert "Seats" not in page_rows
    assert page_rows["Times"].startswith("Not shown live")


def test_room_link_receipt_is_a_link_not_a_reservation() -> None:
    _, receipt = cards.room_link_receipt(OPTION)
    assert receipt["title"] == "Your booking link"
    rows = {row["label"]: row["value"] for row in receipt["summary_rows"]}
    assert rows["Room"] == "HSSE 2101"
    assert rows["When"] == LINE["slot_label"]
    assert rows["Book here"] == LINE["handoff_url"]
    assert rows["Next step"] == "Not reserved by ResourcePilot: book it with your own sign-in"
    assert rows["Re-checked"].startswith("Open when ResourcePilot re-checked it live")
    assert [cta["selection"] for cta in receipt["ctas"]] == [
        {"action": "open_form", "service": "rooms"},
        {"action": "show_bookings"},
        {"action": "start_over"},
    ]
    assert [cta["label"] for cta in receipt["ctas"]] == [
        "Find another room",
        "My bookings",
        "Menu",
    ]
    assert "sub_options" not in receipt  # terminal-safe: no input beyond its CTA buttons
    assert not PAYMENT_WORDS.findall(json.dumps(receipt))
    _, page = cards.room_link_receipt(PAGE_OPTION)
    page_rows = {row["label"]: row["value"] for row in page["summary_rows"]}
    assert page_rows["Re-checked"].startswith("Not checked live")


def test_housing_card_shows_sources_and_official_links() -> None:
    _, card = cards.housing_card(HOUSING)
    text = json.dumps(card)
    assert card["title"] == "Housing at Purdue University · West Lafayette, IN"
    assert "https://housing.purdue.edu/apply" in text
    assert "IPEDS 2022" in text
    assert "never applies or pays" in text
    assert [cta["selection"] for cta in card["ctas"]] == [
        {"action": "open_service", "service": "rooms"},
        {"action": "start_over"},
    ]
    _, empty = cards.housing_card({})
    assert empty["title"] == "Housing at your school"
    assert {"label": "Housing office", "value": "Not found on the school's site"} in (
        empty["summary_rows"]
    )


def test_bookings_card_lists_booked_rooms_with_their_links() -> None:
    empty_kind, empty = cards.bookings_card([])
    assert empty_kind == "detail"
    assert empty["summary_rows"] == [{"label": "Bookings", "value": "No bookings yet"}]
    kind, card = cards.bookings_card([BOOKED, {"status": "booked", "data": {}}])
    assert kind == "carousel"
    assert len(card["items"]) == 1
    item = card["items"][0]
    assert item["title"] == "HSSE 2101"
    assert "Purdue University" in item["subtitle"]
    assert LINE["slot_label"] in item["subtitle"]
    assert item["primary_cta"]["selection"] == {
        "action": "show_booking",
        "workflow_id": "workflow-1",
    }
    _, page = cards.bookings_card([{**BOOKED, "option": PAGE_OPTION}])
    assert describe_window(ROOM_BRIEF) in page["items"][0]["subtitle"]


def test_progress_card_marks_finished_and_current_stages() -> None:
    chain = ("intake", "researcher", "campus_rooms", "verification", "planner")
    assert set(chain) <= set(cards.STAGE_LABELS)
    assert {"recheck", "link", "payment"} <= set(cards.STAGE_LABELS)
    assert cards.STAGE_ART["payment"] == "svc-housing"
    assert all(len(label) <= 24 for label in cards.STAGE_LABELS.values())
    _, card = cards.progress_card("workflow-123456789", "verification", chain)
    assert card["root"]["children"][0]["src"] == cards.art("role-verification")
    children = card["root"]["children"][1:]
    assert children[0] == {"type": "badge", "label": "Step 4 of 5", "variant": "info"}
    steps = children[1]["items"]
    assert [(item["children"][0]["label"], item["children"][1]["value"]) for item in steps] == [
        ("Done", "Reading your form"),
        ("Done", "Researching your school"),
        ("Done", "Reading open rooms"),
        ("Now", "Verifying every result"),
        ("Next", "Ranking open rooms"),
    ]
    assert children[2]["value"] == "Workflow workflow"
    assert list(_selections(card)) == [
        {"action": "show_status", "workflow_id": "workflow-123456789"}
    ]
    _, recheck = cards.progress_card("workflow-1", "recheck")
    assert recheck["root"]["children"][0]["src"] == cards.art("role-campus-rooms")
    assert recheck["root"]["children"][1]["label"] == "Live update"
    assert recheck["root"]["children"][2]["items"][0]["children"][1]["value"] == (
        "Re-checking your room"
    )
    assert len(recheck["root"]["children"]) == 5


def test_known_actions_cover_the_room_and_demo_call_flows_only() -> None:
    assert set(cards.KNOWN_ACTIONS) == {
        "set_school",
        "change_school",
        "start_over",
        "open_service",
        "open_form",
        "submit_form",
        "show_bookings",
        "show_booking",
        "show_status",
        "view_room",
        "recheck_room",
        "show_results",
        "show_wellness_view",
        "view_wellness_event",
        "submit_link",
        "view_housing",
        "show_housing_facts",
        "show_all_housing",
        "unlock_housing",
        "place_call",
        "call_status",
        "open_orchestrator",
    }
    assert set(cards.PROSE_ACTIONS) <= set(cards.KNOWN_ACTIONS)
    consequential = {
        "set_school",
        "submit_form",
        "recheck_room",
        "submit_link",
        "place_call",
        "unlock_housing",
    }
    assert consequential <= cards.INPUT_ACTIONS
    assert not consequential & set(cards.PROSE_ACTIONS)


def test_direct_json_selection_is_parsed_before_prose() -> None:
    parsed = cards.parse_selection(
        '@resourcepilot {"selection":{"action":"recheck_room",'
        '"option_id":"opt_0123456789","workflow_id":"w"}}'
    )
    assert parsed["action"] == "recheck_room"
    assert parsed["option_id"] == "opt_0123456789"
    assert parsed["workflow_id"] == "w"
    flat = cards.parse_selection(
        '{"action":"submit_link","workflow_id":"w","booking_link":"https://x.edu"}'
    )
    assert flat == {"action": "submit_link", "workflow_id": "w", "booking_link": "https://x.edu"}
    view = cards.parse_selection('{"action":"view_room","workflow_id":"w","option_id":"opt_1"}')
    assert view["option_id"] == "opt_1"


def test_prose_fallback_only_allows_non_consequential_actions() -> None:
    assert cards.parse_selection("Can you show status?")["action"] == "show_status"
    assert cards.parse_selection("show results again") == {"action": "show_results"}
    assert cards.parse_selection("please show bookings") == {"action": "show_bookings"}
    assert cards.parse_selection("start over") == {"action": "start_over"}
    assert cards.parse_selection("I need a study room") == {
        "action": "open_service",
        "service": "rooms",
    }
    assert cards.parse_selection("what about dorms")["service"] == "housing"
    assert cards.parse_selection("recheck room and submit link") == {}
    assert cards.parse_selection("submit form https://purdue.edu") == {}
    assert cards.parse_selection("view room opt_1") == {}
    assert cards.parse_selection("project bundle with a DSLR") == {}
    assert cards.parse_selection("") == {}


def test_cards_module_has_no_bundle_or_payment_surface() -> None:
    removed = (
        "bundle_form",
        "bundle_carousel",
        "bundle_detail",
        "bundle_rows",
        "holds_review_card",
        "payment_options_card",
        "receipt_card",
        "recovery_card",
        "refund_card",
        "vetting_card",
        "example_bundle_selection",
        "demo_control_buttons",
    )
    assert not [name for name in removed if hasattr(cards, name)]
    assert set(cards.SERVICE_TITLES) == {"rooms", "wellness", "housing", "emergency"}
    source = (ROOT / "resourcepilot" / "cards.py").read_text()
    for module in ("pricing", "registry", "bundles", "logistics", "escrow", "payment"):
        assert f"resourcepilot.{module}" not in source
        assert f"from resourcepilot import {module}" not in source


def test_every_orchestrator_reply_is_a_card() -> None:
    assert not hasattr(cards, "text_message")
    source = (ROOT / "agents" / "run.py").read_text()
    assert "TextContent(" not in source
    assert "ChatMessage(" not in source


def test_wellness_card_always_carries_the_crisis_line() -> None:
    kind, payload = cards.wellness_card("wf-1", {"school": {"school_name": "Test U"}})
    message = cards.card_message("x", kind, payload)
    encoded = json.dumps(payload, ensure_ascii=False)
    assert message.content[1].metadata["card_kind"] == "custom"
    assert cards.CRISIS_TEXT in encoded
    assert "No public room-booking system found for Test U" in encoded
    assert "No public events calendar found for Test U" in encoded
    form_kind, form = cards.wellness_form()
    assert form_kind == "form"
    assert "988" in form["title"]
    names = {field["name"] for field in cards.card_inputs(form)}
    assert names == {"day", "window", "duration"}


def test_wellness_hub_choice_grid_routes_to_rooms_and_events() -> None:
    kind, payload = cards.wellness_card("wf-1", WELLNESS)
    cards.card_message("x", kind, payload)
    grids = [field for field in cards.card_inputs(payload) if field["type"] == "choice_grid"]
    assert len(grids) == 1
    assert grids[0]["name"] == "wellness_view"
    assert [choice["value"] for choice in grids[0]["choices"]] == ["rooms", "events"]
    assert cards.card_buttons(payload)[0] == (
        "Open selection",
        {"action": "show_wellness_view", "workflow_id": "wf-1"},
    )
    _, carousel = cards.rooms_carousel("wf-1", [OPTION], "Test U", wellness=True)
    assert carousel["items"][0]["primary_cta"]["selection"] == {
        "action": "view_room",
        "workflow_id": "wf-1",
        "option_id": OPTION["option_id"],
    }
    _, detail = cards.room_detail("wf-1", OPTION, wellness=True)
    assert {"label": "Need help now?", "value": cards.CRISIS_TEXT} in detail["summary_rows"]
    _, receipt = cards.room_link_receipt(OPTION, service="wellness")
    assert receipt["ctas"][0]["selection"] == {"action": "open_form", "service": "wellness"}


def test_wellness_event_list_is_capped_and_actions_are_not_duplicated() -> None:
    events = [
        {"title": f"Event {index}", "when": "Tue", "url": f"https://events.x.edu/{index}"}
        for index in range(cards.CARD_EVENTS + 2)
    ]
    _, payload = cards.wellness_events_card(
        "wf-1",
        {
            "school": {"school_name": "Test U"},
            "wellness": {"status": "found", "events": events},
        },
    )
    event_actions = [
        selection for label, selection in cards.card_buttons(payload) if label == "List item"
    ]
    assert len(event_actions) == cards.CARD_EVENTS
    assert [selection["event_index"] for selection in event_actions] == ["0", "1", "2", "3", "4"]
    assert f"Showing {cards.CARD_EVENTS} of {len(events)} verified events." in json.dumps(payload)


def test_wellness_events_are_tappable_and_open_a_native_detail() -> None:
    _, event_list = cards.wellness_events_card("wf-1", WELLNESS)
    actions = [
        selection for selection in _selections(event_list) if selection["action"].startswith("view")
    ]
    assert actions == [
        {"action": "view_wellness_event", "workflow_id": "wf-1", "event_index": "0"},
        {"action": "view_wellness_event", "workflow_id": "wf-1", "event_index": "1"},
    ]
    kind, detail = cards.wellness_event_detail("wf-1", WELLNESS["wellness"]["events"][0])
    assert kind == "detail"
    assert detail["hero_image"] == EVENT_PHOTO
    assert {"label": "Official RSVP", "value": "https://events.x.edu/1"} in (detail["summary_rows"])


def test_wellness_prose_only_opens_the_safe_overview() -> None:
    for text in ("any wellness events?", "I need a meditation space", "flu shot near me"):
        assert cards.parse_selection(text) == {"action": "open_service", "service": "wellness"}


def test_emergency_cards_say_not_911_and_only_a_button_places_the_call() -> None:
    form_kind, form = cards.emergency_form()
    assert form_kind == "form"
    assert "not 911" in form["title"]
    fields = {field["name"]: field for field in form["fields"]}
    assert fields["demo_only"] == {
        "name": "demo_only",
        "kind": "checkbox",
        "label": "I understand: demo only",
        "required": True,
    }
    kind, review = cards.emergency_review_card("wf-9", PREVIEW)
    cards.card_message("x", kind, review)
    assert kind == "review"
    assert cards.card_buttons(review) == [
        ("Call now", {"action": "place_call", "workflow_id": "wf-9"}),
        ("Cancel", {"action": "start_over"}),
    ]
    assert "never 911" in json.dumps(review, ensure_ascii=False)
    for payload in (
        cards.emergency_call_card("wf-9", CALL),
        cards.emergency_call_card("wf-9", CALL, CALL_STATUS),
    ):
        kind, card = payload
        cards.card_message("x", kind, card)
        encoded = json.dumps(card, ensure_ascii=False)
        assert cards.DEMO_NOTICE in encoded and "0142" in encoded
    assert "What is your location?" in encoded
    for text in ("call now", "place the call", "emergency call 911 now"):
        assert cards.parse_selection(text).get("action") != "place_call"


def _image_urls(node) -> list[str]:
    urls = []
    if isinstance(node, dict):
        for key in ("src", "image", "hero_image"):
            if isinstance(node.get(key), str):
                urls.append(node[key])
        for value in node.values():
            urls.extend(_image_urls(value))
    elif isinstance(node, list):
        for value in node:
            urls.extend(_image_urls(value))
    return urls


# Pictures a card may show that are not ResourcePilot's own art: a school's own hall or event photo.
OWN_PHOTOS = {PHOTO_HALL["photo"], EVENT_PHOTO}


def test_art_names_match_the_contract() -> None:
    from resourcepilot.config import ALL_AGENTS

    roles = {cards.agent_art(identity.key) for identity in ALL_AGENTS}
    assert roles == {name for name in cards.ART if name.startswith("role-")}
    assert len(roles) == 8
    assert set(cards.STAGE_ART.values()) <= cards.ART
    assert set(cards.STAGE_ART) <= set(cards.STAGE_LABELS)
    with pytest.raises(KeyError):
        cards.art("cat-camera")
    with pytest.raises(KeyError):
        cards.agent_art("fulfillment")


def test_every_art_name_has_a_committed_image_and_every_agent_an_avatar() -> None:
    # The images are generated from assets/src by the art script and committed with the code.
    from resourcepilot.config import ALL_AGENTS

    for name in cards.ART:
        assert (ROOT / "assets" / "cards" / f"{name}.jpg").is_file(), name
    for identity in ALL_AGENTS:
        assert (ROOT / "assets" / "avatars" / f"{identity.key}.jpg").is_file(), identity.key


@pytest.mark.parametrize("key", ["orchestrator", "intake", "campus_rooms", "memory_audit"])
def test_agent_art_names_each_role(key) -> None:
    assert cards.agent_art(key) == f"role-{key.replace('_', '-')}"


@pytest.mark.parametrize(("factory", "kind"), FACTORIES)
def test_every_card_has_a_picture_from_the_repository(factory, kind, monkeypatch) -> None:
    monkeypatch.delenv("CARD_IMAGE_BASE", raising=False)
    _, payload = factory()
    urls = _image_urls(payload)
    if kind in {"form", "review"}:
        assert not urls  # Native ASI:One forms/reviews follow an illustrated detail screen.
        return
    assert urls, "every card carries at least one image"
    for url in set(urls) - OWN_PHOTOS:
        assert url.startswith(cards.DEFAULT_IMAGE_BASE + "cards/"), url
        assert url.rsplit("/", 1)[1].removesuffix(".jpg") in cards.ART, url


@pytest.mark.parametrize("base", ["", "http://example.com/assets/", "   "])
@pytest.mark.parametrize(("factory", "kind"), FACTORIES)
def test_cards_stay_valid_with_images_turned_off(factory, kind, base, monkeypatch) -> None:
    monkeypatch.setenv("CARD_IMAGE_BASE", base)
    actual_kind, payload = factory()
    assert actual_kind == kind
    cards.card_message("x", actual_kind, payload)
    # Only a hall's own photo can remain; it is the school's, not ResourcePilot's art.
    assert set(_image_urls(payload)) <= {PHOTO_HALL["photo"]}


def test_image_base_can_move_to_another_https_host(monkeypatch) -> None:
    monkeypatch.setenv("CARD_IMAGE_BASE", "https://cdn.example.org/rp")
    assert cards.art("hero-info") == "https://cdn.example.org/rp/cards/hero-info.jpg"


def test_menu_is_a_native_picture_carousel_with_bookings_and_crisis_help() -> None:
    kind, menu = cards.welcome_card()
    assert kind == "carousel"
    assert [item["image"] for item in menu["items"]] == [
        cards.art(f"svc-{name}")
        for name in ("rooms", "wellness", "housing", "emergency", "bookings")
    ]
    assert [selection for _, selection in cards.card_buttons(menu)][-1] == {
        "action": "show_bookings"
    }
    assert cards.CRISIS_TEXT in menu["subtitle"]


def test_event_photos_come_from_the_feed_and_fall_back_to_art() -> None:
    _, hub = cards.wellness_card("workflow-1", WELLNESS)
    assert cards.art("wellness-hero") in _image_urls(hub)
    assert cards.art("room-wellness") in _image_urls(hub)
    _, event_list = cards.wellness_events_card("workflow-1", WELLNESS)
    urls = _image_urls(event_list)
    assert EVENT_PHOTO in urls
    assert cards.art("event-default") in urls
    encoded = json.dumps(hub, ensure_ascii=False)
    assert encoded.index(cards.CRISIS_TEXT) < encoded.index("wellness-hero")
    unsafe = {**WELLNESS["wellness"]["events"][0], "photo": "http://x.edu/a.jpg"}
    _, event_list = cards.wellness_events_card(
        "workflow-1", {**WELLNESS, "wellness": {"status": "found", "events": [unsafe]}}
    )
    assert "http://x.edu/a.jpg" not in _image_urls(event_list)


def test_halls_show_their_own_photo_else_the_default_hall() -> None:
    _, carousel = cards.housing_carousel("workflow-1", HALLS)
    images = {item["id"]: item.get("image") for item in carousel["items"]}
    assert images[HALL["option_id"]] == cards.art("hall-default")
    assert images[PHOTO_HALL["option_id"]] == PHOTO_HALL["photo"]
    _, plain = cards.housing_detail("workflow-1", HALL, HALLS)
    assert plain["hero_image"] == cards.art("hall-default")
    _, photo = cards.housing_detail("workflow-1", PHOTO_HALL, HALLS)
    assert photo["hero_image"] == PHOTO_HALL["photo"]


def test_room_detail_shows_its_carousel_picture() -> None:
    _, carousel = cards.rooms_carousel("workflow-1", [OPTION, PAGE_OPTION], "Purdue")
    for index, item in enumerate(carousel["items"]):
        option = [OPTION, PAGE_OPTION][index]
        _, detail = cards.room_detail("workflow-1", option, index=index)
        assert detail["hero_image"] == item["image"]
    _, wellness = cards.room_detail("workflow-1", OPTION, wellness=True)
    assert wellness["hero_image"] == cards.art("room-wellness")
    _, receipt = cards.room_link_receipt(OPTION)
    assert receipt["hero_image"] == cards.art("hero-receipt")


def test_emergency_flow_keeps_disclaimers_across_native_and_visual_cards() -> None:
    _, overview = cards.service_overview_card("emergency")
    assert overview["hero_image"] == cards.art("svc-emergency")
    assert cards.DEMO_NOTICE in json.dumps(overview, ensure_ascii=False)
    for _, card in (
        cards.emergency_call_card("wf-9", CALL),
        cards.emergency_call_card("wf-9", CALL, CALL_STATUS),
    ):
        children = card["root"]["children"]
        assert children[0] == {
            "type": "badge",
            "label": "Demo drill · not 911",
            "variant": "warning",
        }
        assert children[1]["value"] == cards.DEMO_NOTICE
        assert "In a real emergency, call 911." in children[1]["value"]
        encoded = json.dumps(card, ensure_ascii=False)
        assert not re.search(r"\d{5,}", encoded)  # never more than the last four digits
    _, form = cards.emergency_form()
    assert "not 911" in form["title"] and not _image_urls(form)
    _, review = cards.emergency_review_card("wf-9", PREVIEW)
    assert cards.DEMO_NOTICE in json.dumps(review, ensure_ascii=False)
    assert not _image_urls(review)
