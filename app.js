/**
 * منطق برنامه پخش‌کننده کتاب صوتی مزرعه حیوانات
 * پشتیبانی از مسیریابی پارامتری (?s=cow) و سازگاری با انواع مرورگرهای موبایل
 */

// داده‌های پیش‌فرض حیوانات (برای تضمین عملکرد بدون مشکل حتی در محیط‌های بدون وب‌سرور/file://)
const FALLBACK_ANIMALS = [
  { id: 'hen', name: 'مرغ', emoji: '🐔', audio: 'audio/hen.mp3' },
  { id: 'cow', name: 'گاو', emoji: '🐄', audio: 'audio/cow.mp3' },
  { id: 'sheep', name: 'گوسفند', emoji: '🐑', audio: 'audio/sheep.mp3' },
  { id: 'goose', name: 'غاز', emoji: '🪿', audio: 'audio/goose.mp3' },
  { id: 'duck', name: 'اردک', emoji: '🦆', audio: 'audio/duck.mp3' },
  { id: 'donkey', name: 'الاغ', emoji: '🫏', audio: 'audio/donkey.mp3' },
  { id: 'dog', name: 'سگ گله', emoji: '🐕', audio: 'audio/dog.mp3' },
  { id: 'horse', name: 'اسب', emoji: '🐎', audio: 'audio/horse.mp3' },
  { id: 'goat', name: 'بز', emoji: '🐐', audio: 'audio/goat.mp3' }
];

class FarmAudioApp {
  constructor() {
    this.animals = [];
    this.currentAnimal = null;
    this.isPlaying = false;

    // عناصر صفحه
    this.playerSection = document.getElementById('player-section');
    this.animalEmoji = document.getElementById('animal-emoji');
    this.animalName = document.getElementById('animal-name');
    this.soundSubtitle = document.getElementById('sound-subtitle');
    this.playBtn = document.getElementById('play-btn');
    this.replayBtn = document.getElementById('replay-btn');
    this.audioElement = document.getElementById('audio-element');
    this.playerStatus = document.getElementById('player-status');
    this.animalsGrid = document.getElementById('animals-grid');

    this.init();
  }

  async init() {
    await this.loadAnimalsData();
    this.renderCatalog();
    this.setupEventListeners();
    this.handleRoute();

    // مدیریت بازگشت تاریخچه مرورگر (Back/Forward)
    window.addEventListener('popstate', () => this.handleRoute());
  }

  async loadAnimalsData() {
    try {
      const response = await fetch('data/animals.json');
      if (!response.ok) throw new Error('Network response not ok');
      this.animals = await response.json();
    } catch (error) {
      console.warn('استفاده از داده‌های پشتیبان حیوانات:', error);
      this.animals = FALLBACK_ANIMALS;
    }
  }

  handleRoute() {
    const params = new URLSearchParams(window.location.search);
    const soundId = params.get('s');

    let targetAnimal = null;
    if (soundId) {
      targetAnimal = this.animals.find(a => a.id.toLowerCase() === soundId.toLowerCase());
    }

    // اگر شناسه‌ای در آدرس نبود، حیوان اول را انتخاب کن
    if (!targetAnimal) {
      targetAnimal = this.animals[0];
    }

    this.selectAnimal(targetAnimal, Boolean(soundId));
  }

  selectAnimal(animal, shouldAutoplay = false) {
    if (!animal) return;
    this.currentAnimal = animal;

    // به‌روزرسانی کارت اصلی
    this.animalEmoji.textContent = animal.emoji;
    this.animalName.textContent = `صدای ${animal.name} ${animal.emoji}`;
    this.soundSubtitle.textContent = `شناسه کیوآرکد: ${animal.id}`;
    document.title = `صدای ${animal.name} | مزرعه حیوانات`;

    // تنظیم منبع صوتی
    this.audioElement.src = animal.audio;
    this.audioElement.load();

    this.updateStatus('آماده برای شنیدن!');
    this.resetPlayButton();

    // علامت‌گذاری کارت فعال در گرید
    this.updateActiveGridCard(animal.id);

    // تلاش برای پخش خودکار در صورت اسکن QR Code
    if (shouldAutoplay) {
      this.attemptAutoplay();
    }
  }

  attemptAutoplay() {
    this.updateStatus('در حال پخش صدا...');
    const playPromise = this.audioElement.play();

    if (playPromise !== undefined) {
      playPromise
        .then(() => {
          this.setPlayingState(true);
        })
        .catch(() => {
          // مرورگرهای موبایل ممکن است بدون لمس کاربر اجازه پخش خودکار ندهند
          this.setPlayingState(false);
          this.updateStatus('👈 برای شنیدن صدا، دکمه نارنجی را لمس کنید');
        });
    }
  }

  togglePlay() {
    if (!this.currentAnimal) return;

    if (this.isPlaying) {
      this.audioElement.pause();
      this.setPlayingState(false);
      this.updateStatus('پخش متوقف شد');
    } else {
      this.audioElement.currentTime = 0;
      this.audioElement.play()
        .then(() => {
          this.setPlayingState(true);
          this.updateStatus(`صدای ${this.currentAnimal.name} در حال پخش است...`);
        })
        .catch(err => {
          console.error('خطای پخش صوتی:', err);
          this.updateStatus('خطا در پخش فایل صوتی');
        });
    }
  }

  setPlayingState(playing) {
    this.isPlaying = playing;
    const btnText = this.playBtn.querySelector('.btn-text');
    const btnIcon = this.playBtn.querySelector('.btn-icon');

    if (playing) {
      this.playerSection.classList.add('active-play');
      this.playBtn.classList.add('playing');
      btnText.textContent = 'توقف صدا';
      btnIcon.textContent = '⏸️';
      this.replayBtn.style.display = 'none';
    } else {
      this.playerSection.classList.remove('active-play');
      this.playBtn.classList.remove('playing');
      btnText.textContent = 'پخش صدا';
      btnIcon.textContent = '🔊';
    }
  }

  resetPlayButton() {
    this.setPlayingState(false);
    this.replayBtn.style.display = 'none';
  }

  updateStatus(msg) {
    if (this.playerStatus) {
      this.playerStatus.textContent = msg;
    }
  }

  renderCatalog() {
    this.animalsGrid.innerHTML = '';

    this.animals.forEach(animal => {
      const card = document.createElement('button');
      card.className = 'animal-item-card';
      card.setAttribute('role', 'listitem');
      card.setAttribute('aria-label', `انتخاب ${animal.name}`);
      card.dataset.id = animal.id;

      card.innerHTML = `
        <span class="animal-item-emoji">${animal.emoji}</span>
        <span class="animal-item-name">${animal.name}</span>
      `;

      card.addEventListener('click', () => {
        // به‌روزرسانی پارامتر آدرس
        const url = new URL(window.location);
        url.searchParams.set('s', animal.id);
        window.history.pushState({}, '', url);

        this.selectAnimal(animal, true);

        // اسکرول نرم به بالای پلیر در موبایل
        this.playerSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });

      this.animalsGrid.appendChild(card);
    });
  }

  updateActiveGridCard(selectedId) {
    const cards = this.animalsGrid.querySelectorAll('.animal-item-card');
    cards.forEach(card => {
      if (card.dataset.id === selectedId) {
        card.classList.add('selected');
      } else {
        card.classList.remove('selected');
      }
    });
  }

  setupEventListeners() {
    // دکمه پخش اصلی
    this.playBtn.addEventListener('click', () => this.togglePlay());

    // دکمه پخش دوباره
    this.replayBtn.addEventListener('click', () => {
      this.audioElement.currentTime = 0;
      this.togglePlay();
    });

    // رویداد پایان پخش صدا
    this.audioElement.addEventListener('ended', () => {
      this.setPlayingState(false);
      this.replayBtn.style.display = 'inline-block';
      this.updateStatus(`پخش تمام شد! می‌خواهید دوباره گوش بدهید؟ 🐣`);
    });

    // رویداد خطا در پخش صوتی
    this.audioElement.addEventListener('error', (e) => {
      console.error('Audio load error:', e);
      this.setPlayingState(false);
      this.updateStatus('متأسفانه فایل صوتی پیدا نشد یا فرمت آن پشتیبانی نمی‌شود.');
    });
  }
}

// راه‌اندازی پس از بارگذاری سند
document.addEventListener('DOMContentLoaded', () => {
  new FarmAudioApp();
});
