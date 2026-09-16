"""Provider-aware, exact-byte MinIO recovery for the acceptance scope.

This maintenance utility never updates PostgreSQL scientific authority. It
only restores a missing object at the already-authoritative key when a source
object has the exact recorded byte size and SHA-256.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import boto3
import botocore
import psycopg

QUEUE_REFS = ("s3", "minio")


def _client(endpoint: str) -> Any:
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=os.environ.get("MINIO_ACCESS_KEY", "mdi-local"),
        aws_secret_access_key=os.environ.get("MINIO_SECRET_KEY", "mdi-local-dev"),
        region_name="us-east-1",
    )


def _missing(client: Any, bucket: str, key: str) -> bool:
    try:
        client.head_object(Bucket=bucket, Key=key)
    except botocore.exceptions.ClientError as exc:
        code = str((exc.response or {}).get("Error", {}).get("Code", ""))
        if code in {"404", "NoSuchKey", "NoSuchBucket", "NotFound"}:
            return True
        raise
    return False


def _read(client: Any, bucket: str, key: str) -> bytes:
    response = client.get_object(Bucket=bucket, Key=key)
    body = response["Body"]
    try:
        data = body.read()
    finally:
        close = getattr(body, "close", None)
        if callable(close):
            close()
    return data if isinstance(data, bytes) else bytes(data)


def _refs(
    conn: psycopg.Connection[Any],
    active: Any,
    bucket: str,
    project_ids: tuple[str, ...] = (),
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    project_filter = " and o.project_id = any(%s)" if project_ids else ""
    project_params: tuple[Any, ...] = (list(project_ids),) if project_ids else ()
    versions = conn.execute(
        f"""
        select v.id::text, o.id::text, o.project_id, o.display_name,
               v.normalized_payload_ref_json, v.content_hash,
               v.availability_status
        from scientific_object_versions v
        join scientific_objects o on o.id = v.scientific_object_id
        join projects p on p.id = o.project_id
        where p.created_by = 'user_local'
          {project_filter}
        order by o.project_id, o.id, v.version_no
        """,
        project_params,
    )
    for version_id, object_id, project_id, display_name, ref, content_hash, availability in versions:
        ref = ref or {}
        key = ref.get("object_key") or ref.get("storage_key")
        size = ref.get("byte_size") or ref.get("size_bytes") or ref.get("sizeBytes")
        checksum = ref.get("checksum") or ref.get("sha256") or content_hash
        if not key or size is None or not _missing(active, bucket, key):
            continue
        items.append(
            {
                "authority": "scientificObjectVersion",
                "id": version_id,
                "objectId": object_id,
                "projectId": project_id,
                "displayName": display_name,
                "targetKey": key,
                "sizeBytes": int(size),
                "sha256": str(checksum),
                "contentType": ref.get("media_type") or ref.get("content_type") or "application/json",
                "availability": availability,
            }
        )
    artifact_project_filter = " and a.project_id = any(%s)" if project_ids else ""
    artifacts = conn.execute(
        f"""
        select a.id, a.project_id, a.job_id, a.tool_call_id, a.type, a.name,
               a.storage_key, a.size_bytes, coalesce(a.sha256, a.content_hash),
               a.content_type, a.storage_provider
        from artifacts a
        join projects p on p.id = a.project_id
        where p.created_by = 'user_local'
          and a.storage_provider = any(%s)
          {artifact_project_filter}
        order by a.project_id, a.id
        """,
        (list(QUEUE_REFS), list(project_ids)) if project_ids else (list(QUEUE_REFS),),
    )
    for row in artifacts:
        artifact_id, project_id, job_id, tool_call_id, artifact_type, name, key, size, checksum, content_type, provider = row
        if not key or size is None or not _missing(active, bucket, key):
            continue
        items.append(
            {
                "authority": "artifact",
                "id": artifact_id,
                "projectId": project_id,
                "jobId": job_id,
                "toolCallId": tool_call_id,
                "artifactType": artifact_type,
                "name": name,
                "targetKey": key,
                "sizeBytes": int(size),
                "sha256": str(checksum),
                "contentType": content_type or "application/octet-stream",
                "storageProvider": provider,
            }
        )
    return items


def _dataset_exports(
    conn: psycopg.Connection[Any],
    project_ids: tuple[str, ...] = (),
) -> list[dict[str, Any]]:
    """Return exact normalized Dataset exports that the product may reopen.

    Unlike ScientificObjectVersion payload refs, legacy Dataset metadata does
    not persist a separate SHA-256 for ``metadata.json``. Recovery therefore
    requires the original same-key metadata object and validates its bound
    object id/content hash before restoring it.
    """

    items: list[dict[str, Any]] = []
    project_filter = " and d.project_id = any(%s)" if project_ids else ""
    rows = conn.execute(
        f"""
        select d.id, d.project_id, d.name, d.metadata_json
        from datasets d
        join projects p on p.id = d.project_id
        where p.created_by = 'user_local'
          {project_filter}
        order by d.project_id, d.id
        """,
        (list(project_ids),) if project_ids else (),
    )
    for dataset_id, project_id, dataset_name, metadata in rows:
        metadata = metadata or {}
        exports = metadata.get("normalizedExports") or metadata.get("normalized_exports") or []
        expected_scope = f"projects/{project_id}/datasets/{dataset_id}/normalized/"
        for export in exports:
            if not isinstance(export, dict):
                continue
            object_id = str(export.get("objectId") or export.get("object_id") or "")
            payload_key = str(export.get("storageKey") or export.get("storage_key") or "")
            metadata_key = str(export.get("metadataKey") or export.get("metadata_key") or "")
            content_hash = str(export.get("contentHash") or export.get("content_hash") or "").lower()
            if (
                not object_id
                or not payload_key.startswith(expected_scope)
                or not metadata_key.startswith(expected_scope)
                or len(content_hash) != 64
                or any(character not in "0123456789abcdef" for character in content_hash)
            ):
                raise RuntimeError(f"invalid normalized export metadata for Dataset {dataset_id}")
            items.append(
                {
                    "authority": "datasetNormalizedExport",
                    "datasetId": str(dataset_id),
                    "projectId": str(project_id),
                    "datasetName": str(dataset_name),
                    "objectId": object_id,
                    "payloadKey": payload_key,
                    "metadataKey": metadata_key,
                    "contentHash": content_hash,
                }
            )
    return items


def _source_index(clients: list[tuple[str, Any]], bucket: str, sizes: set[int]) -> dict[tuple[int, str], list[dict[str, str]]]:
    index: dict[tuple[int, str], list[dict[str, str]]] = defaultdict(list)
    for label, client in clients:
        token: str | None = None
        while True:
            args: dict[str, Any] = {"Bucket": bucket, "MaxKeys": 1000}
            if token:
                args["ContinuationToken"] = token
            page = client.list_objects_v2(**args)
            for entry in page.get("Contents", []):
                if int(entry["Size"]) not in sizes:
                    continue
                payload = _read(client, bucket, entry["Key"])
                signature = (len(payload), hashlib.sha256(payload).hexdigest())
                index[signature].append({"sourceStore": label, "sourceKey": entry["Key"]})
            if not page.get("IsTruncated"):
                break
            token = str(page["NextContinuationToken"])
    return index


def _read_same_key_source(
    clients: list[tuple[str, Any]],
    *,
    bucket: str,
    key: str,
) -> tuple[dict[str, str], bytes]:
    for label, client in clients:
        if label == "target":
            continue
        try:
            return {"sourceStore": label, "sourceKey": key}, _read(client, bucket, key)
        except botocore.exceptions.ClientError:
            continue
    raise RuntimeError(f"no exact same-key source for {key}")


def _validate_dataset_export_metadata(item: dict[str, Any], payload: bytes) -> None:
    try:
        metadata = json.loads(payload.decode("utf-8"))
    except Exception as exc:
        raise RuntimeError(f"invalid normalized metadata JSON for {item['metadataKey']}") from exc
    if (
        str(metadata.get("objectId") or "") != item["objectId"]
        or str(metadata.get("contentHash") or "").lower() != item["contentHash"]
    ):
        raise RuntimeError(f"normalized metadata identity mismatch for {item['metadataKey']}")


def restore(
    *,
    db_url: str,
    bucket: str,
    target_endpoint: str,
    source_endpoints: list[str],
    project_ids: tuple[str, ...] = (),
) -> dict[str, Any]:
    target = _client(target_endpoint)
    clients = [("target", target)]
    clients.extend((f"source-{index}", _client(endpoint)) for index, endpoint in enumerate(source_endpoints, start=1))
    with psycopg.connect(db_url) as conn:
        items = _refs(conn, target, bucket, project_ids)
        dataset_exports = _dataset_exports(conn, project_ids)
    index = _source_index(clients, bucket, {item["sizeBytes"] for item in items})
    results: list[dict[str, Any]] = []
    for item in items:
        expected = (item["sizeBytes"], item["sha256"])
        candidates = [candidate for candidate in index.get(expected, []) if candidate["sourceKey"] != item["targetKey"]]
        # Prefer a same-key copy from a retained store. This is both cheaper
        # and stronger than a same-hash cross-key match when qualification
        # storage preserved the original object layout.
        if not candidates:
            for label, client in clients:
                if label == "target":
                    continue
                try:
                    payload = _read(client, bucket, item["targetKey"])
                except botocore.exceptions.ClientError:
                    continue
                if (len(payload), hashlib.sha256(payload).hexdigest()) == expected:
                    candidates = [{"sourceStore": label, "sourceKey": item["targetKey"]}]
                    break
        if not candidates:
            raise RuntimeError(f"no exact source for {item['authority']}:{item['id']}:{item['targetKey']}")
        source = candidates[0]
        source_client = dict(clients)[source["sourceStore"]]
        payload = _read(source_client, bucket, source["sourceKey"])
        if (len(payload), hashlib.sha256(payload).hexdigest()) != expected:
            raise RuntimeError(f"source validation failed for {item['targetKey']}")
        if _missing(target, bucket, item["targetKey"]):
            target.put_object(Bucket=bucket, Key=item["targetKey"], Body=payload, ContentType=item["contentType"])
            action = "RESTORED"
        else:
            action = "NOOP"
        readback = _read(target, bucket, item["targetKey"])
        actual = (len(readback), hashlib.sha256(readback).hexdigest())
        if actual != expected:
            raise RuntimeError(f"target validation failed for {item['targetKey']}: {actual!r} != {expected!r}")
        results.append({**item, "source": source, "action": action})

    dataset_results: list[dict[str, Any]] = []
    for item in dataset_exports:
        payload_missing = _missing(target, bucket, item["payloadKey"])
        metadata_missing = _missing(target, bucket, item["metadataKey"])

        if payload_missing:
            payload_source, payload = _read_same_key_source(
                clients,
                bucket=bucket,
                key=item["payloadKey"],
            )
        else:
            payload_source = {"sourceStore": "target", "sourceKey": item["payloadKey"]}
            payload = _read(target, bucket, item["payloadKey"])
        if hashlib.sha256(payload).hexdigest() != item["contentHash"]:
            raise RuntimeError(f"normalized payload checksum mismatch for {item['payloadKey']}")

        if metadata_missing:
            metadata_source, metadata_payload = _read_same_key_source(
                clients,
                bucket=bucket,
                key=item["metadataKey"],
            )
        else:
            metadata_source = {"sourceStore": "target", "sourceKey": item["metadataKey"]}
            metadata_payload = _read(target, bucket, item["metadataKey"])
        _validate_dataset_export_metadata(item, metadata_payload)

        if payload_missing:
            target.put_object(
                Bucket=bucket,
                Key=item["payloadKey"],
                Body=payload,
                ContentType="application/json",
            )
        if metadata_missing:
            target.put_object(
                Bucket=bucket,
                Key=item["metadataKey"],
                Body=metadata_payload,
                ContentType="application/json",
            )

        payload_readback = _read(target, bucket, item["payloadKey"])
        metadata_readback = _read(target, bucket, item["metadataKey"])
        if hashlib.sha256(payload_readback).hexdigest() != item["contentHash"]:
            raise RuntimeError(f"target normalized payload validation failed for {item['payloadKey']}")
        _validate_dataset_export_metadata(item, metadata_readback)
        dataset_results.append(
            {
                **item,
                "payloadSource": payload_source,
                "metadataSource": metadata_source,
                "payloadAction": "RESTORED" if payload_missing else "NOOP",
                "metadataAction": "RESTORED" if metadata_missing else "NOOP",
            }
        )
    return {
        "schemaVersion": "phase14r.exact-minio-reference-recovery.v1.1",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "bucket": bucket,
        "targetEndpoint": target_endpoint,
        "sourceEndpoints": source_endpoints,
        "projectIds": list(project_ids),
        "referenceCountBefore": len(items),
        "restoredCount": sum(result["action"] == "RESTORED" for result in results),
        "noopCount": sum(result["action"] == "NOOP" for result in results),
        "items": results,
        "datasetExportCount": len(dataset_results),
        "datasetPayloadRestoredCount": sum(
            result["payloadAction"] == "RESTORED" for result in dataset_results
        ),
        "datasetMetadataRestoredCount": sum(
            result["metadataAction"] == "RESTORED" for result in dataset_results
        ),
        "datasetExports": dataset_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-url", default=os.environ.get("DATABASE_URL", "postgresql://mdi@127.0.0.1:55434/mdi"))
    parser.add_argument("--bucket", default=os.environ.get("MINIO_BUCKET", "mdi-artifacts"))
    parser.add_argument("--target-endpoint", default=os.environ.get("MINIO_ENDPOINT", "http://127.0.0.1:9000"))
    parser.add_argument("--source-endpoint", action="append", required=True)
    parser.add_argument(
        "--project-id",
        action="append",
        default=[],
        help="Limit exact-byte recovery to one project. Repeat for multiple projects.",
    )
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    evidence = restore(
        db_url=args.db_url,
        bucket=args.bucket,
        target_endpoint=args.target_endpoint,
        source_endpoints=args.source_endpoint,
        project_ids=tuple(args.project_id),
    )
    serialized = json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True)
    print(serialized)
    if args.evidence:
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        args.evidence.write_text(serialized + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
