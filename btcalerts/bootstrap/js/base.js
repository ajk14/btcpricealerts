$(document).ready(function(){	
	$('input:radio[name=delivery_type]').click(function(){
		var value = $(this).val();
		if (value == "EMAIL")
		    {
			console.log("EMAIL");
		    }
		else if (value == "SMS")
		    {
			console.log("SMS");
		    }
		else
		    {
			console.log("neither");
		    }
	    });
    });
