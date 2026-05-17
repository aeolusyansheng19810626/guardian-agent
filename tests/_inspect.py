"""Quick DOM probe to find Streamlit chrome selectors and iframe positioning."""
import json
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_context(viewport={"width": 1440, "height": 900}).new_page()
    pg.goto("http://localhost:8530/", wait_until="networkidle", timeout=60_000)
    # Give the websocket script a few seconds to actually render the iframe
    pg.wait_for_selector('iframe[title*="guardian_ui"]', timeout=30_000)
    pg.wait_for_timeout(2000)

    info = pg.evaluate(
        """() => {
            const result = {};
            result.testids = Array.from(document.querySelectorAll('[data-testid]'))
                .slice(0, 50)
                .map(e => {
                    const r = e.getBoundingClientRect();
                    return {
                        t: e.getAttribute('data-testid'),
                        tag: e.tagName,
                        rect: { x: Math.round(r.left), y: Math.round(r.top),
                                w: Math.round(r.width), h: Math.round(r.height) }
                    };
                });
            const iframe = document.querySelector('iframe[title*="guardian_ui"]');
            if (iframe) {
                const r = iframe.getBoundingClientRect();
                result.iframe = {
                    x: Math.round(r.left), y: Math.round(r.top),
                    w: Math.round(r.width), h: Math.round(r.height),
                    title: iframe.title
                };
                const chain = [];
                let n = iframe;
                while (n && n !== document.body) {
                    n = n.parentElement;
                    if (!n) break;
                    const cs = getComputedStyle(n);
                    const r2 = n.getBoundingClientRect();
                    chain.push({
                        tag: n.tagName,
                        cls: (n.className || '').slice(0, 80),
                        testid: n.getAttribute('data-testid'),
                        pad: cs.padding, mar: cs.margin,
                        h: Math.round(r2.height), y: Math.round(r2.top)
                    });
                }
                result.chain = chain;
                result.bodyHeight = document.body.scrollHeight;
                result.docHeight = document.documentElement.scrollHeight;
                result.windowHeight = window.innerHeight;
            }
            // Find any <style> blocks containing our marker
            const styles = Array.from(document.querySelectorAll('style'));
            result.matchingStyles = styles.filter(s => /stHeader|guardian_ui/.test(s.textContent || ''))
                .map(s => (s.textContent || '').slice(0, 400));
            // Inspect the iframe's direct parent and grandparent
            const iframe2 = document.querySelector('iframe[title*="guardian_ui"]');
            if (iframe2) {
                const dump = (n) => {
                    if (!n) return null;
                    const cs = getComputedStyle(n);
                    const r = n.getBoundingClientRect();
                    return {
                        tag: n.tagName, testid: n.getAttribute('data-testid'),
                        cls: (n.className || '').slice(0, 80),
                        display: cs.display, padding: cs.padding, margin: cs.margin,
                        height: cs.height, minHeight: cs.minHeight,
                        rect: { y: Math.round(r.top), h: Math.round(r.height) },
                        kids: Array.from(n.children).map(c => ({
                            tag: c.tagName, cls: (c.className||'').slice(0,60),
                            testid: c.getAttribute('data-testid'),
                            cs: { display: getComputedStyle(c).display, height: getComputedStyle(c).height, padding: getComputedStyle(c).padding, margin: getComputedStyle(c).margin, position: getComputedStyle(c).position },
                            rect: (() => { const r = c.getBoundingClientRect(); return { y: Math.round(r.top), h: Math.round(r.height) }; })()
                        }))
                    };
                };
                result.iframeParent = dump(iframe2.parentElement);
                result.iframeGrandparent = dump(iframe2.parentElement?.parentElement);
            }
            const ec = document.querySelector('[data-testid="stElementContainer"]');
            if (ec) {
                const cs = getComputedStyle(ec);
                result.elementContainer = {
                    display: cs.display, padding: cs.padding, margin: cs.margin,
                    minHeight: cs.minHeight, height: cs.height,
                    childCount: ec.children.length,
                    children: Array.from(ec.children).map(c => ({
                        tag: c.tagName, cls: (c.className||'').slice(0,60),
                        rect: (() => { const r = c.getBoundingClientRect(); return { y: Math.round(r.top), h: Math.round(r.height) }; })(),
                        cs: { display: getComputedStyle(c).display, padding: getComputedStyle(c).padding, margin: getComputedStyle(c).margin }
                    }))
                };
            }
            // Computed display of stHeader
            const h = document.querySelector('[data-testid="stHeader"]');
            if (h) {
                const cs = getComputedStyle(h);
                result.stHeaderComputed = { display: cs.display, height: cs.height, position: cs.position };
            }
            // List all iframes
            result.allIframes = Array.from(document.querySelectorAll('iframe'))
                .map(f => ({ title: f.title, src: f.src.slice(0, 100) }));
            return result;
        }"""
    )
    print(json.dumps(info, indent=2, ensure_ascii=False))
    b.close()
