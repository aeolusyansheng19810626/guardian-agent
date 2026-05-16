"""End-to-end UI smoke test for Guardian Agent.

Boots a Streamlit dev server on a free port, drives the page with Playwright,
and asserts each high-visibility feature works. The only network call gated
behind real LLM credentials is the Run button — without keys we expect a
graceful error path rather than a successful "done" state.
"""
from __future__ import annotations

import os
import re
import socket
import subprocess
import sys
import time

# Force UTF-8 on stdout/stderr so em-dashes and CJK don't crash on cp932 hosts.
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass
from contextlib import closing
from pathlib import Path

from playwright.sync_api import (
    Browser,
    BrowserContext,
    FrameLocator,
    Page,
    Playwright,
    expect,
    sync_playwright,
)

REPO = Path(__file__).resolve().parent.parent


def _free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _start_streamlit(port: int) -> subprocess.Popen:
    env = os.environ.copy()
    env["STREAMLIT_BROWSER_GATHERUSAGESTATS"] = "false"
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["PYTHONIOENCODING"] = "utf-8"
    log_path = REPO / "tests" / "_streamlit.log"
    log_path.unlink(missing_ok=True)
    log_file = open(log_path, "w", encoding="utf-8", errors="replace")
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            f"--server.port={port}",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
        ],
        cwd=str(REPO),
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )
    proc._log_file = log_file  # type: ignore[attr-defined]
    proc._log_path = log_path  # type: ignore[attr-defined]
    deadline = time.time() + 30
    while time.time() < deadline:
        if proc.poll() is not None:
            log = log_path.read_text(encoding="utf-8", errors="replace")
            raise RuntimeError(f"streamlit exited early\n{log}")
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                time.sleep(2.0)  # let it warm up + script first-run
                return proc
        except OSError:
            time.sleep(0.3)
    raise RuntimeError("streamlit did not start in 30s")


def _stop(proc: subprocess.Popen) -> None:
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        proc.kill()


# --- Test cases ---


def get_iframe(page: Page) -> FrameLocator:
    """Return the FrameLocator for the guardian_ui custom component iframe."""
    selector = 'iframe[title*="guardian_ui"], iframe[src*="components.guardian_ui"], iframe[src*="component"]'
    try:
        page.locator(selector).first.wait_for(state="attached", timeout=45_000)
    except Exception:
        # Dump everything we can see for debugging
        try:
            page.screenshot(path=str(REPO / "tests" / "_debug_page.png"))
            html = page.content()
            (REPO / "tests" / "_debug_page.html").write_text(
                html, encoding="utf-8", errors="replace"
            )
            iframes = page.evaluate(
                "() => Array.from(document.querySelectorAll('iframe'))"
                ".map(f => ({title: f.title, src: f.src, id: f.id}))"
            )
            print("[debug] iframes seen:", iframes)
        except Exception as derr:
            print("[debug] screenshot failed:", derr)
        raise
    return page.frame_locator(selector).first


def assert_idle_renders(frame: FrameLocator) -> None:
    expect(frame.locator("text=Guardian Agent").first).to_be_visible(timeout=15_000)
    # Idle hero CTA buttons (Chinese default lang)
    expect(frame.get_by_role("button", name=re.compile("运行样例"))).to_be_visible()


def test_initial_idle(frame: FrameLocator) -> dict:
    assert_idle_renders(frame)
    # Top tabs visible
    expect(frame.get_by_role("tab", name=re.compile("交付物审查"))).to_be_visible()
    expect(frame.get_by_role("tab", name=re.compile("障害报告审查"))).to_be_visible()
    return {"name": "initial idle", "ok": True}


def test_tab_switch(frame: FrameLocator) -> dict:
    delivery_tab = frame.get_by_role("tab", name=re.compile("交付物审查"))
    delivery_tab.click()
    expect(frame.locator(".page-title")).to_have_text(
        re.compile("交付物审查"), timeout=5_000
    )
    incident_tab = frame.get_by_role("tab", name=re.compile("障害报告审查"))
    incident_tab.click()
    expect(frame.locator(".page-title")).to_have_text(
        re.compile("障害报告审查"), timeout=5_000
    )
    return {"name": "tab switch", "ok": True}


def test_language_switch(frame: FrameLocator) -> dict:
    # Click "EN"
    frame.locator(".seg .seg-btn", has_text="EN").first.click()
    expect(frame.locator(".page-title")).to_have_text(
        re.compile("Incident report|Deliverable", re.IGNORECASE), timeout=5_000
    )
    # 日
    frame.locator(".seg .seg-btn", has_text="日").first.click()
    expect(frame.locator(".page-title")).to_have_text(
        re.compile("障害|成果物"), timeout=5_000
    )
    # back to 中
    frame.locator(".seg .seg-btn", has_text="中").first.click()
    expect(frame.locator(".page-title")).to_have_text(
        re.compile("障害|交付物"), timeout=5_000
    )
    return {"name": "language switch zh/ja/en", "ok": True}


def _component_frame(page: Page):
    """Resolve the actual playwright Frame (not FrameLocator) for the iframe."""
    handle = page.locator(
        'iframe[title*="guardian_ui"], iframe[src*="components.guardian_ui"], iframe[src*="component"]'
    ).first.element_handle()
    if handle is None:
        return None
    return handle.content_frame()


def _poll_attr(f, expr: str, expected: str, timeout_ms: int = 8000) -> str:
    """Poll an evaluate-expression until it equals `expected` (case-insensitive)."""
    deadline = time.time() + timeout_ms / 1000
    last = ""
    while time.time() < deadline:
        last = f.evaluate(expr)
        if str(last).strip().lower() == expected.lower():
            return last
        time.sleep(0.2)
    return last


def test_theme_switch(frame: FrameLocator, page: Page) -> dict:
    moon_btn = frame.locator(
        'button.icon-btn[title*="深色"], button.icon-btn[title*="dark" i]'
    ).first
    moon_btn.click()
    f = _component_frame(page)
    assert f is not None, "could not resolve component iframe"
    theme = _poll_attr(
        f, "() => document.documentElement.getAttribute('data-theme')", "dark"
    )
    assert theme == "dark", f"expected dark, got {theme!r}"

    sun_btn = frame.locator(
        'button.icon-btn[title*="浅色"], button.icon-btn[title*="light" i]'
    ).first
    sun_btn.click()
    theme = _poll_attr(
        f, "() => document.documentElement.getAttribute('data-theme')", "light"
    )
    assert theme == "light", f"expected light, got {theme!r}"
    return {"name": "theme switch light/dark", "ok": True}


def test_palette_switch(frame: FrameLocator, page: Page) -> dict:
    swatch_btn = frame.locator('button.icon-btn[title*="主色"]').first
    swatch_btn.click()
    frame.locator('button[title="indigo"]').first.click()
    f = _component_frame(page)
    assert f is not None, "could not resolve component iframe"
    brand_600 = _poll_attr(
        f,
        "() => getComputedStyle(document.documentElement)"
        ".getPropertyValue('--brand-600').trim()",
        "#4f46e5",
    )
    assert brand_600.lower() == "#4f46e5", f"expected indigo, got {brand_600!r}"

    swatch_btn.click()
    frame.locator('button[title="emerald"]').first.click()
    brand_600 = _poll_attr(
        f,
        "() => getComputedStyle(document.documentElement)"
        ".getPropertyValue('--brand-600').trim()",
        "#059669",
    )
    assert brand_600.lower() == "#059669", f"expected emerald, got {brand_600!r}"
    return {"name": "palette switch", "ok": True}


def test_sample_button(frame: FrameLocator) -> dict:
    # Idle hero "运行样例" populates input and stays in idle (controller
    # handles USE_SAMPLE).
    frame.get_by_role("button", name=re.compile("运行样例")).click()
    textarea = frame.locator("textarea.textarea")
    expect(textarea).not_to_have_value("", timeout=5_000)
    val = textarea.input_value()
    assert "障害" in val or "服务器" in val, f"unexpected sample text: {val[:80]}"
    return {"name": "sample button populates textarea", "ok": True}


def test_clear_button(frame: FrameLocator) -> dict:
    frame.locator("textarea.textarea").fill("temp content")
    # The InputPanel clear button is the second .btn-lg in that card; the
    # first is the primary Run button. Match by exact "清空" text inside the
    # input card to avoid hitting the sidebar's "清空历史".
    frame.locator(".card .row > button.btn.btn-lg", has_text=re.compile(r"^\s*清空\s*$")).first.click()
    expect(frame.locator("textarea.textarea")).to_have_value("", timeout=5_000)
    return {"name": "clear button empties textarea", "ok": True}


def test_run_button_triggers_running(frame: FrameLocator) -> dict:
    """Without API keys the graph will fail — but we should at least see the
    UI flip into the 'running' state momentarily before the Streamlit error
    surfaces."""
    # Fill the input
    frame.locator("textarea.textarea").fill(
        "测试输入：需求文档缺少风险章节。"
    )
    run_btn = frame.get_by_role("button", name=re.compile("开始审查"))
    run_btn.click()
    # The component re-renders with state="running" — we look for either the
    # spinner button or the "Agent 编排执行中" copy. Either is acceptable.
    try:
        expect(
            frame.locator("text=Agent 编排执行中").first
        ).to_be_visible(timeout=8_000)
        return {"name": "run button → running state", "ok": True}
    except Exception:
        # If keys aren't configured, the graph build itself may fail and the
        # state never enters running — count that as a soft pass for now and
        # report explicitly.
        return {
            "name": "run button → running state",
            "ok": False,
            "note": "did not see 'running' UI within 8s (likely auth failure)",
        }


def main() -> int:
    port = _free_port()
    print(f"[boot] streamlit on http://localhost:{port}")
    proc = _start_streamlit(port)
    results: list[dict] = []
    try:
        with sync_playwright() as p:
            browser: Browser = p.chromium.launch(headless=True)
            ctx: BrowserContext = browser.new_context(
                viewport={"width": 1440, "height": 900}
            )
            page = ctx.new_page()
            page.on("console", lambda m: print(f"[console:{m.type}] {m.text}"))
            page.on("pageerror", lambda e: print(f"[pageerror] {e}"))
            page.goto(f"http://localhost:{port}/", wait_until="networkidle", timeout=60_000)
            frame = get_iframe(page)
            # Wait for initial idle render
            assert_idle_renders(frame)

            for fn in (
                test_initial_idle,
                test_tab_switch,
                test_language_switch,
                test_sample_button,
                test_clear_button,
            ):
                try:
                    results.append(fn(frame))
                except Exception as err:  # noqa: BLE001
                    results.append({"name": fn.__name__, "ok": False, "error": repr(err)})

            for fn in (test_theme_switch, test_palette_switch):
                try:
                    results.append(fn(frame, page))
                except Exception as err:  # noqa: BLE001
                    results.append({"name": fn.__name__, "ok": False, "error": repr(err)})

            try:
                results.append(test_run_button_triggers_running(frame))
            except Exception as err:  # noqa: BLE001
                results.append({"name": "run button", "ok": False, "error": repr(err)})

            browser.close()
    finally:
        _stop(proc)
        try:
            log_file = proc._log_file  # type: ignore[attr-defined]
            log_file.close()
            log_path = proc._log_path  # type: ignore[attr-defined]
            print(f"\n[streamlit log] {log_path}")
            print(log_path.read_text(encoding="utf-8", errors="replace")[-4000:])
        except Exception:
            pass

    print("\n=== Results ===")
    failed = 0
    for r in results:
        flag = "OK" if r.get("ok") else "FAIL"
        line = f"[{flag}] {r['name']}"
        if "error" in r:
            line += f" — {r['error']}"
        if "note" in r:
            line += f" — {r['note']}"
        print(line)
        if not r.get("ok"):
            failed += 1
    print(f"\n{len(results) - failed}/{len(results)} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
