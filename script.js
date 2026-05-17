// Поиск книг
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
    
    if (title.includes(query) || author.includes(query)) {
      card.style.display = 'block';
    } else {
      card.style.display = 'none';
    }
  });
});

// Поиск по Enter
searchInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') searchButton.click();
});

// Клик по карточке книги
bookCards.forEach(card => {
  card.addEventListener('click', () => {
    const title = card.querySelector('h3').textContent;
    alert(`Открываем книгу: "${title}"`);
  });
});
