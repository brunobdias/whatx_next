$(document).ready(function(){
    $('.dropdown-trigger').dropdown();
    $('.sidenav').sidenav();
    $('.carousel').carousel({
        dist: -50,
        numVisible: 15,
        indicators: true,
        padding: 100,
        pressed: false
    });
    $('.tooltipped').tooltip();
    $('.collapsible').collapsible();
  });