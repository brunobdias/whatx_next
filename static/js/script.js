$(document).ready(function(){
    $('.dropdown-trigger').dropdown();
    $('.sidenav').sidenav();
    $('.tooltipped').tooltip();
    $('.carousel').carousel({
        dist: -50,
        numVisible: 20,
        indicators: false,
        padding: 100
    });
    $('.collapsible').collapsible();
  });