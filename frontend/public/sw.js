const CACHE_NAME = 'bulamu-chain-bot-v1.0.0';
const urlsToCache = [
    '/',
    '/voice-consultation',
    '/emergency',
    '/blockchain',
    '/education',
    '/consultation',
    '/login',
    '/register',
    '/manifest.json',
    // Add your static assets
    '/favicon.ico',
    // Add other important routes and assets
];

// Install event - cache resources
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version or fetch from network
                if (response) {
                    return response;
                }

                return fetch(event.request).then((response) => {
                    // Don't cache non-successful responses
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }

                    // Clone the response
                    const responseToCache = response.clone();

                    caches.open(CACHE_NAME)
                        .then((cache) => {
                            cache.put(event.request, responseToCache);
                        });

                    return response;
                }).catch(() => {
                    // Return offline page for navigation requests
                    if (event.request.destination === 'document') {
                        return caches.match('/offline.html');
                    }
                });
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Background sync for offline consultations
self.addEventListener('sync', (event) => {
    if (event.tag === 'background-consultation') {
        event.waitUntil(syncConsultations());
    }
});

async function syncConsultations() {
    // Get pending consultations from IndexedDB
    const pendingConsultations = await getPendingConsultations();

    for (const consultation of pendingConsultations) {
        try {
            // Try to send the consultation
            await fetch('/api/consultations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(consultation)
            });

            // Remove from pending if successful
            await removePendingConsultation(consultation.id);
        } catch (error) {
            console.error('Failed to sync consultation:', error);
        }
    }
}

// Mock functions for IndexedDB operations
async function getPendingConsultations() {
    // Implement IndexedDB logic to retrieve pending consultations
    return [];
}

async function removePendingConsultation(id) {
    // Implement IndexedDB logic to remove synced consultation
}

// Push notification event
self.addEventListener('push', (event) => {
    const options = {
        body: event.data ? event.data.text() : 'New health update available',
        icon: '/icons/icon-192x192.png',
        badge: '/icons/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: '2'
        },
        actions: [
            {
                action: 'explore',
                title: 'View Details',
                icon: '/icons/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close notification',
                icon: '/icons/xmark.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('BulamuChainBot', options)
    );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    if (event.action === 'explore') {
        // Open the app to a specific page
        event.waitUntil(
            clients.openWindow('/')
        );
    } else if (event.action === 'close') {
        // Just close the notification
        event.notification.close();
    } else {
        // Default action - open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});
