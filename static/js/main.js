$(document).ready(function(){
    console.info("DOM is now ready");
    initTags();
});

function initTags() {
    $(document).on('click', '.toadd .tag',function(){
        var value = $(this).text();
        var $selected = $('input[name="selected"]');
        var selection = cleanArray($selected.val().split(","));
        var index = $.inArray(value, selection);
        if (index === -1) {
            var tag = '<span class="tag">'+
                value + '<span class="typicons-times"></span>'+
                '</span>';
            selection.push(value);
            $selected.val(selection.join(","));
            $('.toremove').append(tag);
        }
    });

    $(document).on('click', '.toremove .tag', function(){
        var $selected = $('input[name="selected"]');
        var value = $(this).text();
        var selection = cleanArray($selected.val().split(","));
        var index = $.inArray(value, selection);
        if (index >= -1) {
			selection.splice(index, 1);
            $selected.val(selection.join(","));
		}
        $(this).remove();
    });

    $('input#query').bind('typeahead:selected', function(e, obj) {
        var $selected = $('input[name="selected"]');
        var selection = cleanArray($selected.val().split(","));
        var index = $.inArray(obj.name, selection);
        if (index === -1) {
            var tag = '<span class="tag">'+
                obj.name + '<span class="typicons-times"></span>'+
                '</span>';
            selection.push(obj.name);
            $selected.val(selection.join(","));
            $('.toremove').append(tag);
        }
        setTimeout(function(){
            $('input#query').val("");
        });
    });

    $(document).on('blur', 'input#query', function(){
        setTimeout(function(){
            $('input#query').val("");
        });
    });

    // Initialize date fields
    var picker = new Pikaday({ field: $('input#start_date')[0] });
    var picker = new Pikaday({
        field: $('input#end_date')[0],
        onSelect: function(date){
            console.log(date);
        },
    });
}

function cleanArray(actual) {
	var newArray = new Array();
	for (var i = 0; i < actual.length; i++) {
		if (actual[i]) {
			newArray.push(actual[i]);
		}
	}
	return newArray;
}
