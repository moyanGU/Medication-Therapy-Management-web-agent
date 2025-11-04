#!/usr/bin/env python3
"""
Diagnostic script to inspect the actual implementation of
apps.authentication.views.send_verification_code inside the backend container.

It performs three checks:
1) Closure search: Traverse DRF wrapper closures to locate the original
   send_verification_code function and print its source.
2) Direct file read: Open apps/authentication/views.py and print the code
   around the send_verification_code definition with line numbers.
3) URL route resolution: Resolve '/api/auth/send-code/' and print the
   resolved callable and its wrapper class (if any).

This script assumes the project root in the container is /app.
"""

import os
import inspect
from pathlib import Path


def setup_django_env() -> None:
    """Ensure DJANGO_SETTINGS_MODULE is set and initialize Django."""
    if "DJANGO_SETTINGS_MODULE" not in os.environ:
        os.environ["DJANGO_SETTINGS_MODULE"] = "mtm_helper.settings"
    print(f"DJANGO_SETTINGS_MODULE={os.environ['DJANGO_SETTINGS_MODULE']}")
    import django
    django.setup()


def closure_search() -> None:
    """Try to locate the original function via DRF wrapper closures and print it."""
    from apps.authentication import views

    f = views.send_verification_code
    print("outer:", getattr(f, "__name__", None), getattr(f, "__module__", None))

    cls = getattr(f, "cls", None) or getattr(f, "view_class", None)
    print("cls:", cls)

    orig = None
    if cls:
        for method_name in ("post", "get", "put", "patch"):
            if hasattr(cls, method_name):
                method = getattr(cls, method_name)
                cells = getattr(method, "__closure__", None) or ()
                for cell in cells:
                    val = getattr(cell, "cell_contents", None)
                    if callable(val) and getattr(val, "__name__", "") == "send_verification_code":
                        orig = val
                        break
                if orig:
                    break

    print(
        "orig func:",
        orig,
        getattr(orig, "__module__", None) if orig else None,
        getattr(orig, "__name__", None) if orig else None,
    )
    if orig:
        try:
            print(inspect.getsource(orig))
        except Exception as e:
            print("inspect.getsource(orig) failed:", e)
    else:
        print("Could not locate original function via closure search.")


def _select_views_py() -> Path | None:
    """Select the views.py path inside the container or local mapping."""
    candidates = [
        Path("/app/apps/authentication/views.py"),
        Path.cwd() / "apps" / "authentication" / "views.py",
        Path(__file__).resolve().parent / "apps" / "authentication" / "views.py",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def print_views_snippet() -> None:
    """Print a snippet around the send_verification_code definition with line numbers."""
    p = _select_views_py()
    print("views.py path:", p)
    if not p or not p.exists():
        print("views.py not found in expected locations.")
        return
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        text = p.read_text()
    lines = text.splitlines()

    target_line = None
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("def send_verification_code"):
            target_line = i
            break

    if target_line is None:
        print("def send_verification_code not found in views.py")
        return

    start = max(1, target_line - 5)
    end = min(len(lines), target_line + 80)
    print(f"----- {p} lines {start}..{end} -----")
    for j in range(start, end + 1):
        print(f"{j:04d}: {lines[j - 1]}")


def resolve_route() -> None:
    """Resolve the URL route to confirm which view is bound."""
    from django.urls import resolve

    try:
        r = resolve("/api/auth/send-code/")
        pattern = getattr(r, "route", None) or getattr(r, "pattern", None)
        print("route.resolve:", pattern)
        func = r.func
        print("resolved func:", func)
        print(
            "resolved func name/module:",
            getattr(func, "__name__", None),
            getattr(func, "__module__", None),
        )
        view_class = getattr(func, "view_class", None) or getattr(func, "cls", None)
        if view_class:
            print("wrapped view class:", view_class)
            print("wrapped view class module:", getattr(view_class, "__module__", None))
    except Exception as e:
        print('resolve("/api/auth/send-code/") failed:', e)


def main() -> None:
    setup_django_env()
    print("=== Closure search for original function ===")
    closure_search()
    print("=== Direct views.py snippet ===")
    print_views_snippet()
    print("=== URL route resolution ===")
    resolve_route()


if __name__ == "__main__":
    main()