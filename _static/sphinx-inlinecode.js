document.addEventListener("DOMContentLoaded", (event) => {
  document.querySelectorAll('details.sphinx-inlinecode').forEach(detail => {
    detail.addEventListener('toggle', function () {
      const dtElement = this.parentNode;
      if (this.open) {
        // When <details> is open, expand the <dt> to full width
        dtElement.style.maxWidth = '100%';
      } else {
        // When <details> is closed, set the <dt> width back to default
        dtElement.style.maxWidth = 'fit-content';
      }
    });
  });
});
