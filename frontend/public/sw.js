/**
 * Bear's Den Service Worker
 * Provides offline caching for static assets and API responses
 */

const CACHE_NAME = 'bears-den-v1';
const STATIC_CACHE = 'bears-den-static-v1';
const API_CACHE = 'bears-den-api-v1';

// Static assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/logo.svg',
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  // Activate immediately
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => {
            return name.startsWith('bears-den-') &&
                   name !== STATIC_CACHE &&
                   name !== API_CACHE;
          })
          .map((name) => caches.delete(name))
      );
    })
  );
  // Take control of all clients immediately
  self.clients.claim();
});

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip API requests that require authentication
  if (url.pathname.startsWith('/api/')) {
    // For API requests, try network first, then cache for read-only endpoints
    if (url.pathname.includes('/heroes/all') ||
        url.pathname.includes('/lineups/templates') ||
        url.pathname.includes('/lineups/general')) {
      event.respondWith(networkFirstThenCache(request, API_CACHE));
    }
    return;
  }

  // For static assets, use cache first
  if (request.destination === 'image' ||
      request.destination === 'font' ||
      url.pathname.endsWith('.css') ||
      url.pathname.endsWith('.js')) {
    event.respondWith(cacheFirstThenNetwork(request, STATIC_CACHE));
    return;
  }

  // For HTML pages, use network first
  event.respondWith(networkFirstThenCache(request, STATIC_CACHE));
});

// Cache first, then network
async function cacheFirstThenNetwork(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);

  if (cachedResponse) {
    // Update cache in background
    fetch(request).then((response) => {
      if (response.ok) {
        cache.put(request, response.clone());
      }
    }).catch(() => {});

    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    // Return offline fallback if available
    return new Response('Offline', { status: 503 });
  }
}

// Network first, then cache
async function networkFirstThenCache(request, cacheName) {
  const cache = await caches.open(cacheName);

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    // Return offline fallback
    return new Response('Offline', { status: 503 });
  }
}

// Listen for messages from the app
self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
});
