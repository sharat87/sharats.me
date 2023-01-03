---
title: Test your Proxy Support
status: draft
---

Several network configurations, especially in large companies and universities, have a proxy configured for all outgoing traffic. Any network traffic that tries to go out _bypassing_ this proxy, will be blocked. For a self-hosted web application, the server will also need to make all and any outgoing connections via this proxy.

Now, several applications, web application servers included, support the `HTTP_PROXY` and `HTTPS_PROXY` environment variables to configure such a proxy. But if you, as the developer of such a web application, don't have a network that blocks non-proxy traffic, want to test your web app's proxy support, how do you do it? How can we ensure, that when a proxy is configured, all outgoing requests are only ever made through the proxy?

This article is my attempt at answering this.

[TOC]

## Docker Networks

To do this, we'll be using Docker's networking features. It provides a simple set of primitives to solve what we need here.

By default, Docker sets up a Bridge network for us, that allows connectivity to external endpoints. With explicit configuration, we can also have an _internal_ network, where connections are only allowed to other containers that are also connected to this internal network.

You can read more about this in Docker's official documentation about [Networking in Docker Compose](https://docs.docker.com/compose/networking/).

## Sandbox

We need a sandbox environment, where there's a proxy, and a subject application. We want to ensure that outgoing requests made from the subject application, always fail, unless they go via the proxy.

Let's start with two containers, in a `docker-compose.yaml` configuration.

- The `subject` container, which is expected to make all outgoing requests via the proxy only.
- The `proxy` container, which runs an HTTP proxy.

For the `subject` container, we'll use an ordinary, friendly, memorable, vanilla Ubuntu container, with the command set to `sleep infinity`. This makes the container stay running, so that we can get in, and play around. Without this, the container would start, do nothing, and just exit. Not very useful.

For the `proxy` container, we'll use `mitmproxy`, specifically, the web interface version, called `mitmweb`. This is an excellent proxy application, best used for intercepting requests during development. If you haven't been spoilt by it, I encourage you to check it out.

So, this is our initial version of the sandbox:

```yaml
version: "3"

services:
  subject:
    image: ubuntu
    command: sleep infinity

  proxy:
    image: mitmproxy/mitmproxy
    ports: ["8081:8081"]
    command: mitmweb --web-host 0.0.0.0
```

Save this as a `docker-compose.yaml`, and do a `docker-compose up -d`. Once you have the two containers running, open [localhost:8081](http://localhost:8081). This is where we'll see all the HTTP requests flowing through our proxy.

Let's get inside the `subject` container, and make some requests. Start a shell with `docker-compose exec subject bash`. This will drop you in a shell session, running _inside_ the `subject` container. Use the following command to install `curl` to play with:

```bash
apt update && apt install -y curl
```

Now if we try to make an external request, say with `curl httpbun.com/get`, we'll get the response show up in our Terminal, but this request won't show up in mitmproxy's UI. For that, let's do `http_proxy=http://proxy:8080 curl httpbun.com/get`. This will show the response in the Terminal, as well as in mitmproxy's UI.

![Sample request on mitmproxy's UI]({static}/static/mitmproxy-sample.png)

Let's step this up. We'll now block direct Internet access to the `subject` container, and only allow connecting via the proxy. Consider the following `docker-compose.yaml` file:

```yaml
version: "3"


services:
  subject:
    image: ubuntu
    command:
      - sleep
      - infinity
    networks:
      intnet: {}

  proxy:
    image: mitmproxy/mitmproxy
    ports: ["8081:8081"]
    command: mitmweb --web-host 0.0.0.0
    networks:
      intnet: {}
      extnet: {}


networks:
  intnet:
    internal: true
  extnet:
```

This is the same as the previous one, except for `networks` configurations. We define two networks, an internal network, named `intnet`, and an external network, named `extnet`. The `subject` container is only connected to `intnet`, so it can only connect to other containers, that are also connected to `intnet`. The `proxy` container is connected to both `intnet` and `extnet`, so it can both access other containers in the `intnet`, as well as access the wider Internet.

With this setup, we expect direct network connections from `subject` to fail, unless the go via the `proxy` container.

Let's do a `docker-compose up -d` with this file, open a shell with `docker-compose exec subject bash`, and try to install `curl` again. But notice that when we run `apt update`, it doesn't work. Since, even this needs Internet, and we've blocked it. We'll use this as proof that blocking Internet is working!

![Requests from apt in mitmproxy UI]({static}/static/mitmproxy-apt-requests.png)

Instead of `apt update`, issue the command `HTTP_PROXY=http://proxy:8080 apt update`. This should make all requests via that proxy, and should even show up in mitmproxy's UI. Make sure you refresh it once, since the mitmproxy container has been recreated.

After that, we'll do `HTTP_PROXY=http://proxy:8080 apt install -y curl`. Notice that this'll also show a bunch of requests in mitmproxy's UI. Now, we can try out our test with `curl`:

```bash
curl httpbun.com/get
```

This... will eventually timeout. The `subject` container doesn't have access to the Internet, so this can't run. Let's try:

```bash
http_proxy=http://proxy:8080 curl httpbun.com/get
```

Notice that we use `http_proxy` here, instead of `HTTP_PROXY`. Yes, `curl` doesn't like `HTTP_PROXY`. It only accepts `http_proxy`. Yes, it's sad.
{.note}

This should work, and the request should show up in mitmproxy's UI.

## Proxying HTTPS Requests

The setup we have so far works with proxying HTTP requests, but not for HTTPS requests. The whole point of HTTPS, over HTTP, is to make man-in-the-middle interventions impossible in a request. But that's exactly what a proxy does!

To solve this, we'll install and setup mitmproxy's CA into the `subject` container. This will ensure that even if mitmproxy intervenes in HTTPS requests, our `subject` container will gladly accept and mark such requests as verified. This is documented on [mitmproxy's documentation](https://docs.mitmproxy.org/stable/concepts-certificates/).

The first time mitmproxy starts, it generates a new random CA certificate. This is the certificate is what we want our `subject` container to trust. So we'll use a Docker volume, to share this cert with the `subject` container.

```yaml hl_lines=12,13,22,23,32,33
version: "3"


services:
  subject:
    image: ubuntu
    command:
      - sleep
      - infinity
    networks:
      intnet: {}
    volumes:
      - certs:/certs:ro

  proxy:
    image: mitmproxy/mitmproxy
    ports: ["8081:8081"]
    command: mitmweb --web-host 0.0.0.0
    networks:
      intnet: {}
      extnet: {}
    volumes:
      - certs:/home/mitmproxy/.mitmproxy


networks:
  intnet:
    internal: true
  extnet:


volumes:
  certs:
```

Here, we define a volume, named `certs`, that'll hold the contents of the `/home/mitmproxy/.mitmproxy` folder, inside the `proxy` containe. This is the path where mitmproxy will save the generated CA root certificate.

We also give the `subject` container access to this volume, at the `/certs` location inside the `container`. Notice the `:ro` suffix here, which means read-only access. We don't expect the `subject` container to write anything to this volume, just read the certificate.

Let's start the containers again with a `docker-compose up -d`, and then run our tests again:

```bash
HTTP_PROXY=http://proxy:8080 apt update
HTTP_PROXY=http://proxy:8080 apt install -y curl
http_proxy=http://proxy:8080 curl httpbun.com/get
https_proxy=http://proxy:8080 curl https://httpbun.com/get
```

The HTTPS request from this last command, should show up as an HTTPS request in mitmproxy, with the ability to view full details of the request and response. Try out the same/similar `curl` commands _without_ the proxy, and notice that those requests fail.

## Conclusion

Since requests directly to the Internet fail, we can use this setup to test if our application doesn't leak any requests, when a proxy is configured. Ideally, when I configure a proxy to be used by an application, I don't expect it to make _any_ request without that proxy.

To do that, we'd replace the `subject` container, to the application we want to test, instead of a vanilla Ubuntu container.
