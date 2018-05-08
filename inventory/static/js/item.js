function change_place(){
    var data={
        id_inventory:$('#id_inventory').val(),
    };

    $.ajax(
        {
            url: "/inventory/get_places",
            type: "get",
            data:data,
            dataType: "json",
            error: function(data){
                $('#id_place').find('option').remove().end();
                $('#id_place').append('<option value="">---------</option>');
                $('#id_place_container').hide();
                console.log(data);
            },
            success: function( response ){
                $('select').material_select('destroy');
                $('#id_place').find('option').remove().end();
                $('#id_place').append('<option value="">---------</option>');
                //TODO Remove this line and the get_menu_categories python views?
                response=JSON.parse(response);
                $.each(response, function(i, value) {
                    $('#id_place').append($('<option>').text(value.title).attr('value', value.id));
                });
                $('#id_place_container').show();

                $('select').material_select();
            }

        }

    );


}

function change_category(){
    var data={
        id_inventory:$('#id_inventory').val(),
    };

    $.ajax(
        {
            url: "/inventory/get_categories",
            type: "get",
            data:data,
            dataType: "json",
            error: function(data){
                $('#id_category').find('option').remove().end();
                $('#id_category').append('<option value="">---------</option>');
                $('#id_category_container').hide();
                console.log(data);
            },
            success: function( response ){
                $('select').material_select('destroy');
                $('#id_category').find('option').remove().end();
                $('#id_category').append('<option value="">---------</option>');
                //TODO Remove this line and the get_menu_categories python views?
                response=JSON.parse(response);
                $.each(response, function(i, value) {
                    $('#id_category').append($('<option>').text(value.title).attr('value', value.id));
                });
                $('#id_category_container').show();

                $('select').material_select();
            }

        }

    );


}


$(document).on('ready',function(){

    $('html body main div.row.change-form div.col.s12.m12.l3 div.card.actions-card div.card-content span.card-title.black-text').append('<div class="row" id="acciones"></div>')
    $('#acciones').append('<button type="submit" id="btn_imprimir_item" class="btn btn-primary" title="Ejecutar la acción seleccionada" name="index" value="0">Imprimir detalle</button>');

    $('#change_id_inventory').hide();
    $('#change_id_place').hide();
    $('#change_id_category').hide();
    $('#add_id_inventory').hide();
    $('#add_id_place').hide();
    $('#add_id_category').hide();

    //Cuando estoy creando oculto categoria y lugar
    if (!(parseInt($('#id_inventory').val())>0)){
        $('#id_category_container').hide();
        $('#id_place_container').hide();
    }

    $('#id_inventory').on('change', function(e){
        change_category();
        change_place();
    });

    $('#btn_imprimir_item').on('click', function(e){
        console.log('Buscamos para imprimir el item')
    })

});
