

//global namespace
var Remit = function(rate,phonenumbers,validate_url) {
	fields = rate.fields;
	this.currency = rate.currency
	this.our_charge = fields.transfer_fee_percentage
	this.exchange_rate = fields.to_usd;
	this.maximum_send_amount = fields.transfer_maximum_usd;
	this.minimum_send_amount = fields.transfer_minimum_usd;
	this.extra_fees = rate.extra_fees;
	this.phonenumbers = phonenumbers;
	this.validate_url = validate_url;
	//display purposes
	this.send_phonenumber = 0
	this.send_amount = 0



this.formatSendAmount();


}


//handle phonenumbers
Remit.prototype.Phonenumber = function(){

receiver_lname = $('#receiver_lname');
receiver_fname = $('#receiver_fname');

phonenumber_ext = $('#phonenumber_ext');
verify_phonenumber_ext = $('#phonenumber_ext_verify');

receiver_number = $('#receiver_number');
verify_receiver_number = $('#verify_receiver_number');

remit = this

$('#phonebook_number').on('change', function() {

	var selected = $('option:selected', this);

	//set names
	receiver_fname.val(selected.data('fname'));
	receiver_lname.val(selected.data('lname'));

	//set extensions
	network_ext = selected.data('ext');
	phonenumber_ext.val(network_ext);
	verify_phonenumber_ext.val(network_ext);

	//set number
	network_number = selected.data('number');
	receiver_number.val(network_number);
	verify_receiver_number.val(network_number);


});

$("#phonenumber_ext").change(function(){
$('#phonenumber_ext_verify').val($('option:selected', this).val())
});

$("#phonenumber_ext_verify").change(function(){
$('#phonenumber_ext').val($('option:selected', this).val());

});

//check the phonenumber
$('#verify_receiver_number, #verify_receiver_number, #phonenumber_ext_verify, #phonenumber_ext, #phonebook_number').change(function(){



if($('#verify_receiver_number').valid()){

remit.checkPhonebook();	

}


});

}


//other fees
Remit.prototype.OtherFees = function(){
ext = $('option:selected', $('#phonenumber_ext_verify')).val();
fees = parseFloat(this.extra_fees[ext]);
if(isNaN(fees)){
	fees = 0;
}
return fees
}



//process send amount function
Remit.prototype.formatSendAmount = function(){

var sendamount = $('#amount_sent').val();

remit = this

var maximum_send_amount = remit.maximum_send_amount;

if (!sendamount.match(/^\d+$/)){
	//remove not numbers
	val = sendamount.substr(0,sendamount.length-1);
	sendamount = val;	
	}else{

	if(parseFloat(sendamount) > maximum_send_amount){
		sendamount = maximum_send_amount;
		//alert("Maximum amout of "+maximum_send_amount);
	}

	}
	
	amount_received = parseFloat(sendamount) * remit.exchange_rate;
	
	//calculate the extra fees
	extra_fees = remit.OtherFees();




	amount_sent = accounting.toFixed(sendamount, 2);


	if(isNaN(amount_received) || amount_received < 1 ){
	amount_received = 0;
	extra_fees = 0;
	}

	//get the total amount to sender
	total_amount_received = amount_received - extra_fees;
	total_amount_received = accounting.toFixed(total_amount_received, 2);




	//amount sent
	$('#receipt_transferamount_usd').html(accounting.formatMoney(amount_sent,'USD '));
	usd_charge = ( parseFloat(remit.our_charge) / 100) * amount_sent;


	$('#receipt_transfercharge_usd').html(accounting.formatMoney(usd_charge,'USD '));
	total_usd_charge = parseFloat(amount_sent) + parseFloat(usd_charge)
	//total_usd_charge = parseFloat(total_usd_charge)
	$('#receipt_transfertotal_usd').html(accounting.formatMoney(total_usd_charge,'USD '));




	//amount received
	//$('#amount_received').val(amount_received);
	$('#amount_received').val(total_amount_received);
	$('#receipt_transferamount_ugx').html( accounting.formatMoney(amount_received,remit.currency+' ') );
	$('#receipt_transfertotal_ugx').html( accounting.formatMoney(total_amount_received,remit.currency+' ') );

	//compute extra fees
	$('#receipt_otherfees_ugx').html(accounting.formatMoney(extra_fees,remit.currency+' '))
	//alert(extra_fees);


	remit.send_amount = total_amount_received

}


//handle send amount changes
Remit.prototype.SendAmount = function(){

maximum_send_amount = parseFloat(this.maximum_send_amount);

exchange_rate = parseFloat(this.exchange_rate);
currency = this.currency+' '
usd_charge_percentage = this.our_charge;

var remit = this;

// detect the change 
$('#amount_sent').bind("change keyup input",function() {

	remit.formatSendAmount();
	

});
}


//validate form , depends on Jquery validate
Remit.prototype.ValidateForm = function(){

var remit = this;

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
      max:remit.maximum_send_amount,
      minlength:1,
      maxlength:6,
      min:remit.minimum_send_amount
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
        min : "You Cannot Transfer An Amount less than " + remit.minimum_send_amount,
        max : "You Cannot Transfer An Amount More than " + remit.maximum_send_amount,
      }
		},
	submitHandler: function(form) {
		//alert("sending money");
		var phonenum = $('#phonenumber_ext').val()+$('#receiver_number').val();
		var msg = 'You are about to Transfer '+$('#recievemoney_currency').val()+' '+$('#receipt_transfertotal_ugx').html()+' to '+$("#phonenumber_ctry_ext").val()+phonenum;
		
		if(confirm(msg))
		{
		//alert(get_mobile_code(phonenum))
		if (remit.get_mobile_code(phonenum) == 'MTN' && 1 ){
			var promise = remit.VerifyPhonenumber(
				$('#phonenumber_ctry').val(),
				$('#phonenumber_ext').val(),
				$('#receiver_number').val()
				);
			promise.success(function (response) {

	        $('#loading_modal').modal('hide');

	        if(response.has_error){


	        alert("Transfers to MTN numbers are currently unavailable.You can use any of our other available services");

	        }else{



	        if(!response.valid){

	        	if(!response.valid_momo){

	        	alert("The number you're trying to send money to is not registered for mobile money. Please provide a number that is registered for mobile money");
	        	
	        	}else{

	        	alert("The number that you're trying to send money to is not fully registered with MTN Uganda. Please inform the recipient to go to the nearest MTN Service Centre with a valid ID to complete SIM card validation.");
	        	}


	        }else{
	 
	        form.submit();

	        }
	    }
		});

		}else{
		form.submit();
		}

		}else{
		return false;
		}
		
		//return remit.VerifyPhonenumber(phonenum,phonenum,phonenum);
    	//return false;
		}
    
    });
} 




Remit.prototype.checkPhonebook = function()
{

phonenumbers = this.phonenumbers


var show = 1;
var ext = $('#phonenumber_ext').val()
var phonenumber = $("#receiver_number").val();
var code = $('#phonenumber_ctry').val();
phonenumber = ''+code+ext+phonenumber+'';
console.log(phonenumber)

//show = phonenumbers[phonenumber]
show = phonenumbers.indexOf(phonenumber)

//console.log(show)

 if(show < 0)
 {
                    
       	$('#sending_add_to_phonebook').show();
         $('#save_to_phonebook').attr('checked','checked');
                               

                   }else
                   {
                   

                      $('#sending_add_to_phonebook').hide();
                    $('#save_to_phonebook').attr('checked','');

 					}  


}



Remit.prototype.VerifyPhonenumber =  function(country_code,ext,phonenumber)
{

	if(country_code == '256')
	{
var remit = this;
    //var ext = $('#phonenumber_ext').val()
    //var phonenumber = $("#receiver_number").val();
    //var country_code = $('#phonenumber_ctry').val();
    return $.ajax({
      //this is the php file that processes the data and send mail
      url: ''+remit.validate_url+'',

      //GET method is used
      type: "GET",

      //data type
      dataType: 'json',

      //pass the data
      data: 'is_verified=true&json=true&number='+phonenumber+'&ext='+ext+'&country_code='+country_code,

      //Do not cache the page
      cache: false,
       beforeSend: function(){
            //$('#loading').show();
             $('#loading_modal').modal('show');
            },
             complete: function(){
            $('#loading_modal').modal('hide');
      },

    });
}else{
	return true;
}
}

Remit.prototype.get_mobile_code = function(phonenum){
console.log(phonenum)
str = phonenum.substring(0,2)
arr = ['77', '78']
if(!!~arr.indexOf(str)){
return 'MTN';
}
return false; 
}
