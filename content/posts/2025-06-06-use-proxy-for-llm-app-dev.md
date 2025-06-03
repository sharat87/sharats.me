---
title: Use a proxy for LLM app development
description: LLM app frameworks make it easy to integrate models—but hide critical details. This article shows you how to use a local proxy to see what's really happening.
---

Most everybody is developing LLM applications these days. There's tons of frameworks and libraries with new ones showing up almost every day. These libraries promise a lot, with a very common theme being that we can switch LLM API provider and the LLM itself with minimal code changes. That we can support new models and providers _much_ faster.

That sounds great, and it is.

But, as with all abstractions that make things dead simple to get started with, they make maintenance and debugging that much harder.

I'm constantly asking, under all those library function calls and abstractions, what is the API call that was eventually made? What was the exact JSON payload that was sent? What was the exact response? What were the headers? This information can make it _oh so much easier_ to debug and optimize. Once you see it in action, there's no going back.

All code for this article is in [this GitHub repo](https://github.com/sharat87/mitmproxy-for-llm-apps). Follow along!

[TOC]

## Setup a local proxy

The best way is to use a local forward proxy for development. There's lots of options today, I've personally used mitmproxy, Proxyman, HTTP Toolkit, and Charles. We'll go with mitmproxy here, but I've almost completely moved to Proxyman now. Most instructions remain the same.

## How does this work?

If you know how these proxies operate, skip this part.

Mitmproxy is a forward proxy for use as a local proxy for development. With the right configuration, it can intercept both HTTP and HTTPS traffic.

When you make an API request to a `example.com`, Python will send that request to the forward proxy. The proxy will then forward the request to the website's server. The proxy then gets the response back, and forwards it back to you. It's quite literally, "<u>m</u>an <u>i</u>n <u>t</u>he <u>m</u>iddle", or as I like to call it, "<u>m</u>achine <u>i</u>n <u>t</u>he <u>m</u>iddle"!

But way of working presents a problem for HTTPS. The server that our code is contacting now isn't `example.com`'s server, it's the proxy. That proxy won't have a valid cert for `example.com`, so the TLS handshake will fail.

To get around this, mitmproxy generates a CA certificate that we can tell our code to trust. That way, the connection between our code and the proxy is verified HTTPS, and the connection between proxy and the final server is also verified HTTPS.

## Setting up a project with mitmproxy

You may choose to start from a blank folder, but we're going to clone the repo for this article and work with that here.

```bash
git clone https://github.com/sharat87/mitmproxy-for-llm-apps
cd mitmproxy-for-llm-apps
uv sync
make mitm
```

This will start the proxy on port 9020 and the web interface on port 9021. The UI should open up in your browser now. Feel free to also open this folder in your IDE/Editor and check things out. Like start with the `Makefile`. I'm basically asking you to clone a random repo and run `make`. DO check the `Makefile` out.

Let's see if things are working fine.

```bash
curl -x http://localhost:9020 httpbun.com/any
```

This request should show up in the mitmproxy UI. Check it out, look around, inspect the request, response, their headers, etc. This is the kind of detail we'll get for all APIs made to LLM providers.

## mitmproxy's CA cert

If we try the above `curl` command with `https`, we'll see a TLS cert verification error.

```bash
curl -x https://localhost:9020 https://httpbun.com/any
```

The CA cert is saved in `~/.mitmproxy/mitmproxy-ca-cert.pem`. If we give this to the above `curl` command, it'll work.

```bash
curl -x https://localhost:9020 --cacert ~/.mitmproxy/mitmproxy-ca-cert.pem https://httpbun.com/any
```

Now this request should show up in the mitmproxy UI, with full details, despite it being a valid and verified HTTPS request.

## Use mitmproxy with requests from Python code

Let's do that in Python code now. This is illustrative, this code is already in `main.py`. Feel free to paste this to a separate `experiment.py` and run it with `uv run python experiment.py`.

```python filename=experiment.py
import sys
import httpx

url = sys.argv[1]

client = httpx.Client(proxy="http://localhost:9020")
response = client.get(url)

print(response)
print(response.text)
```

Run it with a `http://` URL:

```bash
uv run python experiment.py http://httpbun.com/any
```

This will show up in mitmproxy. Now let's do `https://`.

```bash
uv run python experiment.py https://httpbun.com/any
```

As we've seen before, this will throw a TLS verification error.

```
httpx.ConnectError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1028)
```

## Getting HTTPS requests into mitmproxy

We have proxy working with `http` URLs, isn't that enough? ~~Unfortunately~~ Fortunately, most all API services today are using HTTPS. If we want to intercept API calls to LLM providers, we have to have HTTPS support with the proxy.

Most HTTP libraries (all?) in Python don't use the system CA trust store. So, while installing the mitmproxy's CA cert into your system is a good idea, it won't help our cause. Instead, we need to add it to the `certifi` bundle.

The `certifi` package's CA trust store contains a list of CA certificates, just like most operating systems and some browsers do. There's pros/cons to doing it this way instead of just using the system trust store, and I have my opinions, but that's a ~~topic~~ rant for another day.

In our Python application, just before we start making any HTTPS requests, we'll add the mitmproxy's CA cert to the `certifi` trust store. Our `main.py` will be:

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

Running it with an `https://` URL now:

```bash
uv run python experiment.py https://httpbun.com/any
```

Should work now.

## Monitor OpenAI SDK calls

Let's use OpenAI's official SDK to make an LLM call.

In our `experiment.py`, instead of the direct call to httpx, let's do this:

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

Running this, you should see a request to OpenAI in mitmproxy, with the full request body JSON and the response body JSON.

To potentially illustrate the value, let's change the code to use OpenAI's new responses API as well:

```python
response = client.responses.create(
    model="gpt-4o-mini",
    input="I'm a little teapot!",
)

print(response.output_text)
```

Run this and you should see how different the JSON body is structured between the two APIs. If you enable streaming in those API calls, you'll see the individual SSE events in the Response tab in mitmproxy.

Same thing with LangChain:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
response = llm.invoke("Hello there matey!")

print(response.content)
```

## Scripting in mitmproxy

Mitmproxy is very scriptable. That sounds like it's an advanced useless feature, but it's great when working with LLM APIs.

[Here's a script](https://github.com/sharat87/mitmproxy-for-llm-apps/blob/main/llm_commenter.py) that'll show the "conversation" in the current API, under the "Comment" tab.

When mitmproxy (or mitmweb) is run with `--script llm_conversation.py`, we'll see the conversation in the Comment tab of any OpenAI completions API call.

Note that this doesn't work _very_ well just yet, because the "Comment" tab is a relatively new feature. But it's still better than deciphering the conversation from the JSON body. Especially with streaming responses.

## Monitor LangChain's tool call conversation

Let's put up a Python script that uses LangChain to get an LLM to call a tool.

> Code from prompt:
> Write a minimal python script to call LangChain with OpenAI, with a single tool to add two numbers, and prompt OpenAI to add 20 to the answer to life, universe, and everything else.

[We've added that generated code to our `main.py`](https://github.com/sharat87/mitmproxy-for-llm-apps/blob/a8721301e2431062979bcbfcc3565c536697c3ef/main.py#L59). Now running it with the proxy env variables, we should see two new calls to OpenAI completions API.

You should be able to see how LangChain sent the tool information to OpenAI, how OpenAI responded with a request to call the tool function, and how LangChain made another call to OpenAI with both the original request to call the tool, as well as the function call result.

As the abstractions grow, when complexity grows, such visibility is absolutely invaluable.

## Handling Dynamic CA Certificates

Here's another case. We want to equip the LLM with a tool to list pods in the default namespace in an EKS cluster.

Look at the [`kubernetes_list_pods` function in `main.py`](https://github.com/sharat87/mitmproxy-for-llm-apps/blob/a8721301e2431062979bcbfcc3565c536697c3ef/main.py#L110) for an example.

Connecting to EKS gets us a new CA cert that we'll be using to talk to the Kubernetes API. But now we need to add this new CA to the `certifi` bundle, that's used both by our application, as well as by mitmproxy. So note, if your mitmproxy is installed in a separate venv, you have to add the CA to the `certifi` bundle in that venv as well.

After that, we need to get mitmproxy to clear it's SSL cache. Yes, it caches. Permanently. Understandably.

The `ssl.clear` command is a custom command, isn't shipped with mitmproxy. It's defined as [a mitmproxy addon in this file](https://github.com/sharat87/mitmproxy-for-llm-apps/blob/main/mitmproxy_ssl_clear.py).

Now running the script shows all interactions with AWS and Kubernetes APIs in mitmproxy UI. This is now ready to be wired up into a tool call for an LLM.

## Fitting mitmproxy into a webapp's Docker container

Let's put up a small Flask webapp that has a form to take a prompt from a user, and shows an LLM response on form submission.

This is in [the `server.py` file](https://github.com/sharat87/mitmproxy-for-llm-apps/blob/main/server.py), and run it with `make serve`. Open [localhost:9022](http://localhost:9022) to see this groundbreaking LLM powered app.

The server of course, is run with the proxy env variables. So when we enter a prompt in the UI and hit submit, we see the LLM call in mitmproxy UI.

Now consider the [Dockerfile](https://github.com/sharat87/mitmproxy-for-llm-apps/blob/main/Dockerfile) for our webapp. There's nothing special here. We load the app into the Docker image, install dependencies and mitmproxy. Setup [an `entrypoint.sh`](https://github.com/sharat87/mitmproxy-for-llm-apps/blob/main/entrypoint.sh) that'll start mitmweb in the background, and run the server.

Run it like this:

```bash
docker build -t mapp . && {
    docker rm -f mapp
    docker run --name mapp -d -p 5021:9021 -p 5022:9022 -e MITM_PASSWORD= -e OPENAI_API_KEY= mapp
}
```

Fill in some password and the OpenAI API key, and open [localhost:5022](http://localhost:5022) to see the app running in the Docker container.

The mitmproxy web UI should be available at [localhost:5021](http://localhost:5021).

Submitting a prompt in the app should show the LLM call in mitmproxy UI.

Of course, goes without saying, um, DO NOT DO THIS IN PRODUCTION. Like, please don't. I'm of half a mind to not include this section here. 🤔

## Conclusion

Abstractions aren't magic&mdash;so long as we understand what's going on underneath.

_Every_ web developer needs a dev proxy. _Especially_ if you're working with LLM provider APIs.
