function validation_rules(transfer_limit_usd,transfer_minimum_usd){
    $("#send_money_form").validate({
    rules:{
      receiver_number:{
      required:true,
      digits: true,
      min:0000000,
      max:9999999,
			minlength:7,
			maxlength:7
			},
      receiver_fname:{
        required:true
      },
       receiver_lname:{
          required:true
      },
      phonenumber_ext_verify: {
      required:true, 
      equalTo:'#phonenumber_ext'
      },
      verify_receiver_number: {
      required:true, 
      equalTo:'#receiver_number'
      },
      amount_sent:{
      required:true,
      digits: true,
      max:transfer_limit_usd,
      minlength:1,
      maxlength:6,
      min:transfer_minimum_usd
      },
       mobile_reason:{
      maxlength:50
      },
		},
      messages: {
          verify_receiver_number: {
          required: "Please verify the Phonenumber",
          equalTo:"The phone number's you provided don't match"
          },
			receiver_number: {
			required: "Please provide a phonenumber",
			digits:"Please provide a valid 7 digit phonenumber",
			minlength: "Please provide a valid 7 digit phonenumber",
      maxlength: "Please provide a valid 7 digit phonenumber",
      min: "Please provide a valid 7 digit phonenumber",
      max: "Please provide a valid 7 digit phonenumber",
			},
      receiver_fname:{
        required:"Please provide the recipient's first name"
      },
       receiver_lname:{
          required:"Please provide the recipient's last name"
      },
      total:
      {
        min : "You Cannot Transfer An Amount less than " + transfer_minimum_usd,
        max : "You Cannot Transfer An Amount More than " + transfer_limit_usd,
      }
		}
    
    });
}


function selectPhonenumber(val)
{

var fname = $('option:selected', val).attr('data-fname');
var lname = $('option:selected', val).attr('data-lname');



var ext =  $('option:selected', val).attr('data-ext');
var numba =  $('option:selected', val).attr('data-number');



//alert(ext);
if(numba.length > 0)
{

$('#receiver_fname').val(fname);
$('#receiver_lname').val(lname);

$('#sending_add_to_phonebook').hide();

$('#verify_phonenumber_div').show();

$('#phonenumber_ext').val(ext);
$('#phonenumber_ext_verify').val(ext);


$('#receiver_number').val(numba);
$('#verify_receiver_number').val(numba);
//remove error if any
$('label[for=receiver_number]').html('');
$('#receiver_number').removeClass('error');

}

}


function receiver_phonenumber(){
return $('#phonenumber_ctry').val()+''+$('#phonenumber_ext').val()+''+$('#receiver_number').val();
}

function verification_phonenumber(){
return $('#phonenumber_ctry').val() +''+$('#phonenumber_ext_verify').val()+''+$('#verify_receiver_number').val();
}


function updatePhoneNumberExt(ele){
    var val = $(ele).val();
    if( $(ele).attr("id") === 'phonenumber_ext_verify')
    {
        $('#phonenumber_ext').val(val);
    }else{
        $('#phonenumber_ext_verify').val(val);
    }   
    checkPhonebook();  
}




function verifyPhonenumber()
{
//if($('#send_money_form').validate().checkForm())
if($('#receiver_number').valid())
{  
$('#verify_phonenumber_div').show();   
}else
{
$('#verify_phonenumber_div').hide();  
}
}



function  checkPhonebook()
{
valid = $('#receiver_number').valid();
//alert(valid);
phonenumber = receiver_phonenumber();
verification_number = verification_phonenumber();



if(valid && phonenumber == verification_number)
{
    var ext = $('#phonenumber_ext').val()
    var phonenumber = $("#receiver_number").val();
    var country_code = $('#phonenumber_ctry').val();
    $.ajax({
      //this is the php file that processes the data and send mail
      url: '{% url "ajax_check_phonebook" %}',

      //GET method is used
      type: "GET",

      //data type
      dataType: 'json',

      //pass the data
      data: 'check_phonebook=true&json=true&number='+phonenumber+'&ext='+ext+'&country_code='+country_code,

      //Do not cache the page
      cache: false,
      //success
      success: function (html) {
                  if(html.show)
                   {
                    $('#sending_add_to_phonebook').show();
                    $('#save_to_phonebook').attr('checked','checked');
                   }else
                   {
                    $('#sending_add_to_phonebook').hide();
                    $('#save_to_phonebook').attr('checked','');
                   }  
      },
    });
}else
{
$('#sending_add_to_phonebook').hide();  
}
}