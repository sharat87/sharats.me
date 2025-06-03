---
title: Use a proxy for LLM app development
description: Frameworks like LangChain make it easy to use LLMs&mdash;but they hide the real HTTP requests. Using a local proxy (like mitmproxy) lets you inspect and debug exactly what's going on, down to the headers and raw payloads.
---

Most everybody is developing LLM applications these days. New frameworks and libraries show up nearly every week. A common theme is easy switching between LLM providers with minimal code changes.

That sounds great, and it is.

But, as with all abstractions that make it dead simple to start, they also make debugging and maintenance that much harder.

I'm constantly asking myself: *Under all those library calls, what actual API request was made? What payload was sent? What did the server return? What were the headers?* Having access to this info makes debugging and discovery **so much easier**. Once you see it, there's no going back.

Example video:

Video: mitmproxy-llm-apis.mp4

All code for this article is in [this GitHub repo](https://github.com/sharat87/mitmproxy-for-llm-apps). Follow along!

[TOC]

## Setup a local proxy

The best way to observe LLM traffic during development is through a **local forward proxy**. I've used mitmproxy, Proxyman, HTTP Toolkit, and Charles. Here we'll use mitmproxy, though I've recently moved to Proxyman. Most setup steps are similar.

## How mitmproxy works (quick primer)

Mitmproxy acts as a **forward proxy** between your local app and the real server.

When your code makes a request to `example.com`, it instead sends it to mitmproxy, which then forwards it to the actual server and relays the response back. Like the name suggests, it's a <u>m</u>an <u>i</u>n <u>t</u>he <u>m</u>iddle. Or, as I like to call it, <u>m</u>achine <u>i</u>n <u>t</u>he <u>m</u>iddle.

### What about HTTPS?

That's where it gets tricky. HTTPS uses TLS certificates, and mitmproxy doesn't have the real cert for `example.com`. This causes a TLS handshake failure unless you trust mitmproxy's generated **custom CA certificate**.

By trusting that CA, your app accepts mitmproxy's certificate for any domain it intercepts and so we don't see any browser warnings or connection errors about failed TLS handshakes.

## Install and run mitmproxy locally

Clone the repo (or start from scratch if you prefer):

```bash
git clone https://github.com/sharat87/mitmproxy-for-llm-apps
cd mitmproxy-for-llm-apps
uv sync
make mitm
```

This runs mitmproxy on port 9020 and starts the web UI on port 9021. It may open in your browser. Open the `Makefile` to inspect what it does, don't just run scripts from random repos... like, who does that? (Looks out the window)

## Test with a simple HTTP request

Try this to verify everything is working:

```bash
curl -x http://localhost:9020 httpbun.com/any
```

You should see this request show up in the mitmproxy UI, along with full request/response headers and bodies.

## Trust mitmproxy's CA cert for HTTPS support

Now try an HTTPS URL:

```bash
curl -x https://localhost:9020 https://httpbun.com/any
```

💥 **Expected** TLS verification failure.

Fix it by telling `curl` to use mitmproxy's CA cert (located at `~/.mitmproxy/mitmproxy-ca-cert.pem`):

```bash
curl -x https://localhost:9020 --cacert ~/.mitmproxy/mitmproxy-ca-cert.pem https://httpbun.com/any
```

Now HTTPS traffic works and shows up in mitmproxy.

## Use mitmproxy with Python requests

Here's how to set up Python code to route traffic through the proxy.

### With `http://`:

```python filename=experiment.py
import sys
import httpx

url = sys.argv[1]

client = httpx.Client(proxy="http://localhost:9020")
response = client.get(url)

print(response)
print(response.text)
```

Run it:

```bash
uv run python experiment.py http://httpbun.com/any
```

This will show up normally in mitmproxy.

### With `https://`: 

💥 Will fail with a certificate verification error.

Let's make Python trust mitmproxy's CA by injecting it into `certifi`'s trusted certificates file, which `httpx` uses:

```python filename=experiment.py
from pathlib import Path
import sys

import certifi
import httpx

# Save the original certifi file
certifi_orig_path = Path(certifi.where() + ".original")
if not certifi_orig_path.exists():
    certifi_orig_path.write_text(Path(certifi.where()).read_text())

# Add mitmproxy's CA cert to the certifi bundle
Path(certifi.where()).write_text(
    certifi_orig_path.read_text()
    + "\n\n# mitmproxy-ca-cert.pem\n"
    + (Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.pem").read_text()
)

url = sys.argv[1]

client = httpx.Client(proxy="http://localhost:9020")
response = client.get(url)
print(response)
print(response.text)
```

Now HTTPS requests work and appear in mitmproxy.

## Monitor OpenAI SDK calls via mitmproxy

Let's now observe a real LLM call using the OpenAI SDK:

```python filename=experiment.py
import openai

client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "I'm a little teapot!"}],
)

print(response.choices[0].message.content)
```

We're using OpenAI's SDK, which, under all the abstractions, uses `httpx` to make the HTTP requests. But that means we don't have control on the creation of the `httpx.Client` object, so we can't inject the proxy there. Thankfully, [`httpx` respects the "standard" proxy environment variables](https://www.python-httpx.org/environment_variables/#proxies). So we run the script like this:

```bash
HTTPS_PROXY=http://127.0.0.1:9020 OPENAI_API_KEY=sk-proj-... uv run python experiment.py
```

You'll now see the full OpenAI API request and response payloads in mitmproxy.

## Compare different API styles

Try switching from completions to the new responses API:

```python
response = client.responses.create(
    model="gpt-4o-mini",
    input="I'm a little teapot!",
)

print(response.output_text)
```

Run this and you should see how different the JSON body is structured between the two APIs. If you enable streaming in those API calls, you'll see the individual SSE events in the Response tab in mitmproxy.

## Inspect LangChain calls

LangChain uses OpenAI under the hood:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
response = llm.invoke("Hello there matey!")

print(response.content)
```

All calls show up in mitmproxy showing the exact API calls under all the LangChain abstractions. This is great for understanding how higher-level tools serialize prompts and responses.

## Use mitmproxy scripting to highlight LLM conversations

Mitmproxy supports scripting addons.

Here's a [script](https://github.com/sharat87/mitmproxy-for-llm-apps/blob/main/llm_commenter.py) that extracts the current LLM "conversation" and shows it in the *Comment* tab for OpenAI completions calls.

Start mitmproxy like this:

```bash
mitmweb --scripts llm_commenter.py
```

Note: it's experimental, and the Comment tab support is new, but still better than manually parsing JSON.

## Inspect tool calls in LangChain

> Code from prompt:
> Write a minimal python script to call LangChain with OpenAI, with a single tool to add two numbers, and prompt OpenAI to add 20 to the answer to life, universe, and everything else.

We have the resulting code [here](https://github.com/sharat87/mitmproxy-for-llm-apps/blob/a8721301e2431062979bcbfcc3565c536697c3ef/main.py#L59). Run it with the proxy enabled and you'll see two OpenAI calls:

- First: receives the tool call
- Second: sends tool execution result and gets final response

Seeing this logic play out makes complex LangChain chains far easier to understand.

## Handle dynamic CA certs (e.g., EKS Kubernetes API)

Some services (like EKS) use their own custom CA certs.

Example: [this function](https://github.com/sharat87/mitmproxy-for-llm-apps/blob/a8721301e2431062979bcbfcc3565c536697c3ef/main.py#L110) connects to Kubernetes and requires trusting the EKS CA.

You'll need to:

1. Add the CA to your app's `certifi` trust store
2. Also add it to **mitmproxy's** trust store (if in a separate venv)
3. Clear mitmproxy's SSL cache

To clear the cache, use [`ssl.clear`](https://github.com/sharat87/mitmproxy-for-llm-apps/blob/main/mitmproxy_ssl_clear.py), a custom mitmproxy addon.

Now mitmproxy shows all AWS and Kubernetes traffic. This is now ready to be wired as a tool for LLMs.

## Run mitmproxy in a Dockerized webapp

We created a small Flask webapp (`server.py`) that prompts for user input and calls an LLM:

```bash
make serve
```

View it at [localhost:9022](http://localhost:9022). LLM traffic will appear in mitmproxy at [localhost:9021](http://localhost:9021).

Check out the [`Dockerfile`](https://github.com/sharat87/mitmproxy-for-llm-apps/blob/main/Dockerfile) and [`entrypoint.sh`](https://github.com/sharat87/mitmproxy-for-llm-apps/blob/main/entrypoint.sh) for how mitmproxy is booted inside the container.

Build and run:

```bash
docker build -t mapp . && {
    docker rm -f mapp
    docker run --name mapp -d -p 5021:9021 -p 5022:9022 -e MITM_PASSWORD= -e OPENAI_API_KEY= mapp
}
```

> ⚠️ **Warning:** Definitely don't run this in production. Like, please _please_ don't.

## Conclusion

Abstractions aren't magic, they're just a facade. Looking behind the curtain can give powerful understanding of the various LLM APIs and frameworks.

_Every_ LLM app developer should have a local dev proxy in their toolkit.
