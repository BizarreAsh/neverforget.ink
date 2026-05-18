const translations = {
  ru: {
    nav_catalog:        'Каталог',
    nav_genres:         'Жанры',
    nav_favorites:      'Избранное',
    nav_about:          'О нас',
    hero_title:         'Читай. Сохраняй. Не забывай.',
    hero_subtitle:      'Тысячи книг в одном месте — бесплатно и навсегда',
    search_placeholder: 'Поиск книги или автора...',
    search_btn:         'Найти',
    section_ru:         'Книги на русском',
    section_en:         'Книги на английском',
    section_de:         'Книги на немецком',
    footer_text:        '© 2026 NeverForget.ink — Все права защищены',
    book_open:          'Открываем книгу',
    about_p1:           'NeverForget — это библиотека коротких историй, которые остаются с тобой навсегда.',
    about_p2:           'Каждая книга здесь — это три главы и десять минут твоего времени. Не больше. Но достаточно, чтобы почувствовать что-то настоящее.',
    about_p3:           'Биографии реальных людей, истории любви, игры судьбы, события которые меняют всё — жанры разные, но цель одна: подарить эмоцию. Ту самую, которую не забываешь.',
    about_p4:           'Библиотека живёт на трёх языках — потому что эмоции не знают границ.',
    about_p5:           'NeverForget. Потому что такие истории не забываются.',
  },
  en: {
    nav_catalog:        'Catalog',
    nav_genres:         'Genres',
    nav_favorites:      'Favorites',
    nav_about:          'About',
    hero_title:         'Read. Save. Never Forget.',
    hero_subtitle:      'Thousands of books in one place — free forever',
    search_placeholder: 'Search for a book or author...',
    search_btn:         'Search',
    section_ru:         'Russian Books',
    section_en:         'English Books',
    section_de:         'German Books',
    footer_text:        '© 2026 NeverForget.ink — All rights reserved',
    book_open:          'Opening book',
    about_p1:           'NeverForget is a library of short stories that stay with you forever.',
    about_p2:           'Every book here is three chapters and ten minutes of your time. No more. But enough to feel something real.',
    about_p3:           'Biographies of real people, love stories, twists of fate, events that change everything — the genres vary, but the goal is one: to give you an emotion. The kind you don\'t forget.',
    about_p4:           'The library lives in three languages — because emotions know no borders.',
    about_p5:           'NeverForget. Because stories like these are never forgotten.',
  },
  de: {
    nav_catalog:        'Katalog',
    nav_genres:         'Genres',
    nav_favorites:      'Favoriten',
    nav_about:          'Über uns',
    hero_title:         'Lesen. Speichern. Nie vergessen.',
    hero_subtitle:      'Tausende Bücher an einem Ort — kostenlos und für immer',
    search_placeholder: 'Buch oder Autor suchen...',
    search_btn:         'Suchen',
    section_ru:         'Russische Bücher',
    section_en:         'Englische Bücher',
    section_de:         'Deutsche Bücher',
    footer_text:        '© 2026 NeverForget.ink — Alle Rechte vorbehalten',
    book_open:          'Buch wird geöffnet',
    about_p1:           'NeverForget ist eine Bibliothek kurzer Geschichten, die für immer bei dir bleiben.',
    about_p2:           'Jedes Buch hier besteht aus drei Kapiteln und zehn Minuten deiner Zeit. Nicht mehr. Aber genug, um etwas Echtes zu spüren.',
    about_p3:           'Biografien realer Menschen, Liebesgeschichten, Schicksalswendungen, Ereignisse, die alles verändern — die Genres sind verschieden, aber das Ziel ist eines: dir eine Emotion zu schenken. Eine, die du nicht vergisst.',
    about_p4:           'Die Bibliothek lebt in drei Sprachen — weil Emotionen keine Grenzen kennen.',
    about_p5:           'NeverForget. Weil solche Geschichten nicht vergessen werden.',
  },
};

let currentLang = 'ru';

const langBtns = document.querySelectorAll('.lang-btn');
const i18nEls  = document.querySelectorAll('[data-i18n], [data-i18n-placeholder]');

function setLanguage(lang) {
  currentLang = lang;
  document.documentElement.lang = lang;

  const t = translations[lang];
  i18nEls.forEach(el => {
    if (el.dataset.i18n)            el.textContent = t[el.dataset.i18n]            ?? el.textContent;
    if (el.dataset.i18nPlaceholder) el.placeholder = t[el.dataset.i18nPlaceholder] ?? el.placeholder;
  });

  langBtns.forEach(btn => btn.classList.toggle('active', btn.dataset.lang === lang));
}

langBtns.forEach(btn => btn.addEventListener('click', () => setLanguage(btn.dataset.lang)));

const searchInput  = document.querySelector('.hero input');
const searchButton = document.querySelector('.hero button');
const bookCards    = document.querySelectorAll('.book-card');

const cardData = Array.from(bookCards).map(card => {
  const displayTitle = card.querySelector('h3').textContent;
  return {
    el: card,
    title:        displayTitle.toLowerCase(),
    author:       card.querySelector('p').textContent.toLowerCase(),
    displayTitle,
  };
});

function runSearch() {
  const query = searchInput.value.toLowerCase().trim();
  cardData.forEach(({ el, title, author }) => {
    el.style.display = (!query || title.includes(query) || author.includes(query)) ? 'block' : 'none';
  });
}

searchButton.addEventListener('click', runSearch);
searchInput.addEventListener('keydown', e => { if (e.key === 'Enter') runSearch(); });

cardData.forEach(({ el, displayTitle }) => {
  el.addEventListener('click', () => alert(`${translations[currentLang].book_open}: "${displayTitle}"`));
});

const aboutModal = document.getElementById('about-modal');

document.querySelector('[data-i18n="nav_about"]').addEventListener('click', e => {
  e.preventDefault();
  aboutModal.classList.add('open');
});

aboutModal.addEventListener('click', e => {
  if (e.target === aboutModal) aboutModal.classList.remove('open');
});

document.querySelector('.modal-close').addEventListener('click', () => {
  aboutModal.classList.remove('open');
});

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') aboutModal.classList.remove('open');
});
