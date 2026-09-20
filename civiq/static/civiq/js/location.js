/* CIVIQ — location.js
   Small, reusable GPS helper for the AI Camera report flow.
   Never blocks the flow if permission is denied. */

const CiviqLocation = {
  /**
   * Requests the browser's current position.
   * onStatus(text) is called with human-readable status updates.
   * Resolves to {latitude, longitude} or null (never rejects).
   */
  request(onStatus) {
    return new Promise((resolve) => {
      if (!navigator.geolocation) {
        onStatus && onStatus('Location not supported on this device.');
        resolve(null);
        return;
      }
      onStatus && onStatus('Detecting your location…');
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          onStatus && onStatus('📍 Location detected');
          resolve({
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
          });
        },
        (err) => {
          onStatus && onStatus('📍 Location permission required — you can still submit without it.');
          resolve(null);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
      );
    });
  },
};
