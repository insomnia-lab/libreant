function initializePopover(){
$('[data-toggle="popover"]').popover();
}


/*********  custom fields stuff **********/

function validateCustomField(customField) {
key = customField.find('.custom-key input').first();
value = customField.find('.custom-value input').first();
if(key.prop('value') !== "" || value.prop('value') !== ""){
    key.prop('required', true);
    value.prop('required', true);
}else{
    key.prop('required', false);
    value.prop('required', false);
}
}


function addCustomField(animation) {
	newCustomField = $('#templates .custom-field-form').clone();
	newCustomField.find('.remove-custom-field button').bind('click', onRemoveCustomField);
	newCustomField.find('input').bind('input', function(e){
		validateCustomField( $(e.target).parents('.custom-field-form'));
	});

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
		if((elem.name === '') || (elem.tagName === 'button'))
			continue;
		metadata[elem.name] = elem.value;
	}
	// collect custom keys
	$('#custom-metadata .custom-field-form').each(function( index ) {
		key = $(this).find('.custom-key input')[0].value;
		value = $(this).find('.custom-value input')[0].value;
		if(key !== "" && value !== "")
			metadata[key] = value;
	});
	return metadata;
}


/********* Initialization *********/

$('[data-toggle="tooltip"]').tooltip();
initializePopover();
$('#custom-metadata .custom-field-form button').bind('click', onRemoveCustomField);

/******* End Initialization *******/
