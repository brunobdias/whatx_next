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
  });
