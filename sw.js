// Service Worker - Jam WITA (mode offline)
// Ubah angka versi saat file diperbarui agar cache lama dibuang
const CACHE = "jam-wita-v6";
const ASSETS = [
  "./",
  "./index.html",
  "./index_jam.html",
  "./manifest.json",
  "./favicon.ico",
  "./icons/icon-48.png",
  "./icons/icon-72.png",
  "./icons/icon-96.png",
  "./icons/icon-144.png",
  "./icons/icon-192.png",
  "./icons/icon-256.png",
  "./icons/icon-384.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-512.png",
  "./icons/apple-touch-icon.png"
];

// Simpan semua file saat pemasangan (satu file gagal tidak membatalkan yang lain)
self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) =>
      Promise.allSettled(ASSETS.map((a) =>
        fetch(a, { cache: "reload" }).then((res) => { if (res.ok) return c.put(a, res); })
      ))
    )
  );
  self.skipWaiting();
});

// Buang cache versi lama
self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Cache dulu (instan & offline), sambil memperbarui salinan di latar belakang
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;

  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const hit = await cache.match(req, { ignoreSearch: true });

    const refresh = fetch(req)
      .then((res) => { if (res && res.ok) cache.put(req, res.clone()); return res; })
      .catch(() => null);

    if (hit) { e.waitUntil(refresh); return hit; }

    const res = await refresh;
    if (res) return res;

    if (req.mode === "navigate") {
      const fallback = (await cache.match("./")) || (await cache.match("./index.html")) || (await cache.match("./index_jam.html"));
      if (fallback) return fallback;
    }
    return new Response("Offline", { status: 503, statusText: "Offline" });
  })());
});
