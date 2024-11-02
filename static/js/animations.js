// Enhanced animations and transitions
document.addEventListener('DOMContentLoaded', () => {
    // Initialize smooth scrolling
    initSmoothScroll();
    
    // Initialize fade animations
    initFadeAnimations();
    
    // Initialize hover effects
    initHoverEffects();
    
    // Initialize image lazy loading
    initLazyLoading();
});

// Smooth scrolling implementation
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Enhanced fade animations
function initFadeAnimations() {
    const fadeElements = document.querySelectorAll('.fade-in, .fade-in-up');
    
    const fadeOptions = {
        threshold: 0.1,
        rootMargin: '0px'
    };
    
    const fadeObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                if (entry.target.classList.contains('fade-in-up')) {
                    entry.target.style.transform = 'translateY(0)';
                    entry.target.style.opacity = '1';
                } else {
                    entry.target.classList.add('visible');
                }
                observer.unobserve(entry.target);
            }
        });
    }, fadeOptions);
    
    fadeElements.forEach(element => {
        if (element.classList.contains('fade-in-up')) {
            element.style.transform = 'translateY(20px)';
            element.style.opacity = '0';
            element.style.transition = 'transform 0.6s ease-out, opacity 0.6s ease-out';
        }
        fadeObserver.observe(element);
    });
}

// Enhanced hover effects
function initHoverEffects() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', () => {
            link.style.transform = 'translateX(10px)';
        });
        
        link.addEventListener('mouseleave', () => {
            link.style.transform = 'translateX(0)';
        });
    });
}

// Lazy loading for images
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageOptions = {
        threshold: 0.1,
        rootMargin: '50px'
    };
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    }, imageOptions);
    
    images.forEach(img => imageObserver.observe(img));
}

// Add smooth page transitions
document.querySelectorAll('a:not([target="_blank"])').forEach(link => {
    link.addEventListener('click', e => {
        if (link.href.startsWith(window.location.origin)) {
            e.preventDefault();
            document.body.style.opacity = '0';
            document.body.style.transition = 'opacity 0.3s ease';
            
            setTimeout(() => {
                window.location = link.href;
            }, 300);
        }
    });
});

// Add smooth fade-in on page load
window.addEventListener('load', () => {
    document.body.style.opacity = '1';
    document.body.style.transition = 'opacity 0.3s ease';
});
