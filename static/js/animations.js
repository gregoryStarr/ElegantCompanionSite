// Smooth fade-in animation for page elements
document.addEventListener('DOMContentLoaded', () => {
    const fadeElements = document.querySelectorAll('.fade-in');
    
    const fadeInOptions = {
        threshold: 0.1,
        rootMargin: '0px'
    };

    const fadeInObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, fadeInOptions);

    fadeElements.forEach(element => {
        fadeInObserver.observe(element);
    });

    // Smooth navigation transitions
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', e => {
            if (link.href.startsWith(window.location.origin)) {
                e.preventDefault();
                document.body.style.opacity = 0;
                setTimeout(() => {
                    window.location = link.href;
                }, 300);
            }
        });
    });
});

// Add smooth fade-in on page load
window.addEventListener('load', () => {
    document.body.style.opacity = 1;
});
