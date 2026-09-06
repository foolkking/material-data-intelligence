import http from "node:http";

const target = new URL(process.env.MDI_FRONTEND_ALIAS_TARGET || "http://127.0.0.1:3013");
const port = Number(process.env.MDI_FRONTEND_ALIAS_PORT || 3000);

const server = http.createServer((req, res) => {
  const upstream = http.request(
    {
      hostname: target.hostname,
      port: target.port,
      method: req.method,
      path: req.url,
      headers: {
        ...req.headers,
        host: target.host,
      },
    },
    (upstreamResponse) => {
      res.writeHead(upstreamResponse.statusCode || 502, upstreamResponse.headers);
      upstreamResponse.pipe(res);
    },
  );
  upstream.on("error", (error) => {
    if (!res.headersSent) {
      res.writeHead(502, { "content-type": "text/plain; charset=utf-8" });
    }
    res.end(`Frontend alias unavailable: ${error.message}`);
  });
  req.pipe(upstream);
});

server.listen(port, "127.0.0.1", () => {
  console.log(`phase14r frontend alias listening on http://127.0.0.1:${port} -> ${target.origin}`);
});
