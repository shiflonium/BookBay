$(document).ready(function ()
{
	$("#clientSubmit").click(function()
	{
	//VALIDATE CLIENT BEFORE ADDING TO THE DB
		$.ajax(
		{
			url:'/_pc_man/',
			method:'POST',
			data:
			{
				clientName:$('input[id=clientName]').val(),
				clientUsername:$('input[id=clientUsername]').val(),
				clientPassword:$('input[id=clientPassword]').val(),
				clientIP:$('input[id=clientIP]').val(),
				clientPort:$('input[id=clientPort]').val(),
				clientOS:$('#clientOS').val()
			},
			success:function(data)
			{
					//Set ip error message
				if (data.ip_err_msg != "")
				{
					$("#ipErrorMsg").text(data.ip_err_msg);
				}
				else if (data.general_err != "")
				{
					$("#ipErrorMsg").text(data.general_err);
				} 
				else
				{
					$("#ipErrorMsg").text('');
				}

				//Set port error message
				if (data.port_err_msg != "")
				{
					$("#portErrorMsg").text(data.port_err_msg);
				}
				else
				{
					$("#portErrorMsg").text('');
				}
				if (data.success_msg == '0')
				{
					$("#clientSuccessSpan").text('Client added successfuly.')
				}
				else
				{
					$("#clientSuccessSpan").text('')
				}
			}

		});
	});

	
	
	//adds a software to the database
	$("#swSubmit").click(function()
	{
		$.ajax({
			url:'/_pc_man_add_sw/',
			method:'POST',
			data:
			{
				softwareName:$("#softwareName").val(),
				clientName:$("#softwareClient").val(),
				softwarePath:$("#softwarePath").val()
			},
			success:function(data)
			{
					if (data.err_msg == "")
				{
					$("#swSuccessSpan").text('Software added successfuly');
					$("#swSuccessSpan").css({'color':'GREEN'});
				}

				else
				{
					$("#swSuccessSpan").text(data.err_msg);
					$("#swSuccessSpan").css({'color':'RED'});
				}
			}
		});
	});
	// 	$.getJSON('/_pc_man_add_sw',
	// 	{
	// 		softwareName:$("#softwareName").val(),
	// 		clientName:$("#softwareClient").val(),
	// 		softwarePath:$("#softwarePath").val()
	// 	},
	// 	function(data)
	// 	{
	// 		if (data.err_msg == "")
	// 		{
	// 			$("#swSuccessSpan").text('Software added successfuly');
	// 			$("#swSuccessSpan").css({'color':'GREEN'});
	// 		}

	// 		else
	// 		{
	// 			$("#swSuccessSpan").text(data.err_msg);
	// 			$("#swSuccessSpan").css({'color':'RED'});
	// 		}

	// 	});

		
	// });


	//Enables and disables the software version dropdown list
	$("#softwareClient").change(function()
	{
		$.ajax({
			url:'/_pc_man_sw/',
			method:'POST',
			data:
			{
				clientName:$("#softwareClient").val()
			},
			success:function(data)
			{
				if (data.os == "WINDOWS")
				{
					$("#softwarePath").attr('disabled',true);
				}
				else
				{
					$("#softwarePath").attr('disabled',false);	
				}
			}
		});
	});
});
