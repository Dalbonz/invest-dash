const CACHE_NAME = 'bk-dash-v1';

self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))))
  );
  self.clients.claim();
});

// data.json은 항상 네트워크에서 최신으로, 나머지 정적 자원은 네트워크 우선 + 실패시 캐시 폴백
self.addEventListener('fetch', (e) => {
  if (e.request.url.includes('data.json')) return;
  e.respondWith(
    fetch(e.request)
      .then(res => {
        const resClone = res.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(e.request, resClone));
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});
