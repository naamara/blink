

//global namespace
var PayBill = function(rate, validate_url) {
	fields = rate.fields;
	this.currency = rate.currency
	this.our_charge = fields.transfer_fee_percentage
	this.exchange_rate = fields.to_usd;
	this.maximum_send_amount = fields.transfer_maximum_usd;
	this.minimum_send_amount = fields.transfer_minimum_usd;
	this.extra_fees = rate.extra_fees;
	this.validate_url = validate_url;
	//display purposes
	this.send_phonenumber = 0
	this.send_amount = 0

}




//other fees
PayBill.prototype.OtherFees = function(){
ext = $('option:selected', $('#phonenumber_ext_verify')).val();
fees = parseFloat(this.extra_fees[ext]);
if(isNaN(fees)){
	fees = 0;
}
return fees
}

//process send amount function
PayBill.prototype.formatSendAmount = function(){

var sendamount = $('#amount').val();
//console.log("formatSendAmount: "+sendamount);

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

PayBill.prototype.formatLocalSendAmount = function(){
	var sendamount = $('#amount_received').val();
	//console.log("formatSendAmount: "+sendamount);

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

		send_amount = parseFloat(sendamount) / remit.exchange_rate;

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
PayBill.prototype.SendAmount = function(){

maximum_send_amount = parseFloat(this.maximum_send_amount);

exchange_rate = parseFloat(this.exchange_rate);
currency = this.currency+' '
usd_charge_percentage = this.our_charge;

var remit = this;

// detect the change
$('#amount').bind("change keyup input",function() {
	remit.formatSendAmount();

	// if (!this.value.match(/^\d+$/)){
	// //remove not numbers
	// val = this.value.substr(0,this.value.length-1);
	// this.value = val;
	// }else{
	//
	// if(parseFloat(this.value) > maximum_send_amount){
	// 	this.value = maximum_send_amount;
	// }
	//
	// }
	//
	// amount_received = parseFloat(this.value) * exchange_rate;
	//
	// //calculate the extra fees
	// //extra_fees = PayBill.OtherFees();
	// extra_fees = 0
	//
	//
	//
	// amount_sent = accounting.toFixed(this.value, 2);
	//
	//
	// if(isNaN(amount_received) || amount_received < 1 ){
	// amount_received = 0;
	// extra_fees = 0;
	// }
	//
	// //get the total amount to sender
	// total_amount_received = amount_received - extra_fees
	// total_amount_received = accounting.toFixed(total_amount_received, 2)
	//
	//
	// //amount sent
	// $('#receipt_transferamount_usd').html(accounting.formatMoney(amount_sent,'USD '));
	// usd_charge = ( parseFloat(usd_charge_percentage) / 100) * amount_sent;
	// $('#receipt_transfercharge_usd').html(accounting.formatMoney(usd_charge,'USD '));
	// total_usd_charge = parseFloat(amount_sent) + parseFloat(usd_charge)
	// //total_usd_charge = parseFloat(total_usd_charge)
	// $('#receipt_transfertotal_usd').html(accounting.formatMoney(total_usd_charge,'USD '));
	//
	//
	//
	//
	// //amount received
	// //$('#amount_received').val(amount_received);
	// $('#amount_received').val(total_amount_received);
	// $('#amount_charged').val(total_usd_charge);
	// $('#receipt_transferamount_ugx').html( accounting.formatMoney(amount_received,currency) );
	// $('#receipt_transfertotal_ugx').html( accounting.formatMoney(total_amount_received,currency) );
	//
	// //compute extra fees
	// $('#receipt_otherfees_ugx').html(accounting.formatMoney(extra_fees,currency))
	// //alert(extra_fees);
	//
	//
	// PayBill.send_amount = total_amount_received


});



 $('#amount_received').bind("propertychange change keyup input paste",function(){

	if (!this.value.match(/^\d+$/)){
	//remove not numbers
	val = this.value.substr(0,this.value.length-1);
	this.value = val;
	}else{

	// if(parseFloat(this.value) > maximum_send_amount){
	// 	this.value = maximum_send_amount;
	// }

	}


	usd_amount = parseFloat(this.value) / exchange_rate;
	extra_fees = 0;
	total_usd_amount = usd_amount + extra_fees;
	total_usd_amount = accounting.toFixed(total_usd_amount, 2)

	//console.log("total_usd_amount: "+total_usd_amount);

	usd_charge = ( parseFloat(usd_charge_percentage) / 100) * total_usd_amount;

	var total_usd = total_usd_amount + usd_charge;
	var final_usd =accounting.toFixed(total_usd, 2)

	//console.log("USD Charge UGX: "+usd_charge);

	$('#receipt_transfercharge_usd').html(accounting.formatMoney(usd_charge,'USD '));
	$('#receipt_transferamount_usd').html(accounting.formatMoney(total_usd_amount,'USD '));



	//console.log("Total USD amount: "+total_usd_amount.toString());

	total_amount_received = accounting.toFixed($('#amount_received').val(), 2);

	//console.log("total_amount_received: "+total_amount_received);

	$('#receipt_transferamount_ugx').html( accounting.formatMoney(total_amount_received,currency) );

	$('#receipt_transfertotal_ugx').html( accounting.formatMoney(total_amount_received,currency) );






	$('#amount').val(final_usd);

	PayBill.send_amount = total_amount_received


	//$(this).val(parseFloat(this.value));

	// $('#paybill_amount').val($(this).val());
	// $('#hidden_amount_received').val($(this).val());
	// //$('#hidden_amount_received').val(parseFloat(this.value));
	// //$('#hidden_amount').val($(this).val());
	// $('#hidden_amount').val($(this).val());


	$('#paybill_amount').val(total_amount_received);
	$('#hidden_amount_received').val(total_amount_received);
	$('#hidden_amount_received').val(parseFloat(this.value));
	//$('#hidden_amount').val($(this).val());
	$('#hidden_amount').val(final_usd);



});

$('#amount_received').focusout(function(){
	//console.log("Amount recieved focusedout");
	$(this).val(total_amount_received);
});

}

PayBill.prototype.QueryAccount =  function(referencenum, billtype, location)
{

	var remit = this;
    return $.ajax({
      //this is the php file that processes the data and send mail
      url: ''+remit.validate_url+'',

      //GET method is used
      type: "GET",

      //data type
      dataType: 'json',

      //pass the data
      data: 'querypaybill=true&json=true&referencenum='+referencenum+'&billtype='+billtype+'&location='+location,

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
}



PayBill.prototype.HandleSubmit = function(){

var remit = this;


	$("#send_money_form").submit(function( event ) {



	//e.preventDefault();





			$('#loading_modal').modal('show');


			alert(event);

			try {

			referencenum = $('#referencenum').val();
			billtype = $('#billtype').val();
			location = $('#location').val();
			var promise = remit.QueryAccount(referencenum, billtype,location);

			promise.success(function (response) {

	        $('#loading_modal').modal('hide');


	        if(response.responsecode == 10){

	        alert("An error occurred on our end, the paybill functionality is currently unavailable. Our team has been notified and is looking into the issue, please try again later");

	        }else{


	        if(billtype == 1){
	        	billtype = 'Electricity (UMEME)';
	        }else{
	        	billtype = 'Water (NWSC)';
	        }


	        if(response.responsecode == 7){

	        	alert(
	        		"The account details you provided are not valid. Account Number: "+referencenum+" is not a valid account number  for Billtype : "+billtype);
	        }else{

	        result = response.result
	        accountname = result.customer_name;
	        outstandingbalance = result.oustanding_balance;
	        var msg = 'You are about to PayBill for  Account Number: '+referencenum+' , Billtype : '+billtype;
	        msg = msg + " Account Name is "+accountname+" and outstanding balance is "+outstandingbalance


	        if(confirm(msg))
			{

			}else{
			event.preventDefault();
			return false;
			}


	        }

	    }

		});

		}catch(err){

			alert(err)
		}

		});

}
