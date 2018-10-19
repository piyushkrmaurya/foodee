
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (settings.type == 'POST' || settings.type == 'PUT' || settings.type == 'DELETE') {
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    }
});


function toggleFav(div, dish_id){
    $.ajax({
            type: "POST",
            url: "/toggle_fav/"+dish_id,
    }).done(function(){
        $(div).toggleClass("fav");
    });
}

function addToCart(div, dish_id){
    $.ajax({
            type: "POST",
            url: "/add_to_cart/"+dish_id,
    }).done(function(){
        $(div).removeClass("cart");
        $(div).addClass("incart");
    });
}

function removeFromCart(div, dish_id){
    $.ajax({
            type: "POST",
            url: "/remove_from_cart/"+dish_id,
    }).done(function(){
        $(div).parent().parent().fadeOut('slow', function() {
            $(div).parent().parent().remove();
            $("#cart").load(" #cart");
        });
    });
}

function changeQuantity(dish_id, div){
    $.ajax({
            type: "POST",
            url: "/change_quantity/"+dish_id+"/"+div.value,
    }).done(function(){
        $("#cart").load(" #cart");
    });
}

function orderNow(){
    $.ajax({
            type: "POST",
            url: "/order_now/"
    }).done(function(){
        $("#cart").html("<div class='alert alert-success'><h3>Order placed Successfully!</h3></div>");
    });
}

