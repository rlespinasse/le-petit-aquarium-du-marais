(() => {
  "use strict";

  /* ── Utilitaires ────────────────────────────────── */
  const rand = (min, max) => Math.random() * (max - min) + min;
  const aquarium = document.getElementById("aquarium");

  /* ── Configuration ─────────────────────────────── */
  const config = {
    title: aquarium.dataset.title || "Le petit aquarium du Marais",
    mascot: aquarium.dataset.mascot || "Glouglou",
    contact: aquarium.dataset.contact || "",
  };

  // Appliquer le titre
  document.title = config.title;
  const sandTitle = aquarium.querySelector(".sand-title");
  if (sandTitle) sandTitle.textContent = config.title;
  const srH1 = document.querySelector("h1.sr-only");
  if (srH1) srH1.textContent = `${config.title} — un aquarium collaboratif rempli de dessins de poissons faits par des enfants`;

  // Appliquer la configuration au panneau d'information
  const infoTitle = document.getElementById("infoTitle");
  if (infoTitle) infoTitle.textContent = `Bienvenue dans ${config.title}\u00A0!`;
  const infoMascotName = document.getElementById("infoMascotName");
  if (infoMascotName) infoMascotName.textContent = config.mascot;
  // Décoder l'email de contact (base64) et l'appliquer à tous les liens de contact
  if (config.contact) {
    let email;
    try { email = atob(config.contact); } catch (e) { email = config.contact; }
    document.querySelectorAll("#infoContact, #legalContact").forEach((el) => {
      el.href = `mailto:${email}`;
      el.textContent = email;
    });
  }

  /* ── Cycle jour/nuit ────────────────────────────── */
  let forcedPhase = null;

  function getDayPhase() {
    if (forcedPhase) return forcedPhase;
    const hour = new Date().getHours();
    if (hour >= 6 && hour < 10) return "dawn";
    if (hour >= 10 && hour < 17) return "day";
    if (hour >= 17 && hour < 20) return "dusk";
    return "night";
  }

  function applyDayNight() {
    const phase = getDayPhase();
    aquarium.dataset.phase = phase;

    const gradients = {
      dawn:  "linear-gradient(180deg, #f4a460 0%, #e07850 10%, #1a8fc4 35%, #14729e 55%, #0e5a7e 75%, #072a3f 100%)",
      day:   "linear-gradient(180deg, #1a8fc4 0%, #14729e 20%, #0e5a7e 45%, #0b3d5b 70%, #072a3f 100%)",
      dusk:  "linear-gradient(180deg, #c0392b 0%, #d35400 10%, #1a6b8a 35%, #0e5a7e 55%, #0b3d5b 75%, #072a3f 100%)",
      night: "linear-gradient(180deg, #0a1628 0%, #0b2040 20%, #0a2a4a 45%, #081e35 70%, #050e1a 100%)",
    };
    aquarium.style.background = gradients[phase];

    let stars = aquarium.querySelector(".stars");
    if (phase === "night") {
      if (!stars) {
        stars = document.createElement("div");
        stars.className = "stars";
        stars.setAttribute("aria-hidden", "true");
        for (let i = 0; i < 30; i++) {
          const star = document.createElement("span");
          star.className = "star";
          star.style.left = `${rand(2, 98)}%`;
          star.style.top = `${rand(1, 12)}%`;
          star.style.animationDelay = `${rand(0, 3)}s`;
          stars.appendChild(star);
        }
        aquarium.prepend(stars);
      }
    } else if (stars) {
      stars.remove();
    }
  }

  applyDayNight();
  setInterval(applyDayNight, 60000);

  /* ── Sélecteur de période ─────────────────────── */
  const phaseBtn = document.getElementById("phaseToggle");
  const phaseLabel = document.getElementById("phaseLabel");
  const phases = [
    { value: null,    label: "Auto" },
    { value: "dawn",  label: "Aube" },
    { value: "day",   label: "Jour" },
    { value: "dusk",  label: "Cr\u00e9puscule" },
    { value: "night", label: "Nuit" },
  ];
  let phaseIndex = 0;

  function cyclePhase() {
    phaseIndex = (phaseIndex + 1) % phases.length;
    forcedPhase = phases[phaseIndex].value;
    if (phaseLabel) phaseLabel.textContent = phases[phaseIndex].label;
    if (phaseBtn) {
      phaseBtn.setAttribute("aria-pressed", String(forcedPhase !== null));
      phaseBtn.setAttribute("aria-label",
        forcedPhase ? `Période : ${phases[phaseIndex].label}` : "Changer la période de la journée"
      );
    }
    applyDayNight();
  }

  if (phaseBtn) phaseBtn.addEventListener("click", cyclePhase);

  /* ── Particules flottantes (plancton) ────────────── */
  const particlesContainer = document.createElement("div");
  particlesContainer.className = "particles";
  particlesContainer.setAttribute("aria-hidden", "true");
  aquarium.appendChild(particlesContainer);

  function spawnParticle() {
    const p = document.createElement("span");
    p.className = "particle";
    p.style.left = `${rand(0, 100)}%`;
    p.style.top = `${rand(5, 85)}%`;
    p.style.animationDuration = `${rand(8, 20)}s`;
    p.style.animationDelay = `${rand(0, 5)}s`;
    particlesContainer.appendChild(p);
    setTimeout(() => p.remove(), 25000);
  }

  for (let i = 0; i < 20; i++) setTimeout(spawnParticle, i * 300);
  setInterval(spawnParticle, 1500);

  /* ── Bulles ───────────────────────────────────── */
  const bubblesContainer = document.getElementById("bubbles");

  function spawnBubble() {
    const b = document.createElement("div");
    b.className = "bubble";
    const size = rand(4, 14);
    b.style.width = `${size}px`;
    b.style.height = `${size}px`;
    b.style.left = `${rand(5, 95)}%`;
    b.style.bottom = `${rand(5, 15)}%`;
    const duration = rand(4, 9);
    b.style.animationDuration = `${duration}s`;
    bubblesContainer.appendChild(b);
    setTimeout(() => b.remove(), duration * 1000);
  }

  setInterval(spawnBubble, 1200);
  for (let i = 0; i < 5; i++) setTimeout(spawnBubble, i * 200);

  /* ── Poisson mascotte (favicon) ──────────────── */
  const contributedFish = document.querySelectorAll(".fish");
  const isAlone = contributedFish.length === 0;

  const mascot = document.createElement("div");
  mascot.className = "fish fish-mascot";
  mascot.dataset.mascot = "true";
  mascot.dataset.message = isAlone
    ? `Je suis ${config.mascot} ! Dessinez-moi des copains, je tourne en rond tout seul !`
    : `Je suis ${config.mascot} ! J'adore nager avec vous les copines et les copains !`;
  const mascotImg = document.createElement("img");
  mascotImg.src = "favicon.svg";
  mascotImg.alt = `${config.mascot}, la mascotte de l'aquarium`;
  mascot.appendChild(mascotImg);
  aquarium.appendChild(mascot);

  /* ── Population de poissons ─────────────────── */
  const sourceFish = Array.from(document.querySelectorAll(".fish:not(.fish-mascot)"));

  /* ── Compteur de poissons ───────────────────── */
  const totalFishCount = sourceFish.length + 1; // +1 pour la mascotte
  const counterEl = document.getElementById("fishCounter");
  if (counterEl) {
    counterEl.textContent = `${totalFishCount} poisson${totalFishCount > 1 ? "s" : ""} dans l'aquarium`;
  }

  /* ── Annonces pour lecteurs d'écran ─────────── */
  const srAnnounce = document.getElementById("srAnnounce");

  /* ── Bulle de dialogue active (une seule à la fois) ── */
  let activeSpeech = null;

  function clearActiveSpeech() {
    if (activeSpeech) {
      activeSpeech.remove();
      activeSpeech = null;
    }
  }

  /* ── Bouton son ───────────────────────────────── */
  let soundEnabled = false;
  let audioCtx = null;
  let bubbleSoundInterval = null;
  const soundBtn = document.getElementById("soundToggle");

  function playBubbleSound() {
    if (!audioCtx || !soundEnabled) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = "sine";
    osc.frequency.setValueAtTime(rand(400, 900), audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(rand(200, 500), audioCtx.currentTime + 0.15);
    gain.gain.setValueAtTime(0.03, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.2);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.2);
  }

  function toggleSound() {
    soundEnabled = !soundEnabled;
    if (soundBtn) {
      soundBtn.setAttribute("aria-pressed", String(soundEnabled));
      soundBtn.setAttribute("aria-label",
        soundEnabled ? "Couper le son" : "Activer le son"
      );
    }
    if (soundEnabled) {
      if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      bubbleSoundInterval = setInterval(playBubbleSound, rand(2000, 5000));
    } else {
      clearInterval(bubbleSoundInterval);
    }
  }

  if (soundBtn) {
    soundBtn.addEventListener("click", toggleSound);
  }

  /* ── Bulle de dialogue ────────────────────────── */
  function showSpeechBubble(fishEl, message, direction) {
    if (fishEl.style.visibility === "hidden") return;

    clearActiveSpeech();

    const container = document.createElement("div");
    container.className = "speech-container";

    if (direction === 1) {
      container.style.left = "100%";
    } else {
      container.style.right = "100%";
      container.style.flexDirection = "row-reverse";
    }

    const dotSizes = [4, 6, 8];
    dotSizes.forEach((size, i) => {
      const dot = document.createElement("span");
      dot.className = "speech-dot";
      dot.style.width = `${size}px`;
      dot.style.height = `${size}px`;
      dot.style.animationDelay = `${i * 0.1}s`;
      container.appendChild(dot);
    });

    const bubble = document.createElement("div");
    bubble.className = "speech-bubble";
    bubble.setAttribute("aria-hidden", "true");
    bubble.innerHTML = message;
    container.appendChild(bubble);

    fishEl.appendChild(container);
    activeSpeech = container;

    if (srAnnounce) srAnnounce.textContent = bubble.textContent;

    setTimeout(() => {
      if (activeSpeech === container) {
        container.remove();
        activeSpeech = null;
      }
    }, 3000);
  }

  /* ── Interaction clic/toucher sur les poissons ── */
  function onFishClick(fishEl) {
    const img = fishEl.querySelector("img");
    const isMascot = fishEl.dataset.mascot === "true";
    let message;

    if (isMascot) {
      message = fishEl.dataset.message;
    } else {
      const fishName = fishEl.dataset.fishName;
      const alt = img ? img.getAttribute("alt") || "" : "";
      const nameMatch = alt.match(/poisson de (.+)/i);
      if (fishName && nameMatch) {
        message = `Je suis <strong>${fishName}</strong>, le poisson de <strong>${nameMatch[1]}</strong>`;
      } else if (nameMatch) {
        message = `Je suis le poisson de <strong>${nameMatch[1]}</strong>`;
      }
    }

    if (!message) return;

    const style = getComputedStyle(fishEl);
    const matrix = new DOMMatrix(style.transform);
    const currentX = matrix.m41;
    const aqWidth = aquarium.getBoundingClientRect().width;
    const direction = currentX < aqWidth / 2 ? 1 : -1;

    showSpeechBubble(fishEl, message, direction);

    fishEl.animate(
      [
        { filter: "brightness(1.3)" },
        { filter: "brightness(1)" },
      ],
      { duration: 600, easing: "ease-out" }
    );

    if (img) {
      img.animate(
        [
          { transform: img.style.transform + " rotate(0deg)" },
          { transform: img.style.transform + " rotate(15deg)" },
          { transform: img.style.transform + " rotate(-10deg)" },
          { transform: img.style.transform + " rotate(0deg)" },
        ],
        { duration: 500, easing: "ease-in-out" }
      );
    }
  }

  aquarium.addEventListener("click", (e) => {
    const fishEl = e.target.closest(".fish");
    if (fishEl) onFishClick(fishEl);
  });

  /* ── Animation des poissons ─────────────────── */
  const fishElements = document.querySelectorAll(".fish");
  const SAFE_TOP_MIN = 5;
  const SAFE_TOP_MAX = 72;

  function animateFish(fishEl) {
    const aq = aquarium.getBoundingClientRect();
    const isMascot = fishEl.dataset.mascot === "true";

    // Effet de profondeur : l'échelle détermine la vitesse et l'opacité
    const scale = isMascot ? rand(0.8, 1.2) : rand(0.5, 1.5);
    const depthFactor = scale;
    const speed = rand(20, 50) * depthFactor + 15;
    const depthOpacity = 0.4 + depthFactor * 0.4;
    const depthZ = Math.round(scale * 10);

    const direction = Math.random() > 0.5 ? 1 : -1;
    const topPercent = rand(SAFE_TOP_MIN, SAFE_TOP_MAX);

    fishEl.style.top = `${topPercent}%`;
    fishEl.style.scale = `${scale}`;
    fishEl.style.opacity = `${depthOpacity}`;
    fishEl.style.zIndex = `${depthZ}`;

    const fishWidth = fishEl.offsetWidth || 120;
    const startX = direction === 1 ? -fishWidth : aq.width + fishWidth;
    const endX = direction === 1 ? aq.width + fishWidth : -fishWidth;
    const distance = Math.abs(endX - startX);
    const duration = distance / speed;

    const img = fishEl.querySelector("img");
    if (img) {
      img.style.transform = direction === 1 ? "scaleX(-1)" : "scaleX(1)";
      if (img.dataset.src && !img.src.includes(img.dataset.src)) {
        img.src = img.dataset.src;
      }
    }

    fishEl.style.visibility = "visible";

    const animation = fishEl.animate(
      [
        { transform: `translateX(${startX}px)` },
        { transform: `translateX(${endX}px)` },
      ],
      {
        duration: duration * 1000,
        easing: "linear",
        fill: "forwards",
      }
    );

    fishEl.animate(
      [
        { marginTop: "0px" },
        { marginTop: `${rand(-12, 12)}px` },
        { marginTop: "0px" },
      ],
      {
        duration: rand(2000, 4000),
        iterations: Math.ceil(duration / 3),
        easing: "ease-in-out",
      }
    );

    animation.onfinish = () => {
      fishEl.style.visibility = "hidden";
      setTimeout(() => animateFish(fishEl), rand(500, 3000));
    };
  }

  // Lancer la mascotte immédiatement, puis échelonner les autres
  animateFish(mascot);
  const otherFish = Array.from(fishElements).filter(f => f !== mascot);
  otherFish.forEach((fish, i) => {
    setTimeout(() => animateFish(fish), (i + 1) * rand(200, 1500));
  });

  /* ── Panneau galerie ──────────────────────────── */
  const galleryPanel = document.getElementById("galleryPanel");
  const galleryBtn = document.getElementById("galleryToggle");
  const galleryClose = document.getElementById("galleryClose");
  const galleryGrid = document.getElementById("galleryGrid");

  if (galleryGrid) {
    // Ajouter la mascotte en premier
    const mascotCard = document.createElement("div");
    mascotCard.className = "gallery-card";
    const mascotCardImg = document.createElement("img");
    mascotCardImg.src = "favicon.svg";
    mascotCardImg.alt = `${config.mascot}, la mascotte`;
    mascotCardImg.loading = "lazy";
    const mascotLabel = document.createElement("span");
    mascotLabel.className = "gallery-name";
    mascotLabel.textContent = config.mascot;
    mascotCard.appendChild(mascotCardImg);
    mascotCard.appendChild(mascotLabel);
    galleryGrid.appendChild(mascotCard);

    // Puis les poissons contribués
    sourceFish.forEach((fishEl) => {
      const img = fishEl.querySelector("img");
      if (!img) return;
      const alt = img.getAttribute("alt") || "";
      const fishName = fishEl.dataset.fishName;
      const nameMatch = alt.match(/poisson de (.+)/i);
      const childName = nameMatch ? nameMatch[1] : "?";

      const card = document.createElement("div");
      card.className = "gallery-card";

      const cardImg = document.createElement("img");
      const picture = fishEl.querySelector("picture");
      if (picture) {
        const source = picture.querySelector("source");
        cardImg.src = source ? source.srcset : img.src;
      } else {
        cardImg.src = img.src;
      }
      cardImg.alt = alt;
      cardImg.loading = "lazy";

      const label = document.createElement("span");
      label.className = "gallery-name";
      label.textContent = fishName ? `${fishName} (${childName})` : childName;

      card.appendChild(cardImg);
      card.appendChild(label);
      galleryGrid.appendChild(card);
    });
  }

  function openGallery() {
    if (!galleryPanel) return;
    galleryPanel.classList.add("visible");
    galleryBtn.setAttribute("aria-expanded", "true");
    galleryClose.focus();
  }

  function closeGallery() {
    if (!galleryPanel) return;
    galleryPanel.classList.remove("visible");
    galleryBtn.setAttribute("aria-expanded", "false");
    galleryBtn.focus();
  }

  if (galleryBtn) galleryBtn.addEventListener("click", openGallery);
  if (galleryClose) galleryClose.addEventListener("click", closeGallery);
  if (galleryPanel) {
    galleryPanel.addEventListener("click", (e) => {
      if (e.target === galleryPanel) closeGallery();
    });
  }

  /* ── Panneau mentions légales ───────────────── */
  const legalPanel = document.getElementById("legalPanel");
  const legalBtn = document.getElementById("legalToggle");
  const legalClose = document.getElementById("legalClose");

  function openLegal() {
    if (!legalPanel) return;
    closePanel();
    legalPanel.classList.add("visible");
    legalClose.focus();
  }

  function closeLegal() {
    if (!legalPanel) return;
    legalPanel.classList.remove("visible");
  }

  document.querySelectorAll("#legalToggle, #legalToggle2, #legalToggleBar").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      openLegal();
    });
  });
  if (legalClose) legalClose.addEventListener("click", closeLegal);
  if (legalPanel) {
    legalPanel.addEventListener("click", (e) => {
      if (e.target === legalPanel) closeLegal();
    });
  }

  /* ── Panneau d'information ──────────────────── */
  const panel = document.getElementById("infoPanel");
  const openBtn = document.getElementById("infoToggle");
  const closeBtn = document.getElementById("infoClose");

  function openPanel() {
    panel.classList.add("visible");
    openBtn.setAttribute("aria-expanded", "true");
    closeBtn.focus();
  }

  function closePanel() {
    panel.classList.remove("visible");
    openBtn.setAttribute("aria-expanded", "false");
    openBtn.focus();
  }

  openBtn.addEventListener("click", openPanel);
  closeBtn.addEventListener("click", closePanel);
  panel.addEventListener("click", (e) => {
    if (e.target === panel) closePanel();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (legalPanel && legalPanel.classList.contains("visible")) {
        closeLegal();
      } else if (galleryPanel && galleryPanel.classList.contains("visible")) {
        closeGallery();
      } else if (panel.classList.contains("visible")) {
        closePanel();
      }
    }

    const activeDialog = [legalPanel, galleryPanel, panel].find(
      d => d && d.classList.contains("visible")
    );
    if (e.key === "Tab" && activeDialog) {
      const focusable = activeDialog.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });
})();
