---
title: Peeking into HTTPS Traffic with a Proxy
tags: proxy, docker, mitmproxy, https, curl, appsmith
---

This article is about configuring a web application, Appsmith in this case, to run correctly behind a firewall that does SSL decryption, as a Docker container. Instead of a firewall, we'll use a proxy, which, for the purpose of the problem statement, should be the same.

[TOC]

Since the proxy needs to support HTTPS decryption, we'll use `mitmproxy`, but Charles or any other proxy that supports this would also work just fine.

## Setting up `mitmproxy`

Install with:

```sh
brew install mitmproxy
```

Now launch it using:

```bash
mitmweb --listen 9020 --web 9021
```

Let it run in a separate Terminal window in the background. This will also open the proxy's web UI at <http://localhost:9021>. To get a console UI instead, use `mitmproxy` instead of `mitmweb` in the above command.

Let's try running some requests through this proxy to see it's working well. Start with:

```sh
curl http://httpbun.com/get
```

This should print a valid JSON as the response, with some details about the request itself. Let's repeat this with the proxy.

```sh
curl --proxy localhost:9020 http://httpbun.com/get
```

You should again see the same response here, but this time, a new entry should appear in the `mitmweb` UI. Here, you can inspect the request and be able to see the path, headers and response of the request.

So we've confirmed that our proxy works. Let's add HTTPS to the mix.

```sh
curl https://httpbun.com/get
```

Again, same thing, but with HTTPS, without a proxy. You should see the same response as before, but without an entry in the proxy. That's to be expected since we didn't put a `--proxy` here. Let's try that now.

```sh
curl --proxy localhost:9020 https://httpbun.com/get
```

This one, should also succeed, unless you've installed `mitmproxy` via a different method. Let's see why.

The way an SSL proxy works is by establishing two SSL connections, one with the client (a browser, or `curl`), initiated by the client, and another with the server (the `httpbun.com` server in this case). Everything sent by the client is encrypted using the certificate of `mitmproxy`, and everything by and to the server is encrypted with the server's certificate.

When installing `mitmproxy` via `brew`, the root certificate was automatically installed on your system, and so `curl` won't complain about the certificate being unverified.

To illustrate this, we can run the same thing in a container, and we should see the error right away:

```sh
docker run --rm alpine/curl --proxy host.docker.internal:9020 https://httpbun.com/get
```

At this, you should see a certificate validation error. This is because the root certificate of `mitmproxy` isn't installed inside the container's environment, and so the `curl` invocation inside, won't be able to verify `mitmproxy`'s certificate.

To confirm that this is indeed because of `mitmproxy`, run the same `docker run` command without the `--proxy host.docker.internal` and you won't see this error, despite running with `https`.

Now we've reproduced the situation where a process (a web server in our case), inside a Docker container, is trying to run behind an SSL-decrypting firewall (or, an SSL-decrypting proxy in our case here). Let's see what we can do to get this to work.



## Setting up

For our adventure here, we'll use the Docker image of Appsmith, located at <https://hub.docker.com/repository/docker/appsmith/appsmith-ce>.

Let's start a _temporary_ Appsmith container with:

```sh
docker run --rm -d --name ace -p 80:9022 appsmith/appsmith-ce
```

Once this is ready, you should be able to access your Appsmith instance at <http://localhost:9022>.

Let's try to run some `curl` requests inside this container, and get them to go through our `mitmweb` proxy.

```sh
docker exec ace curl --proxy host.docker.internal:9020 http://httpbun.com/get
```

This should work fine, and the request should show up in the proxy UI with full details as well. Now let's do the same thing with `https`.

```sh
docker exec ace curl --proxy host.docker.internal:9020 https://httpbun.com/get
```

Let's copy the root certificate into the container. For `mitmproxy`, the root cert is generated at first start, and is located at `~/.mitmproxy/mitmproxy-ca-cert.pem`, going by the docs at <https://docs.mitmproxy.org/stable/concepts-certificates/#the-mitmproxy-certificate-authority>.

```sh
docker cp ~/.mitmproxy/mitmproxy-ca-cert.pem ace:/
```

With this command, we are copying the root certificate of `mitmproxy` into the container, into the root folder. Let's run the same `curl` command now, providing it this root cert:

```sh
docker exec ace curl --proxy host.docker.internal:9020 --cacert /mitmproxy-ca-cert.pem https://httpbun.com/get
```

Now we'll see the correct response, as well as full details of this request in the proxy UI.


## Setting proxy on the whole container

We're now at the point where it's possible for requests inside the container to be run via the proxy, without any cert validation errors.

But this currently needs to be deliberate. Like in the example above, the `curl` command needs the cert to be specified explicitly. Instead, we'd like even ordinary `curl` commands to always go through the proxy, since, that's how a firewall would work, and ultimately, that's what we are trying to reproduce here.

Let's stop the `ace` container and start it again with proxy configuration set.

```sh
docker stop ace
docker run --rm -d --name ace -p 80:9022 \
	-e HTTP_PROXY=http://host.docker.internal:9020 \
	-e HTTPS_PROXY=http://host.docker.internal:9020 \
	-e http_proxy=http://host.docker.internal:9020 \
	-e https_proxy=http://host.docker.internal:9020 \
	appsmith/appsmith-ce
```

Yep, that's right. We need to set both `http_proxy` _and_ `HTTP_PROXY` for all applications inside the container to take it seriously. 🤦

Let's run a normal `curl` request on this container to see if the proxy settings are applied:

```sh
docker run ace curl http://httpbun.com/get
```

If the proxy configuration is working, then you should see this request appear in the proxy UI. Also, for `https` URLs:

```sh
docker run ace curl https://httpbun.com/get
```

This, as we can expect, fails due to a cert validation error, since it's using the proxy, but the proxy's certificate can't be verified. We can provide the root cert of `mitmproxy` using the `--cacert` argument, but we want it to apply to all requests in the container, without such explicit configuration, so we won't do that.

Instead, we want to _install_ the root certificate of `mitmproxy` to the _truststore_, so that it's available to _all_ processes in the container for validating SSL certificates.

How this is done, depends on the operating system, but in our case, since the container is Ubuntu, all we need to do is:

- Copy the certificate file to `/usr/local/share/ca-certificates`.
- If the cert has the `.pem` extension, rename it to use the `.crt` extension. This is because Ubuntu's `update-ca-certificates` command only picks files with a `.crt` extension.
- Run `update-ca-certificates`.

Let's copy the root cert into the container, and install it by running the above commands inside the container:

```sh
docker cp ~/.mitmproxy/mitmproxy-ca-cert.pem ace:/usr/local/share/ca-certificates/mitmproxy-ca-cert.crt
docker exec ace update-ca-certificates
```

The output should say that one certificate has been added to the truststore.

Let's run the same `https` request again:

```sh
docker exec ace curl https://httpbun.com/get
```

This should now print the correct response, as well as show up on the proxy UI with full details for inspection. 🎉

## Conclusion

This has culminated in creating the PR [#14207](https://github.com/appsmithorg/appsmith/pull/14207/files). This PR contains a fer QoL improvements over the solution above.

1. We install `ca-certificates-java`, so that when we run `update-ca-certificates`, they are also installed into the JVM truststore. This is important since, one, Java maintains its own truststore (like Firefox), and two, Appsmith's server runs on the JVM, so we need this there as well.

2. We provide support for a `ca-certs` folder in the volume, where users can drop any root cert files which will be auto-added on container startup.

3. We run `update-ca-certificates --fresh` instead of just `update-ca-certificates`, so that any cert file _removed_ from the `ca-certs` folder, also gets removed from the truststores.

4. We mix up values of the proxy env variables, so that setting just one of `http_proxy` and `HTTP_PROXY` would be enough. This is also done for `https_proxy` and `HTTPS_PROXY`.

5. We provide a friendly warning when there's `.pem` files in the `ca-certs` folder, since, most likely, they are there because the user forgot to rename them to use the `.crt` extension.

6. The JVM needs the `-Djava.net.useSystemProxies=true` to use the system configured proxy. Additionally, we also set the individual proxy configuration as additional system properties, so we can apply them when executing requests via Apaches' web client libraries. Since, well, that library doesn't respect system proxy configuration, although the rest of JVM does. Go figure.

7. We set a `NO_PROXY` env variable to hosts that should _not_ go through the proxy, like `localhost` and `127.0.0.1`.

Of course, considering our premise, which is to be able to use Appsmith behind an SSL decrypting proxy, all a user needs to do, is to place the firewall's root certificate in the `ca-certs` folder, and restart the Appsmith container.

## Bonus: Using Charles

Notes on using Charles instead of `mitmproxy`.

Install with:

```sh
brew install charles
```

Open Charles

Go to `Proxy -> SSL Proxying Settings`, under "SSL Proxying", add a few domains you want SSL decryption to be done. Let's add an entry under "Include", with host set to `httpbun.com` and port set to `443` (which is the default port of HTTPS).

Check with http curl, response should show up correctly, and the request should show up in Charles with full information.

Check with https curl, get an error response back, and the request should show up in Charles with incomplete information, and a red error icon.

To get the Charles' root certificate, go to `Help -> SSL Proxying -> Save Charles Root Certificate...`. Provide a location to save this cert, like your home folder.

The other steps should be the same as explained above for `mitmproxy`.
