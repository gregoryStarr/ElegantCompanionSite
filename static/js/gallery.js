// Lightbox Gallery Implementation
class Gallery {
    constructor() {
        this.images = document.querySelectorAll('.gallery-item img');
        this.lightbox = this.createLightbox();
        this.bindEvents();
    }

    createLightbox() {
        const lightbox = document.createElement('div');
        lightbox.className = 'lightbox';
        lightbox.innerHTML = `
            <div class="lightbox-content">
                <img src="" alt="">
                <button class="close">&times;</button>
                <button class="prev">&lt;</button>
                <button class="next">&gt;</button>
            </div>
        `;
        document.body.appendChild(lightbox);
        return lightbox;
    }

    bindEvents() {
        this.images.forEach((img, index) => {
            img.addEventListener('click', () => this.openLightbox(index));
        });

        this.lightbox.querySelector('.close').addEventListener('click', () => {
            this.lightbox.style.display = 'none';
        });

        this.lightbox.querySelector('.prev').addEventListener('click', () => {
            this.currentIndex = (this.currentIndex - 1 + this.images.length) % this.images.length;
            this.updateLightboxImage();
        });

        this.lightbox.querySelector('.next').addEventListener('click', () => {
            this.currentIndex = (this.currentIndex + 1) % this.images.length;
            this.updateLightboxImage();
        });
    }

    openLightbox(index) {
        this.currentIndex = index;
        this.lightbox.style.display = 'flex';
        this.updateLightboxImage();
    }

    updateLightboxImage() {
        const img = this.lightbox.querySelector('img');
        img.src = this.images[this.currentIndex].src;
        img.alt = this.images[this.currentIndex].alt;
    }
}

// Initialize gallery when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Gallery();
});
