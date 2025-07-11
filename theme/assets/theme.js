// Basis JavaScript - Wordt later uitgebreid
console.log("Theme JavaScript geladen.");

document.addEventListener('DOMContentLoaded', function() {

  // Voorbeeld: Smooth scroll voor ankerlinks (als die er zijn)
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const targetElement = document.querySelector(this.getAttribute('href'));
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: 'smooth'
        });
      }
    });
  });

  // Sticky Header Logica
  const header = document.querySelector('.site-header.is-sticky-enabled');
  if (header) {
    let lastScrollTop = 0;
    const headerHeight = header.offsetHeight; // Get initial height

    window.addEventListener('scroll', function() {
      let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

      if (scrollTop > headerHeight + 50) { // Begin met sticky maken na scrollen voorbij de header hoogte + een buffer
        header.classList.add('is-sticky');
      } else {
        header.classList.remove('is-sticky');
      }

      // Optioneel: header verbergen/tonen bij scrollen
      // if (scrollTop > lastScrollTop && scrollTop > headerHeight + 100){ // Scroll down
      //   header.classList.add('site-header--hidden');
      // } else { // Scroll up
      //   header.classList.remove('site-header--hidden');
      // }
      lastScrollTop = scrollTop <= 0 ? 0 : scrollTop; // For Mobile or negative scrolling
    }, false);
  }


  // Dropdown menu toegankelijkheid (basis)
  const navItemsWithDropdown = document.querySelectorAll('.site-nav__item');
  navItemsWithDropdown.forEach(item => {
    const link = item.querySelector('.site-nav__link');
    const dropdown = item.querySelector('.site-nav__dropdown');

    if (dropdown) {
      // Toon/verberg bij focus/blur voor toetsenbordnavigatie
      link.addEventListener('focus', () => {
        // Om te voorkomen dat alle dropdowns openen bij tabben,
        // moeten we controleren of de focus *binnen* dit item is.
        // Dit is een eenvoudige implementatie; een robuustere zou event bubbling/capturing gebruiken.
      });

      // Muis events blijven via CSS :hover afgehandeld.
      // Je kunt hier JS toevoegen voor click-to-open op mobiel indien nodig.
    }
  });


  // Hier komt later de logica voor de pop-up en eventuele animaties.


  // Nieuwsbrief Pop-up Logica
  const newsletterPopup = document.getElementById('newsletterPopup');
  if (newsletterPopup && newsletterPopup.style.display !== 'flex') { // Controleer of het niet al getoond is (bijv. na form submit error)
    const popupDelay = parseInt(newsletterPopup.dataset.delay || '5', 10) * 1000; // in milliseconden
    const closeButton = newsletterPopup.querySelector('.newsletter-popup__close');
    const noThanksButton = newsletterPopup.querySelector('.newsletter-popup__no-thanks');
    const popupFormShopify = newsletterPopup.querySelector('.newsletter-popup__form-shopify form');

    const showPopup = () => {
      newsletterPopup.style.display = 'flex';
      // Optioneel: body scroll lock
      // document.body.style.overflow = 'hidden';
    };

    const hidePopup = (setCookie = true) => {
      newsletterPopup.style.display = 'none';
      // document.body.style.overflow = ''; // Herstel scroll
      if (setCookie) {
        // Zet een cookie om de pop-up niet opnieuw te tonen voor X dagen
        const expiryDate = new Date();
        expiryDate.setDate(expiryDate.getDate() + 30); // Toon niet voor 30 dagen
        document.cookie = `newsletterPopupDismissed=true; expires=${expiryDate.toUTCString()}; path=/; SameSite=Lax`;
      }
    };

    // Controleer of de pop-up al eerder is gesloten
    if (!document.cookie.includes('newsletterPopupDismissed=true')) {
      setTimeout(showPopup, popupDelay);
    }

    if (closeButton) {
      closeButton.addEventListener('click', () => hidePopup());
    }
    if (noThanksButton) {
        noThanksButton.addEventListener('click', () => hidePopup());
    }


    // Als het Shopify formulier succesvol is, sluit ook de popup en zet cookie
    if (popupFormShopify) {
        // We kunnen niet direct zien of het formulier succesvol was zonder de pagina te herladen
        // of complexere AJAX. Voor nu, als het formulier bestaat, en de gebruiker het submit,
        // sluiten we het. Een betere UX zou zijn om de pagina te herladen met een succesbericht.
        // Of, als het formulier via AJAX wordt gesubmit (niet standaard in dit thema), dan
        // kan de `hidePopup` na een succesvolle AJAX call worden aangeroepen.

        // Als er een succesbericht is van een vorige submit (pagina herladen), sluit niet automatisch.
        const successMessage = popupFormShopify.querySelector('.form-success');
        if (successMessage && successMessage.offsetParent !== null) { // if success message is visible
            // Doe niets, laat de gebruiker het succes zien.
            // De popup blijft dan open tot handmatig gesloten.
        }
    }


    // Klikken buiten de pop-up content sluit het ook
    newsletterPopup.addEventListener('click', function(event) {
      if (event.target === newsletterPopup.querySelector('.newsletter-popup__overlay')) {
        hidePopup();
      }
    });

    // ESC toets sluit de pop-up
    document.addEventListener('keydown', function(event) {
      if (event.key === 'Escape' && newsletterPopup.style.display === 'flex') {
        hidePopup();
      }
    });
  }

  // Fade-in secties bij scrollen
  const sectionsToFade = document.querySelectorAll('.section-fade-in');
  if (sectionsToFade.length > 0) {
    const observerOptions = {
      root: null, // ten opzichte van de viewport
      rootMargin: '0px',
      threshold: 0.1 // percentage van het element dat zichtbaar moet zijn
    };

    const observerCallback = (entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target); // Stop met observeren na zichtbaar worden
        }
      });
    };

    const intersectionObserver = new IntersectionObserver(observerCallback, observerOptions);
    sectionsToFade.forEach(section => {
      intersectionObserver.observe(section);
    });
  }

});
