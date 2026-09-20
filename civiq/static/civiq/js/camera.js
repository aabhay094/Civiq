/* CIVIQ — camera.js
   Handles opening the device camera (or falling back to a file input on
   desktop / unsupported browsers), capturing a still frame, and producing
   a File object ready to upload. */

const CiviqCamera = {
  stream: null,

  /** Starts the live camera preview inside the given <video> element. */
  async start(videoEl) {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('camera-unsupported');
    }
    this.stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: 'environment' } },
      audio: false,
    });
    videoEl.srcObject = this.stream;
    await videoEl.play();
  },

  stop() {
    if (this.stream) {
      this.stream.getTracks().forEach((t) => t.stop());
      this.stream = null;
    }
  },

  /** Captures the current video frame as a JPEG File. */
  capture(videoEl) {
    const canvas = document.createElement('canvas');
    canvas.width = videoEl.videoWidth;
    canvas.height = videoEl.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
    return new Promise((resolve) => {
      canvas.toBlob(
        (blob) => {
          resolve(new File([blob], `civiq-capture-${Date.now()}.jpg`, { type: 'image/jpeg' }));
        },
        'image/jpeg',
        0.9
      );
    });
  },
};
