// Translations
const translations = {
  ru: {
    nav_catalog:    'Каталог',
    nav_genres:     'Жанры',
    nav_favorites:  'Избранное',
    nav_about:      'О нас',
    hero_title:     'Читай. Сохраняй. Не забывай.',
    hero_subtitle:  'Тысячи книг в одном месте — бесплатно и навсегда',
    search_placeholder: 'Поиск книги или автора...',
    search_btn:     'Найти',
    popular_title:  'Популярные книги',
    footer_text:    '© 2026 NeverForget.ink — Все права защищены',
    book_open:      'Открываем книгу',
  },
  en: {
    nav_catalog:    'Catalog',
    nav_genres:     'Genres',
    nav_favorites:  'Favorites',
    nav_about:      'About',
    hero_title:     'Read. Save. Never Forget.',
    hero_subtitle:  'Thousands of books in one place — free forever',
    search_placeholder: 'Search for a book or author...',
    search_btn:     'Search',
    popular_title:  'Popular Books',
    footer_text:    '© 2026 NeverForget.ink — All rights reserved',
    book_open:      'Opening book',
  },
  de: {
    nav_catalog:    'Katalog',
    nav_genres:     'Genres',
    nav_favorites:  'Favoriten',
    nav_about:      'Über uns',
    hero_title:     'Lesen. Speichern. Nie vergessen.',
    hero_subtitle:  'Tausende Bücher an einem Ort — kostenlos und für immer',
    search_placeholder: 'Buch oder Autor suchen...',
    search_btn:     'Suchen',
    popular_title:  'Beliebte Bücher',
    footer_text:    '© 2026 NeverForget.ink — Alle Rechte vorbehalten',
    book_open:      'Buch wird geöffnet',
  },
};

let currentLang = 'ru';

function setLanguage(lang) {
  currentLang = lang;
  document.documentElement.lang = lang;

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    if (translations[lang][key]) el.textContent = translations[lang][key];
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.dataset.i18nPlaceholder;
    if (translations[lang][key]) el.placeholder = translations[lang][key];
  });

  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });
}

// Language switcher
document.querySelectorAll('.lang-btn').forEach(btn => {
  btn.addEventListener('click', () => setLanguage(btn.dataset.lang));
});

// Book search
const searchInput = document.querySelector('.hero input');
const searchButton = document.querySelector('.hero button');
const bookCards = document.querySelectorAll('.book-card');

searchButton.addEventListener('click', () => {
  const query = searchInput.value.toLowerCase().trim();

  if (query === '') {
    bookCards.forEach(card => card.style.display = 'block');
    return;
  }

  bookCards.forEach(card => {
    const title = card.querySelector('h3').textContent.toLowerCase();
    const author = card.querySelector('p').textContent.toLowerCase();
    card.style.display = (title.includes(query) || author.includes(query)) ? 'block' : 'none';
  });
});

searchInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') searchButton.click();
});

// Book card click
bookCards.forEach(card => {
  card.addEventListener('click', () => {
    const title = card.querySelector('h3').textContent;
    alert(`${translations[currentLang].book_open}: "${title}"`);
  });
});
