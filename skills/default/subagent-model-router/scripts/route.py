#!/usr/bin/env python3
"""Apply subagent-model-router policy to one JSON request."""

from __future__ import annotations

import json
import argparse
import math
from datetime import date
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "reference" / "catalog.json"
TIERS = ("Fast", "Standard", "Premium")
TIER_RANK = {tier: index for index, tier in enumerate(TIERS)}
EFFORT_ORDER = ("low", "medium", "high", "xhigh", "max", "ultra")
EFFORTS = set(EFFORT_ORDER)
WORK_CHOICES = ("bounded", "standard", "coding", "exploration", "planning", "execplan", "review")
REVIEW_CHOICES = ("mechanical", "substantive", "security")
RISK_CHOICES = (
    "security_sensitive", "high_stakes", "unusually_difficult", "repeated_reasoning_failures",
    "user_requested_best_quality", "new_evidence_raises_floor", "stakes_or_ambiguity_increased",
    "important_review_miss",
)
FAILURE_CHOICES = (
    "reasoning_gap", "repeated_constraints_missed", "repeated_reasoning_failures",
    "new_evidence_raises_floor", "context_does_not_fit",
)


class RouteError(ValueError):
    pass


def _object(value, name, allowed):
    if not isinstance(value, dict):
        raise RouteError(f"{name} must be an object")
    unknown = set(value) - set(allowed)
    if unknown:
        raise RouteError(f"{name} has unknown fields: {', '.join(sorted(unknown))}")


class _StoreNamedFlag(argparse.Action):
    def __init__(self, option_strings, dest, value, **kwargs):
        self.value = value
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, name, option_string=None):
        flags = getattr(namespace, self.dest, None)
        if flags is None:
            flags = {}
        flags[name] = self.value
        setattr(namespace, self.dest, flags)


def _validate_request(request):
    _object(request, "request", ("task", "constraints", "usage"))
    task = request.get("task", {})
    _object(task, "task", ("work", "review", "risks", "failure", "selected_tier", "prior_important_miss"))
    if task.get("work", "standard") not in WORK_CHOICES:
        raise RouteError("task.work is invalid")
    if task.get("review") not in (None, *REVIEW_CHOICES):
        raise RouteError("task.review is invalid")
    flag_sets = {
        "risks": RISK_CHOICES,
        "failure": FAILURE_CHOICES,
    }
    for name, allowed in flag_sets.items():
        flags = task.get(name, {})
        _object(flags, f"task.{name}", allowed)
        if any(not isinstance(value, bool) for value in flags.values()):
            raise RouteError(f"task.{name} values must be booleans")
    if "prior_important_miss" in task and not isinstance(task["prior_important_miss"], bool):
        raise RouteError("task.prior_important_miss must be a boolean")
    if task.get("selected_tier") is not None and task["selected_tier"] not in TIERS:
        raise RouteError("task.selected_tier must be Fast, Standard, Premium, or null")
    constraints = request.get("constraints", {})
    _object(constraints, "constraints", ("models", "efforts"))
    for key in ("models", "efforts"):
        if key in constraints and (not isinstance(constraints[key], list) or
                                   not all(isinstance(item, str) and item for item in constraints[key])):
            raise RouteError(f"constraints.{key} must be an array of nonempty strings")
    usage = request.get("usage", {})
    fields = ("input_tokens", "cached_input_tokens", "cache_write_tokens", "output_tokens")
    _object(usage, "usage", (*fields, "cache_reuse_confirmed"))
    for key in fields:
        value = usage.get(key)
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 0):
            raise RouteError(f"usage.{key} must be a non-negative integer or null")
    if "cache_reuse_confirmed" in usage and not isinstance(usage["cache_reuse_confirmed"], bool):
        raise RouteError("usage.cache_reuse_confirmed must be a boolean")


def load_catalog():
    try:
        catalog = json.loads(DATA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RouteError(f"cannot load {DATA.name}: {error}") from None
    if not isinstance(catalog, dict) or catalog.get("schema_version") != 1:
        raise RouteError(f"{DATA.name}: unsupported schema_version")
    if not isinstance(catalog.get("sources"), dict):
        raise RouteError(f"{DATA.name}: sources metadata is missing")
    retired = catalog.get("retired_models")
    if not isinstance(retired, dict) or not isinstance(retired.get("names"), list) or not all(isinstance(name, str) for name in retired["names"]):
        raise RouteError(f"{DATA.name}: invalid retired model list")
    retired_ids = {name.casefold().replace(" ", "-") for name in retired["names"]}
    tier_data = catalog.get("tiers")
    if not isinstance(tier_data, dict) or set(tier_data) != set(TIERS):
        raise RouteError(f"{DATA.name}: tiers must contain Fast, Standard, and Premium")
    candidates = []
    for tier in TIERS:
        rows = tier_data[tier]
        if not isinstance(rows, list) or not rows:
            raise RouteError(f"{DATA.name}: {tier} candidates must be a non-empty array")
        for row in rows:
            required = {"provider", "model", "status", "capability", "eligibility", "effort_spec"}
            if not isinstance(row, dict) or not required.issubset(row):
                raise RouteError(f"{DATA.name}: malformed {tier} candidate")
            if not all(isinstance(row[key], str) and row[key] for key in ("provider", "model", "status", "capability")):
                raise RouteError(f"{DATA.name}: invalid candidate text fields in {tier}")
            if row["model"].casefold() in retired_ids:
                raise RouteError(f"{DATA.name}: retired model {row['model']!r} is a candidate")
            eligibility, spec = row["eligibility"], row["effort_spec"]
            if not isinstance(eligibility, dict):
                raise RouteError(f"{DATA.name}: invalid eligibility metadata for {row['model']!r}")
            allowed_eligibility_fields = {
                "surface_any_of", "plan_any_of", "retired_for_most_users_on",
                "special_retention_confirmation_required", "enterprise_default_enabled",
                "enterprise_admin_enablement_required",
            }
            if set(eligibility) - allowed_eligibility_fields:
                raise RouteError(f"{DATA.name}: unknown eligibility metadata for {row['model']!r}")
            for key in ("surface_any_of", "plan_any_of"):
                if key in eligibility and (not isinstance(eligibility[key], list) or
                                           not all(isinstance(value, str) for value in eligibility[key])):
                    raise RouteError(f"{DATA.name}: invalid {key} for {row['model']!r}")
            for key in ("special_retention_confirmation_required", "enterprise_default_enabled",
                        "enterprise_admin_enablement_required"):
                if key in eligibility and not isinstance(eligibility[key], bool):
                    raise RouteError(f"{DATA.name}: invalid {key} for {row['model']!r}")
            if "retired_for_most_users_on" in eligibility:
                try:
                    date.fromisoformat(eligibility["retired_for_most_users_on"])
                except (TypeError, ValueError):
                    raise RouteError(f"{DATA.name}: invalid retirement date for {row['model']!r}") from None
            if not isinstance(spec, str) or spec.rstrip("+") not in EFFORTS or spec.count("+") > 1:
                raise RouteError(f"{DATA.name}: invalid effort_spec for {row['model']!r}")
            floor_effort = spec.rstrip("+")
            efforts = list(EFFORT_ORDER[EFFORT_ORDER.index(floor_effort):]) if spec.endswith("+") else [spec]
            candidates.append({**row, "tier": tier, "efforts": efforts,
                               "catalog_order": len(candidates)})

    raw_rates = catalog.get("rates")
    if not isinstance(raw_rates, dict) or not raw_rates:
        raise RouteError(f"{DATA.name}: rates must be a non-empty object")
    rates = {}
    for model, rows in raw_rates.items():
        if not isinstance(model, str) or not isinstance(rows, list) or not rows:
            raise RouteError(f"{DATA.name}: malformed rate rows for {model!r}")
        rates[model] = []
        for row in rows:
            required = {"condition", "input", "cached_input", "cache_write", "output"}
            if not isinstance(row, dict) or not required.issubset(row):
                raise RouteError(f"{DATA.name}: malformed price row for {model!r}")
            condition = row["condition"]
            match = re.fullmatch(r"([≤>])([0-9]+)K", condition) if isinstance(condition, str) else None
            promo = re.fullmatch(r"promotional (through|before) ([0-9]{4}-[0-9]{2}-[0-9]{2})", condition) if isinstance(condition, str) else None
            if condition != "default" and match is None and promo is None:
                raise RouteError(f"{DATA.name}: unsupported price condition {condition!r}")
            values = {key: row[key] for key in ("input", "cached_input", "cache_write", "output")}
            if any(value is not None and (not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value < 0) for value in values.values()):
                raise RouteError(f"{DATA.name}: invalid rate for {model!r}")
            expiry = promo.group(2) if promo else None
            if expiry:
                try:
                    date.fromisoformat(expiry)
                except ValueError:
                    raise RouteError(f"{DATA.name}: invalid promotion expiry for {model!r}") from None
            rates[model].append({"condition": condition, "limit": int(match.group(2)) * 1000 if match else None,
                                 "operator": match.group(1) if match else None, "expires": expiry,
                                 "expiry_inclusive": promo.group(1) == "through" if promo else False, **values})
    defaults = catalog.get("task_defaults")
    if not isinstance(defaults, list):
        raise RouteError(f"{DATA.name}: task_defaults must be an array")
    return candidates, rates, defaults


def _applicable_rate(rows, input_tokens):
    if not rows:
        return None
    if input_tokens is not None:
        for row in rows:
            operator = row["operator"]
            limit = row["limit"]
            if operator == "≤" and input_tokens <= limit:
                return row
            if operator == ">" and input_tokens > limit:
                return row
    default = next((row for row in rows if row["condition"] == "default"), None)
    if default:
        return default
    today = date.today().isoformat()
    return next((row for row in rows if row["expires"] and
                 (today < row["expires"] or row["expiry_inclusive"] and today == row["expires"])), None)


def _floor(task):
    work = task.get("work", "standard")
    review = task.get("review")
    risks = task.get("risks", {})
    failure = task.get("failure", {})
    if not isinstance(risks, dict) or not isinstance(failure, dict):
        raise RouteError("task risks and failure must be objects")
    if review == "security":
        return "Premium", "security review floor"
    premium_flags = (
        "security_sensitive", "high_stakes", "unusually_difficult",
        "repeated_reasoning_failures", "user_requested_best_quality",
        "new_evidence_raises_floor", "stakes_or_ambiguity_increased",
    )
    if any(risks.get(flag) is True for flag in premium_flags) or any(
        failure.get(flag) is True for flag in (
            "repeated_reasoning_failures", "new_evidence_raises_floor",
        )
    ):
        return "Premium", "task facts require Premium"
    if review is not None:
        if review not in ("mechanical", "substantive", "security"):
            raise RouteError("task.review must be mechanical, substantive, security, or null")
        if task.get("prior_important_miss") is True or risks.get("important_review_miss") is True:
            return "Premium", "prior important review miss establishes Premium floor"
        return ("Fast", "mechanical review") if review == "mechanical" else ("Standard", "ordinary review")
    if work in ("planning", "execplan"):
        return "Standard", "planning work"
    if work in ("bounded", "exploration"):
        return "Fast", "bounded low-risk work"
    if work in ("standard", "coding"):
        return "Standard", "substantive task"
    raise RouteError("task.work must be bounded, standard, coding, exploration, planning, or execplan")


def _cost(candidate, rates, usage):
    if usage.get("input_tokens") is None or usage.get("output_tokens") is None:
        return None, ["input and output token estimates were not both supplied"]
    if any(key in usage and usage[key] is None for key in ("cached_input_tokens", "cache_write_tokens")):
        return None, ["cache token estimate is unknown"]
    cached = usage.get("cached_input_tokens") or 0
    written = usage.get("cache_write_tokens") or 0
    uncached = usage["input_tokens"]
    row = _applicable_rate(rates.get(candidate["model"], []), uncached + cached + written)
    if row is None:
        return None, ["no applicable bundled price row; a promotion may have expired"]
    if not usage.get("cache_reuse_confirmed", False):
        uncached += cached
        cached = 0
    total = 0.0
    for amount, field in ((uncached, "input"), (cached, "cached_input"),
                          (written, "cache_write"), (usage["output_tokens"], "output")):
        if amount and row[field] is None:
            return None, [f"{field} rate is not listed"]
        total += amount * (row[field] or 0) / 1_000_000
    return round(total, 10), []


def _planning_pairs(defaults):
    matching = [item for item in defaults if isinstance(item, dict) and item.get("name") == "Planning"]
    if len(matching) != 1 or not isinstance(matching[0].get("alternatives"), list):
        raise RouteError(f"{DATA.name}: exactly one valid Planning default is required")
    pairs = [matching[0].get("starting"), *matching[0]["alternatives"]]
    if any(not isinstance(pair, dict) or set(pair) != {"model", "effort"} or
           not isinstance(pair["model"], str) or pair["effort"] not in EFFORT_ORDER for pair in pairs):
        raise RouteError(f"{DATA.name}: invalid Planning configuration")
    return [(pair["model"], pair["effort"]) for pair in pairs]


def _rank_candidates(selected, rates, planning):
    order = {model: index for index, (model, _) in enumerate(planning or [])}
    def baseline(item):
        row = _applicable_rate(rates.get(item["model"], []), 0)
        if row is None or row["input"] is None or row["output"] is None:
            return float("inf")
        return row["input"] + row["output"]

    selected.sort(key=lambda item: (
        item["estimated_cost_usd"] is None,
        item["estimated_cost_usd"] if item["estimated_cost_usd"] is not None else baseline(item),
        order.get(item["model"], len(order)), bool(item["eligibility"]), item["catalog_order"], item["effort"],
    ))
    if not planning:
        family = re.fullmatch(r"(.*?)(\d+(?:\.\d+)?)(.*)", selected[0]["model"])
        if family:
            def comparable(item):
                match = re.fullmatch(r"(.*?)(\d+(?:\.\d+)?)(.*)", item["model"])
                return (match and (match.group(1), match.group(3)) == (family.group(1), family.group(3))
                        and item["estimated_cost_usd"] == selected[0]["estimated_cost_usd"]
                        and (item["estimated_cost_usd"] is not None or baseline(item) == baseline(selected[0])))
            peers = [item for item in selected if comparable(item)]
            newest = max(peers, key=lambda item: tuple(int(part) for part in
                         re.fullmatch(r"(.*?)(\d+(?:\.\d+)?)(.*)", item["model"]).group(2).split(".")))
            selected.remove(newest)
            selected.insert(0, newest)
    if planning:
        starting = next((item for item in selected if (item["model"], item["effort"]) == planning[0]), None)
        if starting is None:
            starting = next((item for item in selected if item["model"] == planning[0][0]), None)
        if starting is not None:
            selected.remove(starting)
            selected.insert(0, starting)


def route(request):
    _validate_request(request)
    task = request.get("task", {})
    constraints = request.get("constraints", {})
    usage = request.get("usage", {})
    floor, reason = _floor(task)
    start = max((floor, task.get("selected_tier") or floor), key=TIER_RANK.get)
    failure = task.get("failure", {})
    if ((task.get("prior_important_miss") is True and task.get("review") is None) or
            failure.get("reasoning_gap") is True or failure.get("repeated_constraints_missed") is True or
            failure.get("context_does_not_fit") is True):
        floor = TIERS[min(TIER_RANK[start] + 1, len(TIERS) - 1)]
        start = max((floor, start), key=TIER_RANK.get)
        reason += "; one-tier escalation for a diagnosed capability gap"
    work = task.get("work", "standard")
    effort_required = (work in ("planning", "execplan") or
                       task.get("review") in ("substantive", "security") or
                       "efforts" in constraints)
    effort_policy = "explicit" if effort_required else "host_default"
    candidates, rates, defaults = load_catalog()
    planning = None
    if work in ("planning", "execplan"):
        planning = _planning_pairs(defaults)
    eligible = []
    for candidate in candidates:
        for effort in candidate["efforts"]:
            if TIER_RANK[candidate["tier"]] < TIER_RANK[start]:
                continue
            if "models" in constraints and candidate["model"] not in constraints["models"]:
                continue
            if "efforts" in constraints and effort not in constraints["efforts"]:
                continue
            item = {**candidate, "effort": effort}
            item["estimated_cost_usd"], item["cost_unknowns"] = _cost(item, rates, usage)
            eligible.append(item)
    if planning is not None and "models" not in constraints:
        eligible = [item for item in eligible if item["model"] in {model for model, _ in planning}]
    tier = next((name for name in TIERS[TIER_RANK[start]:] if any(item["tier"] == name for item in eligible)), None)
    if tier is None:
        return {"recommendation_available": False, "availability_verified": False, "floor": floor,
                "tier": None, "model": None, "reasoning_effort": None,
                "effort_policy": effort_policy, "capability_at_host_default_verified": False,
                "reason": reason + "; no catalog configuration meets the floor and constraints",
                "fallback": "none", "estimated_cost_usd": None, "cost_minimum_verified": False}
    selected = [item for item in eligible if item["tier"] == tier]
    _rank_candidates(selected, rates, planning)
    chosen = selected[0]
    alternative = next((item for item in selected[1:]
                        if effort_policy == "explicit" or item["model"] != chosen["model"]), None)
    reason += "; provisional catalog fit; live availability is not verified"
    if planning and chosen["model"] == planning[0][0]:
        reason += "; Planning starting model is preferred"
    reason += "; GitHub Copilot token estimates exclude retries, verification, and other overhead"
    if chosen["estimated_cost_usd"] is None:
        reason += "; token estimates or applicable rates are incomplete; ranking uses equal uncached input and output unit rates at ordinary context"
    if TIER_RANK[tier] > TIER_RANK[floor]:
        reason += f"; selected {tier} from requested tier {start}; task floor remains {floor}"
    fallback = ({"model": alternative["model"],
                 "reasoning_effort": alternative["effort"] if effort_required else None,
                 "effort_policy": effort_policy,
                 "capability_at_host_default_verified": False} if alternative else "none")
    return {"recommendation_available": True, "availability_verified": False, "floor": floor, "tier": tier,
            "model": chosen["model"], "reasoning_effort": chosen["effort"] if effort_required else None,
            "effort_policy": effort_policy, "capability_at_host_default_verified": False, "reason": reason,
            "escalation_trigger": "verification reveals a reasoning gap",
            "fallback": fallback,
            "catalog_restrictions": chosen["eligibility"],
            "fallback_restrictions": alternative["eligibility"] if alternative else {},
            "estimated_cost_usd": chosen["estimated_cost_usd"], "cost_minimum_verified": False,
            }


def main():
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description="Recommend a model and effort policy from task facts, constraints, and optional token estimates.",
        epilog=(
            "JSON fields and defaults:\n"
            "  task.work: standard; task.review and task.selected_tier: unset.\n"
            "  task.risks and task.failure: all supported flags default false.\n"
            "  task.prior_important_miss: false. Model/effort constraints are unrestricted\n"
            "  when omitted, except Planning uses its catalog pool unless models are given.\n"
            "  Missing input/output token counts make cost unknown. Omitted cache token\n"
            "  counts are zero; cache reuse confirmation defaults false.\n"
            "\n"
            "Choice meanings:\n"
            "  work: bounded (narrow), standard (ordinary), coding (substantive code),\n"
            "  exploration (bounded, low-risk exploration), planning, execplan, review\n"
            "  (supply --review with it).\n"
            "  review: mechanical (non-semantic changes, straightforward verification),\n"
            "  substantive (judgment), security (security).\n"
            "  risks: security_sensitive (security), high_stakes (serious consequences),\n"
            "  unusually_difficult (hard task), repeated_reasoning_failures (recurring),\n"
            "  user_requested_best_quality (explicit request), new_evidence_raises_floor\n"
            "  (new facts), stakes_or_ambiguity_increased (higher uncertainty),\n"
            "  important_review_miss (prior review error).\n"
            "  failures: reasoning_gap (reasoning failed), repeated_constraints_missed\n"
            "  (constraints missed again), repeated_reasoning_failures (recurring),\n"
            "  new_evidence_raises_floor (new facts), context_does_not_fit (only when no\n"
            "  suitable same-tier configuration fits).\n"
            "  efforts: low, medium, high, xhigh, max, ultra; each step raises effort.\n"
            "  Token counts are non-negative integers: input-tokens is uncached input;\n"
            "  cached-input-tokens and cache-write-tokens are separate cache amounts.\n"
            "  The rate threshold uses their sum. Output tokens are separate.\n"
            "\n"
            "Input and precedence:\n"
            "  With no flags or --input, read one JSON request from stdin. --input FILE\n"
            "  reads a file; --input - explicitly combines stdin JSON with flags. Flags\n"
            "  alone use an empty request and do not read stdin. Supplied flags override\n"
            "  only their JSON fields. Each --risk/--no-risk or --failure/--no-failure\n"
            "  occurrence sets that value; the last occurrence wins. Repeated --model/--effort\n"
            "  replace the JSON list. JSON is validated before any override.\n"
            "\n"
            "Output and limits:\n"
            "  Success writes one JSON object to stdout (exit 0). Errors go to stderr\n"
            "  (exit 2). recommendation_available=false means no catalog match; it is\n"
            "  still a valid result with exit 0. effort_policy is explicit for planning,\n"
            "  execplan, substantive/security review, or a user effort constraint; otherwise\n"
            "  it is host_default and reasoning_effort is null. The caller omits the effort\n"
            "  argument in host_default mode. Host-default capability is unverified.\n"
            "  Live availability is not verified, and\n"
            "  estimated cost is not a verified minimum. If token estimates or rates\n"
            "  are incomplete, ranking assumes equal uncached input/output unit rates\n"
            "  at ordinary context. GitHub Copilot estimates exclude retries, verification,\n"
            "  and other overhead. The caller checks the returned model and\n"
            "  checks the required model control and, for explicit policy, the exact effort\n"
            "  control before dispatch.\n"
            "\n"
            "Examples:\n"
            "  python3 route.py --work bounded\n"
            "  python3 route.py --input request.json --review substantive --risk high_stakes\n"
            "  cat request.json | python3 route.py --input - --no-risk high_stakes"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-i", "--input", metavar="FILE", default=None,
                        help="JSON request file; use - to explicitly read stdin with flags")
    task = parser.add_argument_group("Task fields")
    task.add_argument("--work", choices=WORK_CHOICES,
                      help="task.work (default: standard; see choice meanings below)")
    task.add_argument("--review", choices=REVIEW_CHOICES,
                      help="task.review; omit for no review")
    task.add_argument("--selected-tier", choices=TIERS,
                      help="task.selected_tier minimum tier (Fast, Standard, Premium)")
    task.add_argument("--risk", dest="risk_flags", action=_StoreNamedFlag, value=True,
                      choices=RISK_CHOICES, metavar="NAME",
                      help="set task.risks.NAME true; repeatable")
    task.add_argument("--no-risk", dest="risk_flags", action=_StoreNamedFlag, value=False,
                      choices=RISK_CHOICES, metavar="NAME",
                      help="set task.risks.NAME false; repeatable")
    task.add_argument("--failure", dest="failure_flags", action=_StoreNamedFlag, value=True,
                      choices=FAILURE_CHOICES, metavar="NAME",
                      help="set task.failure.NAME true; repeatable")
    task.add_argument("--no-failure", dest="failure_flags", action=_StoreNamedFlag, value=False,
                      choices=FAILURE_CHOICES, metavar="NAME",
                      help="set task.failure.NAME false; repeatable")
    for flag, value in (("--prior-important-miss", True), ("--no-prior-important-miss", False)):
        task.add_argument(flag, dest="prior_important_miss", action="store_const", const=value,
                          default=None, help=f"set task.prior_important_miss {str(value).lower()}")

    constraints = parser.add_argument_group("Constraints")
    constraints.add_argument("--model", action="append", metavar="ID",
                             help="add ID to constraints.models; repeatable and replaces JSON list")
    constraints.add_argument("--effort", action="append", choices=EFFORT_ORDER, metavar="LEVEL",
                             help="add LEVEL to constraints.efforts; repeatable and replaces JSON list (see meanings below)")

    usage = parser.add_argument_group("Token usage")
    for option, field in (("--input-tokens", "input_tokens"),
                          ("--cached-input-tokens", "cached_input_tokens"),
                          ("--cache-write-tokens", "cache_write_tokens"),
                          ("--output-tokens", "output_tokens")):
        usage.add_argument(option, dest=field, type=_nonnegative_int, metavar="COUNT",
                           help=f"usage.{field}; non-negative integer (see token semantics below)")
    cache_group = usage.add_mutually_exclusive_group()
    cache_group.add_argument("--cache-reuse-confirmed", dest="cache_reuse_confirmed",
                             action="store_const", const=True, default=None,
                             help="set usage.cache_reuse_confirmed true")
    cache_group.add_argument("--no-cache-reuse-confirmed", dest="cache_reuse_confirmed",
                             action="store_const", const=False,
                             help="set usage.cache_reuse_confirmed false")
    args = parser.parse_args()
    options = vars(args).copy()
    options.pop("input")
    has_flags = any(value is not None for value in options.values())
    if ((args.input is None and not has_flags) or args.input == "-") and sys.stdin.isatty():
        print("route: no JSON on stdin; use --input FILE or pipe a JSON request", file=sys.stderr)
        return 2
    try:
        if args.input == "-" or (args.input is None and not has_flags):
            request = json.load(sys.stdin)
        elif args.input is None:
            request = {}
        else:
            try:
                with open(args.input, encoding="utf-8") as request_file:
                    request = json.load(request_file)
            except OSError as error:
                raise RouteError(f"cannot read {args.input!r}: {error.strerror or error}") from None
        _validate_request(request)
        _apply_flags(request, args)
        print(json.dumps(route(request), sort_keys=True))
        return 0
    except (json.JSONDecodeError, RouteError, OSError, KeyError, ValueError) as error:
        label = "invalid JSON" if isinstance(error, json.JSONDecodeError) else str(error)
        print(f"route: {label}", file=sys.stderr)
        return 2


def _nonnegative_int(value):
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a non-negative integer") from None
    if number < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return number


def _apply_flags(request, args):
    task_flags = {
        "work": args.work,
        "review": args.review,
        "selected_tier": args.selected_tier,
        "prior_important_miss": args.prior_important_miss,
    }
    has_task_flags = (any(value is not None for value in task_flags.values()) or
                      args.risk_flags or args.failure_flags)
    task = request.setdefault("task", {}) if has_task_flags else None
    if task is not None:
        for key, value in task_flags.items():
            if value is not None:
                task[key] = value
        for key, flags in (("risks", args.risk_flags), ("failure", args.failure_flags)):
            if flags:
                task.setdefault(key, {}).update(flags)
    constraint_fields = {"models": args.model, "efforts": args.effort}
    constraints = request.setdefault("constraints", {}) if any(
        value is not None for value in constraint_fields.values()) else request.get("constraints", {})
    for key, value in constraint_fields.items():
        if value is not None:
            constraints[key] = value
    usage_fields = {"input_tokens": args.input_tokens, "cached_input_tokens": args.cached_input_tokens,
                    "cache_write_tokens": args.cache_write_tokens, "output_tokens": args.output_tokens,
                    "cache_reuse_confirmed": args.cache_reuse_confirmed}
    if any(value is not None for value in usage_fields.values()):
        usage = request.setdefault("usage", {})
        for key, value in usage_fields.items():
            if value is not None:
                usage[key] = value


if __name__ == "__main__":
    raise SystemExit(main())
