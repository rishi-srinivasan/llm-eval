#!/usr/bin/env python3
"""TTFT + tokens per task prompt against an Ollama OpenAI-compatible endpoint (stdlib only).
  ttft.py [--model glm-5.3-flash:cloud] [--host http://localhost:11434] [--reps 3] [--max-tokens 512]
Run inside the eval container with --host http://host.docker.internal:11434 to include Docker overhead.
"""
import argparse, glob, json, statistics as st, time, urllib.request

def one(host, model, prompt, max_tokens):
    body = json.dumps(dict(model=model, stream=True, max_tokens=max_tokens, stream_options={"include_usage": True},
                           messages=[{"role": "user", "content": prompt}])).encode()
    req = urllib.request.Request(f"{host}/v1/chat/completions", body, {"Content-Type": "application/json"})
    t0, first, first_content, usage = time.time(), None, None, {}
    with urllib.request.urlopen(req, timeout=600) as r:
        for raw in r:
            line = raw.decode().strip()
            if not line.startswith("data: ") or line == "data: [DONE]":
                continue
            c = json.loads(line[6:])
            if c.get("usage"):
                usage = c["usage"]
            d = (c.get("choices") or [{}])[0].get("delta", {})
            if first is None and (d.get("content") or d.get("reasoning") or d.get("reasoning_content")):
                first = time.time() - t0  # first token of any kind (thinking counts)
            if first_content is None and d.get("content"):
                first_content = time.time() - t0
    return dict(ttft=first, ttft_content=first_content, total=time.time() - t0,
                prompt_tokens=usage.get("prompt_tokens"), completion_tokens=usage.get("completion_tokens"))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="glm-5.3-flash:cloud"); p.add_argument("--host", default="http://localhost:11434")
    p.add_argument("--reps", type=int, default=3); p.add_argument("--max-tokens", type=int, default=512)
    a = p.parse_args()
    one(a.host, a.model, "hi", 8)  # warm-up: connection/model load excluded
    print("task      ttft_s  ttft_content_s  prompt_tok  completion_tok  total_s")
    for f in sorted(glob.glob("tasks/*/prompt.md")):
        rs = [one(a.host, a.model, open(f).read(), a.max_tokens) for _ in range(a.reps)]
        m = lambda k: st.median([r[k] for r in rs if r[k] is not None] or [float("nan")])
        print(f"{f.split('/')[-2]:8}  {m('ttft'):6.2f}  {m('ttft_content'):14.2f}  {m('prompt_tokens'):10.0f}  {m('completion_tokens'):14.0f}  {m('total'):7.2f}")
