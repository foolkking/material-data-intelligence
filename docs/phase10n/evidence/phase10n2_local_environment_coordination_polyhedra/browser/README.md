Browser evidence was produced by the real Chromium, Firefox, WebKit and Chromium
390x844 Workspace replay runner over the exact N2 contract fixture. Each desktop
browser lazy-loaded one persisted N2 payload, selected the exact site, opened the
Inspector and rendered backend vertices/faces without a canvas fallback. Chromium
completed 50 mount/unmount cycles with zero listener, observer, animation-frame,
WebGL, canvas or payload-request growth. The 200% reflow-equivalent viewport and
mobile viewport both recorded zero horizontal overflow; mobile focus trap/return
passed and the minimum visible touch target was 44 CSS px. Console errors, page
errors, failed responses and unapproved external requests were all zero.
