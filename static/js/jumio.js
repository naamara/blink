$(function(){
  console.log("jumio loaded");
  var marchant_token="fcf1eec3-728d-4f8a-8811-5b8e0e534597";
  var api_secret = "9mnQyVj1ppiyVESYroDHZS23Z9OfQ9GS";
  var success_url="https://simtransfer.com/jumiopass/";
  var error_url="https://simtransfer.com/jumiofail/";

  var post_data={
    "successurl":success_url,
    "error_url":error_url
  };

  var user_data={
    marchant_token:api_secret
  };

  var data_hash=window.btoa(JSON.stringify(post_data));

  var user_hash=window.btoa(JSON.stringify(user_data));

  console.log("Base64 Data: "+data_hash);
  console.log("Base64 User: "+user_hash);

  //jumio_request(data_hash,user_hash);
  cors_test(data_hash,user_hash,success_url,error_url);


});


function base_auth(item,value){
  var token = item+":"+value;
  var hash = //window.btoa(unescape(encodeURIComponent(token)));
  window.btoa(token);
  console.log("Hash: "+hash);
  return hash;
}

function jumio_request(data_hash,user_hash){
  var jumio_url="https://netverify.com/api/netverify/v2/initiateNetverify";

  $.ajax({
    url:jumio_url,
    type:"POST",
    contentType:"application/json",
    crossDomain: true,
    data:{
      "Authorization ":"Basic "+data_hash
    },

    headers:{
       "Access-Control-Allow-Origin":"https://netverify.com/api/netverify/v2/initiateNetverify",
       Authorization:"Basic "+user_hash,
       Accept: "application/json",
       //"Content-Type":"application/json",
       "User-Agent":"MyCompany MyApp/1.0.0",
    },

    //beforeSend:function(xhr){
      //xhr.setRequestHeader("Authorization", "Basic "+user_hash);
      //xhr.setRequestHeader("Accept","application/json");
      //xhr.setRequestHeader("Content-Type", "application/json");
      //xhr.setRequestHeader("Accept","application/json");
      //xhr.setRequestHeader("User-Agent","YOURCOMPANYNAME YOURAPPLICATIONNAME/x.x.x");
    //},
    success:function(data){
      console.log("Success: "+data);
    },
    error:function(jqXhr, textStatus, errorThrown){
      console.log("Errors: "+JSON.stringify(jqXhr)+" "+textStatus.toString()+" "+errorThrown.toString());
    }

  });

}


/*


curl -i --user validuser:70e12a10-83c7-11e0-9d78-0800200c9a65 -H "Content-Type: application/json" -H "Accept: application/json" -X POST -d '{"person":{"name":"bob"}}' http://mysite.com/api.php

curl -H




curl --user fcf1eec3-728d-4f8a-8811-5b8e0e534597:password 9mnQyVj1ppiyVESYroDHZS23Z9OfQ9GS  https://netverify.com/api/netverify/v2/initiateNetverify

*/


/*
Data:
eyJzdWNjZXNzdXJsIjoiaHR0cHM6Ly9zaW10cmFuc2Zlci5jb20vanVtaW9wYXNzLyIsImVycm9yX3VybCI6Imh0dHBzOi8vc2ltdHJhbnNmZXIuY29tL2p1bWlvZmFpbC8ifQ==

User:
eyJtYXJjaGFudF90b2tlbiI6IjltblF5VmoxcHBpeVZFU1lyb0RIWlMyM1o5T2ZROUdTIn0=

*/
