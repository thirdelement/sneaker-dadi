// Credit SirNovi post at https://github.com/metafizzy/flickity/issues/534
// Function to resize carousel cards to same height
function setSliderHeightToMax(slider) {
    slider.cells.forEach(cell => cell.element.style.height = '');
        
    let heights = slider.cells.map(cell => cell.element.offsetHeight),
        max = Math.max.apply(Math, heights);
    
    slider.cells.forEach(cell => cell.element.style.height = max + 'px');
  }
  
  // Run function above on ready and on window resize
  var slider = document.querySelector('.carousel');
  var flkty = new Flickity( slider, {
      on: {
          ready: function() {
              setSliderHeightToMax(this);
          }
      }
  });
  
  window.addEventListener('resize', function(){
      setSliderHeightToMax(flkty);
  });