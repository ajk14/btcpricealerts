var firstClick = 1;

function updateMessages(value)
{
    if (value == "EMAIL")
	{
	    $("#text_message")[0].style.display='none';
	    $("#email_message")[0].style.display='block';
	}
    else if (value == "SMS")
	{
	    $('#email_message')[0].style.display='none';
	    $('#text_message')[0].style.display='block';
	}
}

$(document).ready(function(){	
	if($('input:radio[name=delivery_type]').is(':checked'))
	    {
		var value = $('input:radio[name=delivery_type]').val();
		updateMessages(value);
		
	    }
	$('input:radio[name=delivery_type]').click(function(){
		value = $(this).val();
		if (value == "SMS" && firstClick && !PHONE_ACTIVE)
		    {
			firstClick = 0; 
			$('#phoneModal').modal('show');
		    }
		updateMessages($(this).val())
		    });
    });
