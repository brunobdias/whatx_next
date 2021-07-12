var movie_id;
var list_type;

$(document).ready(function () {
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
    $('.tabs').tabs();
    $('.fixed-action-btn').floatingActionButton();
    $('.modal').modal();
});

/* Animated Checkboxes */
/* src https://codepen.io/jaradlight/pen/IEbKq */
$('.checkbox').click(function () {
    $(this).toggleClass('is-checked');
});

$('#to_watch').click(function () {
    if ($('#edt_to_watch').val() == "on") {
        $('#edt_to_watch').val('off');
    } else {
        $('#edt_to_watch').val('on');
        
        if ($('#edt_watched').val() == "on"){
            $('#edt_watched').val('off');   

            $('#watched').toggleClass('is-checked');
        }
        
        if ($('#edt_liked').val() == "on"){
            $('#edt_liked').val('off');   

            $('#liked').toggleClass('is-checked');
        }
        
        if ($('#edt_favorite').val() == "on"){
            $('#edt_favorite').val('off');   

            $('#favorite').toggleClass('is-checked');
        }
    }
    
});

$('#watched').click(function () {
    if ($('#edt_watched').val() == "on") {
        $('#edt_watched').val('off');
    } else {
        $('#edt_watched').val('on');
        
        if ($('#edt_to_watch').val() == "on"){
            $('#edt_to_watch').val('off');   
                     
            $('#to_watch').toggleClass('is-checked');
        }
    }
});

$("#liked").click(function () {
    if ($('#edt_liked').val() == "on") {
        $('#edt_liked').val('off');
    } else {
        $('#edt_liked').val('on');

        if ($('#edt_watched').val() != "on"){
            $('#edt_watched').val('on');   

            $('#watched').toggleClass('is-checked');
        }

        if ($('#edt_to_watch').val() == "on"){
            $('#edt_to_watch').val('off');   
                     
            $('#to_watch').toggleClass('is-checked');
        }
    }
});

$("#favorite").click(function () {
    if ($('#edt_favorite').val() == "on") {
        $('#edt_favorite').val('off');
    } else {
        $('#edt_favorite').val('on');
        
        if ($('#edt_watched').val() != "on"){
            $('#edt_watched').val('on');   

            $('#watched').toggleClass('is-checked');
        }
        
        if ($('#edt_to_watch').val() == "on"){
            $('#edt_to_watch').val('off');   
                     
            $('#to_watch').toggleClass('is-checked');
        }
    }
});

$(".trigger-modal-delete").click(function () {
    var title = '<mark>' + $(this)
        .closest('li') // goes up in the tree to closest li
        .find('.title').html() + // then back to .title and get content
        '</mark>';
    var imgURL = $(this)
        .closest('li')
        .find('.img-path').attr('src');
    movie_id = $(this)
        .closest('li')
        .find('#movie_id').attr('name');
    $(".modal-title").html(title);
    $(".modal-img").attr('src', imgURL);     
    $(".modal-footer").html(`<a href="#!" class="modal-close waves-effect waves-green btn">Cancel</a> 
        <a id="delete-btn" href="/delete_movie/${movie_id}" 
        class="modal-close waves-effect waves-red btn red lighten-3 delete-btn">Delete</a>`)
});


$('#search_bar').keypress(function(event){

    var keycode = (event.keyCode ? event.keyCode : event.which);
    if(keycode == '13'){
        var query = $.trim($('#search_bar').val());
        window.location.href = '/search_results/search/multi/' + query ;
    }

});