function initializePopover(){
    $('[data-toggle="popover"]').popover();
}


/*********  custom fields stuff **********/


function clearEmptyInput(e){
    if(e.target.value.trim() === '')
        e.target.value = '';
}

function validateCustomKeysRepetition() {

	var counts = {};

    function inc(key){
        if(counts.hasOwnProperty(key))
            counts[key]++;
        else
            counts[key] = 1;
    }

    // collect presets
    elements = document.getElementById('mega-form').elements;
	for(var i = 0; i < elements.length; i++)
        inc(elements[i].name.trim());

    customKeys = $('#custom-metadata .custom-field-form .custom-key input');

    // collect custom keys
    customKeys.each(function(index, elem) {
        inc(elem.value.trim());
    });

    customKeys.each(function(index, elem) {
        validityMessage = "";
        value = elem.value.trim();
        if(value){
            if(value.startsWith('_'))
                validityMessage = "Key cannot stats with underscore";
            if(counts[value] > 1)
                validityMessage = "Key used more than once";
        }

        if(validityMessage == ""){
            elem.setCustomValidity("");
            $(elem).parent().removeClass('has-error');
        } else {
            elem.setCustomValidity(validityMessage);
            $(elem).parent().addClass('has-error');
        }
    });
}

function validateCustomField(customField) {
    key = customField.find('.custom-key input').get(0);
    value = customField.find('.custom-value input').get(0);
    if(key.value.trim() != "" || value.value.trim() != ""){
        key.setAttribute('required', 'true');
        value.setAttribute('required', 'true');
    }else{
        key.removeAttribute('required');
        value.removeAttribute('required');
    }
}


function addCustomField(animation) {
	newCustomField = $('#templates .custom-field-form').clone();
	bindCustomField(newCustomField);

	if(animation){
		newCustomField.hide();
		$('#custom-metadata').append(newCustomField);
		newCustomField.slideDown('fast');
	}else{
		$('#custom-metadata').append(newCustomField);
	}
}


function onRemoveCustomField(e) {
	customField = $(e.target).parents('.custom-field-form').first();
	customField.slideUp('fast', function (){
		this.remove();
	});
}

function bindCustomField(customField) {
	customField.find('.remove-custom-field button').bind('click', onRemoveCustomField);
    customField.find('.custom-key input').bind('input', validateCustomKeysRepetition);
    customField.find('input').bind('input', function(e){
		validateCustomField( $(e.target).parents('.custom-field-form'));
	});
    customField.find('input').focusout(clearEmptyInput);
}

function bindAllCustomFields() {
    $('#custom-metadata .custom-field-form').each(function() {
         bindCustomField($(this));
    });
}

/*********  end custom fields stuff **********/


function submitFormHandler(){
	metadata = collectMetadata();
	$.ajax({
		type: "PUT",
		url: $('#mega-form')[0].action,
		data: JSON.stringify(metadata),
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		success: function(data){
			exitUpdatingMode();
			showSuccessModal();
		},
		error: function(errMsg) {
			exitUpdatingMode();
			showErrorModal();
		}
	});

	enterUpdatingMode();
}

function showSuccessModal(){
	m = $('#success-modal').modal();
	m.modal('toogle');
}

function showErrorModal(){
	m = $('#error-modal').modal();
	m.modal('toogle');
}

function enterUpdatingMode(){
	$('#submit-button').hide();
	$('#updating-button').show();
}

function exitUpdatingMode(){
	$('#updating-button').hide();
	$('#submit-button').show();
}

function collectMetadata(){
	metadata = {};
	elements = document.getElementById('mega-form').elements;
	for(var i = 0; i < elements.length; i++){
		elem = elements[i];
		kname = elem.name.trim()
        if((kname === '') || (elem.tagName === 'button'))
			continue;
		metadata[kname] = elem.value.trim();
	}
	// collect custom keys
	$('#custom-metadata .custom-field-form').each(function( index ) {
		key = $(this).find('.custom-key input')[0].value.trim();
		value = $(this).find('.custom-value input')[0].value.trim();
		if(key !== "" && value !== "")
			metadata[key] = value;
	});
	return metadata;
}



/********* Initialization *********/

$('[data-toggle="tooltip"]').tooltip();
initializePopover();
bindAllCustomFields();

/******* End Initialization *******/
