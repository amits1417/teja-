document.addEventListener('DOMContentLoaded', function(){
  var toggle = document.getElementById('navToggle');
  var nav = document.querySelector('.main-nav');
  if(toggle && nav){
    toggle.addEventListener('click', function(){ nav.classList.toggle('open'); });
  }
});
