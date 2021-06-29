$(document).ready(function(){
    $('.dropdown-trigger').dropdown();
    $('.sidenav').sidenav();
    $('.carousel').carousel({
        dist: -50,
        numVisible: 15,
        indicators: false,
        padding: 100
    });
    $('.tooltipped').tooltip();
    $('.collapsible').collapsible();
  });