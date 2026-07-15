import json
import re
import structlog

logger = structlog.get_logger()


def _remove_markdown_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines)
    return cleaned


def _extract_json_block(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        return text[start:end]
    return text


def _fix_trailing_commas(text: str) -> str:
    return re.sub(r",\s*([}\]])", r"\1", text)


def _fix_unquoted_keys(text: str) -> str:
    return re.sub(
        r'([\{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:',
        r'\1"\2":',
        text,
    )


def _fix_single_quotes(text: str) -> str:
    result = []
    in_double = False
    in_single = False
    escaped = False

    for ch in text:
        if escaped:
            if in_single and ch == "'":
                result.append("'")
            else:
                result.append("\\" + ch)
            escaped = False
            continue

        if ch == "\\":
            result.append(ch)
            escaped = True
            continue

        if ch == '"' and not in_single:
            in_double = not in_double
            result.append(ch)
        elif ch == "'" and not in_double:
            in_single = not in_single
            result.append('"')
        else:
            result.append(ch)

    return "".join(result)


def _try_parse(text: str) -> dict:
    return json.loads(text)


def _close_truncated_json(text: str) -> str:
    if not text.endswith("}"):
        quote_count = 0
        brace_depth = 0
        bracket_depth = 0
        escaped = False
        for ch in text:
            if escaped:
                escaped = False
                continue
            if ch == "\\":
                escaped = True
                continue
            if ch == '"':
                quote_count += 1
            elif quote_count % 2 == 0:
                if ch == "{":
                    brace_depth += 1
                elif ch == "}":
                    brace_depth -= 1
                elif ch == "[":
                    bracket_depth += 1
                elif ch == "]":
                    bracket_depth -= 1
        closing = ""
        if bracket_depth > 0:
            closing += "]" * bracket_depth
        if brace_depth > 0:
            closing += "}" * brace_depth
        if closing:
            logger.info("json_truncated_repaired", added=closing)
            return text + closing
    return text


def robust_json_parse(text: str) -> dict:
    original = text

    # Strategy 1: Direct parse
    try:
        return _try_parse(text)
    except json.JSONDecodeError:
        pass

    # Pre-process: remove markdown fences
    cleaned = _remove_markdown_fences(text)

    # Strategy 2: Extract between first { and last }
    cleaned = _extract_json_block(cleaned)
    try:
        return _try_parse(cleaned)
    except json.JSONDecodeError:
        pass

    # Strategy 3: Close truncated JSON
    cleaned = _close_truncated_json(cleaned)
    try:
        return _try_parse(cleaned)
    except json.JSONDecodeError:
        pass

    # Strategy 4: Remove trailing commas
    fixed = _fix_trailing_commas(cleaned)
    try:
        return _try_parse(fixed)
    except json.JSONDecodeError:
        pass

    # Strategy 5: Fix unquoted keys
    fixed = _fix_unquoted_keys(cleaned)
    fixed = _fix_trailing_commas(fixed)
    try:
        return _try_parse(fixed)
    except json.JSONDecodeError:
        pass

    # Strategy 6: Fix single quotes
    fixed = _fix_single_quotes(cleaned)
    fixed = _fix_trailing_commas(fixed)
    fixed = _fix_unquoted_keys(fixed)
    try:
        return _try_parse(fixed)
    except json.JSONDecodeError:
        pass

    # Strategy 7: Combined repairs from scratch
    fixed = _fix_single_quotes(_remove_markdown_fences(original))
    fixed = _extract_json_block(fixed)
    fixed = _fix_unquoted_keys(fixed)
    fixed = _fix_trailing_commas(fixed)
    fixed = _close_truncated_json(fixed)
    try:
        return _try_parse(fixed)
    except json.JSONDecodeError:
        pass

    # Strategy 8: Try demjson3
    try:
        import demjson3
        return demjson3.decode(cleaned)
    except (ImportError, Exception):
        pass

    # Strategy 9: Try json-repair
    try:
        from json_repair import repair_json
        return json.loads(repair_json(cleaned))
    except (ImportError, Exception):
        pass

    raise ValueError(f"No se pudo parsear JSON: {original[:300]}")
