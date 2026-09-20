/* CIVIQ — ai-report.js
   Orchestrates the AI Camera flow: capture -> preview -> analyze ->
   review -> submit. Keeps the captured File in memory across steps and
   drives the step-based UI in ai_camera.html. */

(function () {
  let capturedFile = null;
  let detectedLocation = null;
  let usingLiveCamera = false;

  const els = {};

  function qs(id) {
    return document.getElementById(id);
  }

  function showStep(name) {
    document.querySelectorAll('.ai-step').forEach((el) => el.classList.add('hidden'));
    qs(`step-${name}`).classList.remove('hidden');
  }

  function setPreviewImage(file) {
    const url = URL.createObjectURL(file);
    els.previewImg.src = url;
    els.reviewImg.src = url;
  }

  async function startCamera() {
    try {
      await CiviqCamera.start(els.video);
      usingLiveCamera = true;
      els.cameraFallback.classList.add('hidden');
      els.video.classList.remove('hidden');
      els.captureBtn.classList.remove('hidden');
    } catch (e) {
      // No camera available (e.g. desktop without webcam) — fall back to file upload.
      usingLiveCamera = false;
      els.video.classList.add('hidden');
      els.captureBtn.classList.add('hidden');
      els.cameraFallback.classList.remove('hidden');
    }
  }

  async function handleCapture() {
    const file = await CiviqCamera.capture(els.video);
    capturedFile = file;
    CiviqCamera.stop();
    setPreviewImage(file);
    showStep('preview');
  }

  function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    capturedFile = file;
    setPreviewImage(file);
    showStep('preview');
  }

  function handleRetake() {
    capturedFile = null;
    showStep('capture');
    startCamera();
  }

  async function handleAnalyze() {
    if (!capturedFile) return;
    showStep('analyzing');

    // Kick off location detection in parallel with AI analysis.
    const locationPromise = CiviqLocation.request((status) => {
      els.locationStatus.textContent = status;
    }).then((loc) => {
      detectedLocation = loc;
    });

    const formData = new FormData();
    formData.append('image', capturedFile);

    let result;
    try {
      const res = await fetch(AI_ANALYZE_URL, {
        method: 'POST',
        headers: { 'X-CSRFToken': CSRF_TOKEN },
        body: formData,
      });
      result = await res.json();
    } catch (e) {
      result = {
        problem_type: 'Unclassified (analysis failed)',
        category: null,
        sector_id: null,
        description: '',
        priority: 'medium',
        confidence: 0.0,
        is_fallback: true,
        sectors: [],
      };
    }

    await locationPromise;
    populateReview(result);
    showStep('review');
  }

  function populateReview(result) {
    els.reviewProblemType.value = result.problem_type || '';
    els.reviewDescription.value = result.description || '';
    els.reviewPriority.value = result.priority || 'medium';
    els.reviewConfidence.value = result.confidence || 0;
    els.reviewAiProcessed.value = result.is_fallback ? 'false' : 'true';

    // Populate the category <select> from the live DB sector list.
    els.reviewSector.innerHTML = '<option value="">— Select category —</option>';
    (result.sectors || []).forEach((s) => {
      const opt = document.createElement('option');
      opt.value = s.id;
      opt.textContent = s.name;
      if (result.sector_id && s.id === result.sector_id) opt.selected = true;
      els.reviewSector.appendChild(opt);
    });

    if (result.is_fallback) {
      els.fallbackNotice.classList.remove('hidden');
    } else {
      els.fallbackNotice.classList.add('hidden');
      if (result.confidence < 0.5) {
        els.lowConfidenceNotice.classList.remove('hidden');
      } else {
        els.lowConfidenceNotice.classList.add('hidden');
      }
    }

    if (detectedLocation) {
      els.reviewLatitude.value = detectedLocation.latitude;
      els.reviewLongitude.value = detectedLocation.longitude;
    }
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!capturedFile) return;

    const formData = new FormData(els.reviewForm);
    formData.append('image', capturedFile);

    els.submitBtn.disabled = true;
    els.submitBtn.textContent = 'Submitting…';

    fetch(AI_SUBMIT_URL, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN },
      body: formData,
    }).then((res) => {
      if (res.redirected) {
        window.location.href = res.url;
      } else {
        window.location.reload();
      }
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    els.video = qs('cameraVideo');
    els.captureBtn = qs('captureBtn');
    els.cameraFallback = qs('cameraFallback');
    els.fileInput = qs('fileInput');
    els.previewImg = qs('previewImg');
    els.reviewImg = qs('reviewImg');
    els.retakeBtn = qs('retakeBtn');
    els.analyzeBtn = qs('analyzeBtn');
    els.locationStatus = qs('locationStatus');
    els.reviewForm = qs('reviewForm');
    els.reviewProblemType = qs('reviewProblemType');
    els.reviewDescription = qs('reviewDescription');
    els.reviewPriority = qs('reviewPriority');
    els.reviewSector = qs('reviewSector');
    els.reviewConfidence = qs('reviewConfidence');
    els.reviewAiProcessed = qs('reviewAiProcessed');
    els.reviewLatitude = qs('reviewLatitude');
    els.reviewLongitude = qs('reviewLongitude');
    els.fallbackNotice = qs('fallbackNotice');
    els.lowConfidenceNotice = qs('lowConfidenceNotice');
    els.submitBtn = qs('submitBtn');
    els.retakeFromReviewBtn = qs('retakeFromReviewBtn');

    startCamera();

    els.captureBtn.addEventListener('click', handleCapture);
    els.fileInput.addEventListener('change', handleFileUpload);
    els.retakeBtn.addEventListener('click', handleRetake);
    els.analyzeBtn.addEventListener('click', handleAnalyze);
    els.retakeFromReviewBtn.addEventListener('click', handleRetake);
    els.reviewForm.addEventListener('submit', handleSubmit);

    lucide.createIcons();
  });
})();
