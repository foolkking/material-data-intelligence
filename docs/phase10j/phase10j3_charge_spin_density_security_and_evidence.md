# Phase 10J-3 Security, Performance, and Evidence Closure

## Trust boundary

Uploaded CHGCAR/CHG/CUBE bytes are untrusted. Parser output, canonical field
metadata, payload hashes, and the validated dataset are the only inputs to
the frontend product. The Worker and renderer use application-owned
algorithms, geometry, materials, URLs, and caps.

The evidence audit confirms: no artifact JavaScript, HTML execution, shader,
dynamic import, external URL, external asset, or external request. The
required marker is `NO_CHARGE_SPIN_PRODUCT_EXTERNAL_NETWORK_REQUESTS` and the
secret scan marker is `NO_SECRET_PATTERN_HITS`.

## Bounds and failure behavior

Canonical parser and frontend payload caps remain authoritative. Derived
fields cannot increase voxel, payload, layer, mesh, Worker, WebGL, or PNG
budgets. Invalid relationships, incompatible quantities, unsupported
non-collinear products, negative electron-density anomalies, and missing
augmentation contributions are reported as typed or visible warnings. The
backend job is not marked failed because the browser lacks Worker/WebGL
support; JSON and metadata remain available.

## Evidence

The runtime evidence includes live collinear artifacts, source and derived
field records, exact integral values, formula relationships, electron,
augmentation, and signed-charge cases, plus browser DOM/console/network/
accessibility/interaction/performance captures. The browser runner verifies
the live default product, paired surfaces, mode changes, integral rows,
formula provenance, Chromium/Firefox/WebKit WebGL2 support, mobile layout,
and zero external requests.
