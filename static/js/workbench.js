/**
 * Created by brandon on 3/3/17.
 */

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
    jQuery('#my-tank-link').css("border-right-style", "none");
    jQuery('#my-tank-link').css("background-color", "lightgray");
    jQuery('my-tank').show();
});

function show(s){
    jQuery('.inner').css("border-right-style", "solid");
    jQuery('.inner').css("background-color", "darkgray");
    jQuery(s + '-link').css("border-right-style", "none");
    jQuery(s + '-link').css("background-color", "lightgray");
    jQuery('.nav-window').hide();
    jQuery(s).show();
}
