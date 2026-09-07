"""Transport-neutral application layer for Material Data Intelligence.

Application modules own use-case and policy logic that must be callable from
any transport (HTTP router, queue worker, or another application service).
They must not import FastAPI, router modules, router-private helpers, or
compatibility facades.
"""
