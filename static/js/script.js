$(document).ready(function(){
    if ($(window).width() < 470) {
        $('.carousel').carousel({
        });
    } else {  
        $('.carousel').carousel({
            dist: -50,
            numVisible: 20,
            indicators: false,
            padding: 100
        });
    }
    $('.dropdown-trigger').dropdown();
    $('.sidenav').sidenav();
    $('.tooltipped').tooltip();
    $('.collapsible').collapsible();
    $('.fixed-action-btn').floatingActionButton();
  });

  /* Animated Checkboxes */
  /* src https://codepen.io/jaradlight/pen/IEbKq */
  $('.checkbox').click(function(){
    $(this).toggleClass('is-checked');
  });
