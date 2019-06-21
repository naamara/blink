

//global namespace
var RemitLanding = function(rate) {
	fields = rate.fields;
	this.currency = rate.currency
	this.our_charge = fields.transfer_fee_percentage
	this.exchange_rate = fields.to_usd;
	this.maximum_send_amount = fields.transfer_maximum_usd;
	this.minimum_send_amount = fields.transfer_minimum_usd;

	this.InitiateLanding()

var remit = this;
// detect the change 
$('#send_currency').bind("change keyup input",function() {

	if (!this.value.match(/^\d+$/)){
	//remove not numbers
	val = this.value.substr(0,this.value.length-1);
	this.value = val;	
	}else{
	if(parseInt(this.value) > remit.maximum_send_amount){
		this.value = remit.maximum_send_amount - 1;
	}
}
remit.InitiateLanding()

});

}


//handle phonenumbers
RemitLanding.prototype.InitiateLanding = function(){

currency = this.currency+' ';
send_amount = parseFloat($('#send_currency').val());

recieve_amount = send_amount * this.exchange_rate
$('#landing_recipient_total').html( accounting.formatMoney(recieve_amount,currency) )




usd_charge = ( parseFloat(this.our_charge) / 100) * send_amount;
$('#landing_our_charge').html(accounting.formatMoney(usd_charge,'USD '));


}




