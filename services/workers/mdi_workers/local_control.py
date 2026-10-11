"""Project-local readiness and graceful draining; never executes application work."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
import socket

from redis import Redis
from redis.backoff import NoBackoff
from redis.retry import Retry
from rq import Queue
from rq.exceptions import StopRequested


class LocalControlMixin:
    @property
    def dequeue_timeout(self) -> int:
        return 1


def local_control_queue(worker_name: str) -> type[Queue]:
    class DrainAwareQueue(Queue):
        @classmethod
        def dequeue_any(cls, queues, timeout, connection, **kwargs):
            # Checked only at a dequeue boundary. A running job completes
            # normally, including its result publication, before teardown.
            requested = connection.hget(f"rq:worker:{worker_name}", "mdi_drain")
            if requested == str(os.getpid()).encode():
                raise StopRequested()
            return super().dequeue_any(queues, timeout, connection, **kwargs)
    return DrainAwareQueue


def inspect_worker(connection: Redis, name: str, pids: list[int], queues: list[str], started_after: datetime) -> dict:
    row = connection.hgetall(f"rq:worker:{name}")
    if not row or row.get(b"death"):
        return {"ready": False, "reason": "not_registered"}
    try:
        pid = int(row[b"pid"])
        birth = datetime.fromisoformat(row[b"birth"].decode().replace("Z", "+00:00"))
        heartbeat = datetime.fromisoformat(row[b"last_heartbeat"].decode().replace("Z", "+00:00"))
        state = row[b"state"].decode()
        owned = pid in pids and row.get(b"hostname", b"").decode() == socket.gethostname()
        owned = owned and birth >= started_after and row.get(b"queues", b"").decode().split(",") == queues
    except (KeyError, ValueError):
        return {"ready": False, "reason": "invalid_registration"}
    if not owned:
        return {"ready": False, "reason": "identity_mismatch"}
    age = (datetime.now(timezone.utc) - heartbeat).total_seconds()
    # RQ extends its lease for long running jobs; legacy idle workers also
    # block longer than 90 seconds. Honor that lease instead of inventing a
    # shorter heartbeat timeout that marks valid work as unavailable.
    if state not in {"idle", "busy"} or age < -5 or connection.ttl(f"rq:worker:{name}") <= 0:
        return {"ready": False, "reason": "not_ready"}
    return {"ready": True, "pid": pid, "birth": row[b"birth"].decode(), "state": state,
            "draining": row.get(b"mdi_drain") == str(pid).encode()}


def set_drain(connection: Redis, name: str, identity: dict, enabled: bool) -> bool:
    """Change only the registration just verified by the process controller."""
    key = f"rq:worker:{name}"
    with connection.pipeline() as transaction:
        transaction.watch(key)
        row = transaction.hgetall(key)
        if (row.get(b"pid") != str(identity["pid"]).encode()
                or row.get(b"birth") != identity["birth"].encode() or row.get(b"death")):
            return False
        transaction.multi()
        if enabled:
            transaction.hset(key, "mdi_drain", str(identity["pid"]))
        else:
            transaction.hdel(key, "mdi_drain")
        transaction.execute()
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("probe", "drain", "resume"))
    parser.add_argument("--name", required=True)
    parser.add_argument("--pids", type=int, nargs="+", required=True)
    parser.add_argument("--queues", nargs="+", required=True)
    parser.add_argument("--started-after", required=True)
    args = parser.parse_args()
    connection = Redis.from_url(os.environ.get("REDIS_URL") or os.environ["MDI_REDIS_URL"],
        socket_connect_timeout=2, socket_timeout=2, retry=Retry(NoBackoff(), 0))
    try:
        since = datetime.fromisoformat(args.started_after.replace("Z", "+00:00"))
        result = inspect_worker(connection, args.name, args.pids, args.queues, since)
        if args.action != "probe":
            if not result["ready"] or not set_drain(connection, args.name, result, args.action == "drain"):
                print(json.dumps({"ready": False, "reason": "identity_changed"}))
                return 1
        print(json.dumps(result))
        return 0
    except Exception:
        # Connection strings and credentials must not enter controller output.
        print(json.dumps({"ready": False, "reason": "control_unavailable"}))
        return 1
    finally:
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
