function toggleDarkClass() {
  var element = document.getElementById('classedark');
  element.classList.toggle('dark');
  
  // Salva lo stato del tema nel localStorage
  localStorage.setItem('theme', element.classList.contains('dark') ? 'dark' : 'light');
}

function loadTheme() {
  // Leggi lo stato del tema dal localStorage
  const theme = localStorage.getItem('theme');

  // Se il tema è impostato su 'dark', applica la classe dark all'elemento
  if (theme === 'dark') {
      document.documentElement.classList.add('dark');
  }
}

// Aggiungi un event listener per il click sul bottone toggle
document.getElementById('toggleButton').addEventListener('click', toggleDarkClass);

// Carica il tema al caricamento della pagina
window.addEventListener('load', loadTheme);

