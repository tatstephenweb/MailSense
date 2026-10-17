// PUSH NOTIFICATIONS
self.addEventListener('push', function(event) {
    const data = event.data.json();

    event.waitUntil(
        self.registration.showNotification(data.title, {
            body: data.body,
            icon: '/static/icon.png'   // use your existing MailSense icon
        })
    );
});


//PWA BUILDING
/*const CACHE_NAME = 'mailsense-v1';
const APP_SHELL = [
    '/dashboard',
    '/static/manifest.json',
    '/static/icon.png'
    // add your CSS/JS files here if they're separate static files
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll(APP_SHELL);
        })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request).then(function(cached) {
            return cached || fetch(event.request);
        })
    );
});

self.addEventListener('push', function(event) {
    const data = event.data.json();

    event.waitUntil(
        self.registration.showNotification(data.title, {
            body: data.body,
            icon: '/static/icon.png'
        })
    );
});*/

self.addEventListener('push', function(event) {
    const data = event.data.json();

    event.waitUntil(
        self.registration.showNotification(data.title, {
            body: data.body,
            icon: '/static/icon.png'
        })
    );
});