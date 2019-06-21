//utility funcs
String.prototype.replaceAt=function(index, character) {
    return this.substr(0, index) + character + this.substr(index+character.length);
}

//global namespace
var Remit = function(rate) {
	//intiate remit
	this.rate = rate
}



//landing form
Remit.prototype.LandingForm = function(){

var countrycode = $('#countrycode');
var sendamount = $('#sendamount');
var recieveamount = $('#receiveamount');
var receiveamountholder = $('#receiveamountholder');
var mobilenumber = $("#mobile_number");

mobilenumber.inputmask("999-999999999");
mobilenumber.val(countrycode.val());

var  delay_time = 1000;


var remit = this;

var delay = (function(){
  var timer = 0;
  return function(callback, ms){
  clearTimeout (timer);
  timer = setTimeout(callback, ms);
 };
})();

var formatform = function(reverse){

	if (reverse === undefined) {
          reverse = false;
    }

	var cc = countrycode.val()
	var exchange_rate = remit.rate.usd_to_ugx;
	var currency = 'UGX ';
	var min_amount = Math.floor(remit.rate.min_amount);
	var max_amount = Math.floor(remit.rate.max_amount);


	if(cc == '254'){
	var exchange_rate = remit.rate.usd_to_kes;
	var currency = 'KES ';
	}

	if(cc == '250'){
	var exchange_rate = remit.rate.usd_to_rwf;
	var currency = 'RWF ';
	}

	var min_amount_exchange = Math.floor(exchange_rate) * min_amount;
	var max_amount_exchange = Math.floor(exchange_rate) * max_amount;

	var samt = Math.floor(sendamount.val());
	var recamt = recieveamount.val();
	recamt = recamt.match(/\d/g);
	recamt = recamt.join("");
	recamt = Math.floor(recamt)

	
	if(samt < min_amount || samt > max_amount){

		if(samt < min_amount){
			samt = min_amount;
			sendamount.val(min_amount);
		}

		if(samt > max_amount){
			samt = max_amount;
			sendamount.val(max_amount);
		}
	}


if(recamt < min_amount_exchange || recamt > max_amount_exchange){

		if(recamt < min_amount_exchange){
			recamt = min_amount_exchange;
			recieveamount.val(min_amount_exchange);
		}

		if(recamt > max_amount_exchange){
			recamt = max_amount_exchange;
			recieveamount.val(max_amount_exchange);
		}
	}

	if(reverse){

	var newsendamt = recamt / Math.floor(exchange_rate);
	newsendamt = Math.floor(newsendamt);
	sendamount.val(newsendamt);
	recieveamount.val(currency+accounting.formatNumber(recamt));

	}else{
	
	
	var newrecamt = samt * exchange_rate;
	newrecamt = Math.floor(newrecamt);
	newrecamt = accounting.toFixed(newrecamt,0);
	receiveamountholder.val(newrecamt);
	recieveamount.val(currency+accounting.formatNumber(newrecamt));


}
}

var formatNumber = function(){

	var number = mobilenumber.val();
	cc = countrycode.val();
	ext = number.substring(0, 3);
	if(cc !== ext){
		mobilenumber.val(cc);
	}

	
	

	if(number.charAt(4) === '0'){
		console.log(number.charAt(4));
    	number = number.substring(0, 3);
    	mobilenumber.val(number);
	}

    /*
	if(number.length > 9){
		number = $('#mobilenumberplaceholder').val();
	}else{
		$('#mobilenumberplaceholder').val(number);
	}
	$('#mobilenumberplaceholder').val(number);
	var mssidn = number;
	if(number.length == 9){
		mssidn = cc_code_ext+'-'+number;
    }
	$("#mobile_number").val(mssidn);
	*/
}


$("#sendamount").keyup(function(){
	delay(function(){
		formatform();
	}, delay_time );
});


$("#receiveamount").keyup(function(){
	delay(function(){
		formatform(reverse=1);
	}, delay_time );
});

$("#countrycode").change(function(){
formatform();
var ext = '+'+countrycode.val()+'-';
$("#mobile_number").val(ext);
formatNumber();
});

$("#mobile_number").keyup(function(){
	/*
	delay(function(){
	formatNumber();
	}, delay_time );
*/
formatNumber();
})


}