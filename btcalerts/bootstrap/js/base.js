$(document).ready(function(){	
	$('input:radio[name=delivery_type]').click(function(){
		var value = $(this).val();
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
		else
		    {
			console.log("neither");
		    }
	    });
    });
