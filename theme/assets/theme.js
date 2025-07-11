// Basis JavaScript - Wordt later uitgebreid
console.log("Theme JavaScript geladen.");

// Voorbeeld: Smooth scroll voor ankerlinks (als die er zijn)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    document.querySelector(this.getAttribute('href')).scrollIntoView({
      behavior: 'smooth'
    });
  });
});

// Hier komt later de logica voor de pop-up en eventuele animaties.
