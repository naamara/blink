var div = '#message_box';

//for adding an error to a page
function add_error_msg(msg)
{
//first the div if its hidden
$(div).show();
$(div).html("<div class='noticecontainer'><div class='noticefail'><div class='noticeimsgdiv'><img id='noticeimsg' src='"+BASE_PATH+"images/close2.png' class='iepngfix'  Onclick=hide_notif('.noticecontainer')></img><br /></div>" + msg +"</div></div>");
}

//for adding an error to a page
function insert_error_msg(msg)
{
//first the div if its hidden
$(div).show();
$(div).insertBefore("<div class='noticecontainer'><div class='noticefail'><div class='noticeimsgdiv'><br /></div>" + msg +"</div></div>");
}

//success msg soft
function add_success_msg_soft(msg)
{
//first the div if its hidden
$(div).show();
$(div).html("<div class='noticecontainer'><div class='noticesoft'><div class='noticeimsgdiv'><br /></div>" + msg +"</div></div>");
}

function add_success_msg(msg,fadetime)
{
//first the div if its hidden
var i=Math.floor(Math.random()*msg.length);
divid = "noticefade" + i;
$(div).show();
$(div).html("<div class='noticecontainer'><div class='noticefade' id='"+divid+"'>" + msg +"</div></div>");
//new Effect.Fade(divid,{ fps: 10, duration: fadetime });
}


function insert_success_msg(msg,fadetime)
{
//first the div if its hidden
var i=Math.floor(Math.random()*msg.length);
divid = "noticefade" + i;
$(div).show();
$(div).insertBefore("<div class='noticecontainer'><div class='noticefade' id='"+divid+"'>" + msg +"</div></div>");
//new Effect.Fade(divid,{ fps: 10, duration: fadetime });
}


function insert_ajaxloading_div(msg)
{
$(div).show();
$(div).insert({top :"<div class='ajaxloadingdiv' id='ajaxloadingdiv"+div+"'  style='z-index:10000;display:block;'><img src='"+BASE_PATH+"images/loading.gif'>" + msg +"</div>"});
}


function add_ajaxloading_div(msg)
{
$(div).show();
$(div).html("<div class='ajaxloadingdiv' id='ajaxloadingdiv"+div+"'  style='z-index:10000;display:block;'><img src='"+BASE_PATH+"images/loading.gif'>" + msg +"</div>");
}

function hide_ajaxloading_div(div)
{
//alert(div);//new Effect.SlideUp($("ajaxloadingdiv"+div+""), {duration:0.2});
$("ajaxloadingdiv"+div+"").hide();
}

function remove_ajaxloading_div(div)
{
$('#ajaxloadingdiv'+div).remove();
}




//togglw the divs
function toggleContainer(param,param2)
{
if($(param).hide())
{
$(param2).show();
}
}

function stripString(param)
{
if(typeof(String.prototype.trim) === "undefined")
{
    String.prototype.trim = function()
    {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
}

var str = param.trim();
return str;
}


function print_r(theObj){
  if(theObj.constructor == Array ||
     theObj.constructor == Object){
    document.write("<ul>")
    for(var p in theObj){
      if(theObj[p].constructor == Array||
         theObj[p].constructor == Object){
document.write("<li>["+p+"] => "+typeof(theObj)+"</li>");
        document.write("<ul>")
        print_r(theObj[p]);
        document.write("</ul>")
      } else {
document.write("<li>["+p+"] => "+theObj[p]+"</li>");
      }
    }
    document.write("</ul>")
  }
}

function confirmNavigation(div)
{
jQuery(function($){
$(div).change(function() {
    if( $(this).val() != "" )
        window.onbeforeunload = "Are you sure you want to leave?";
});
 });
}

//get an image atrribute from a string
function getImageSrcFromString(data)
{
var imgsrc;
var imgsrcraw;
var data = "<div class='getimgsrc'>"+data+"</div>";
jQuery(function($){
//var imgsrc = $("img",$(data)).attr("src");
imgsrcraw = $("img", $(data)).attr ("src");
if(imgsrcraw)
{
var ext = imgsrcraw.split('.').pop();
ext = ext.toLowerCase();
if(ext == 'jpg' || ext == 'jpeg' || ext == 'gif' || ext == '')
{
imgsrc = imgsrcraw;
}
}
 });
return imgsrc;
}

//utitlity for opening new tab and focusing on it
function openLinkInNewWindow(link) {
var newWindow = window.open(link);
newWindow.focus();
}

//utitlity for posting to new window and selecting radion buttons
function uiPostToNewWindow(url,formid,fields,method)
{
    var form = $(''+formid+'');
    form.action = url;

    //change the submit method
    if(method)
    {
    form.method = method;
    }

     for(var field in fields)
     {
        form.innerHTML += '<input type="hidden" name="' + field + '" value="' + eval('fields["' + field + '"]') + '" />';
        }

    //alert(form.innerHtml);
    form.submit();
}

function uiRadioSelected(parent_id) {
    var options=$(parent_id).getElementsByTagName('input');
	var selected;
	for (var i=0; i<options.length; i++)
		if (options[i].checked)
			return options[i];
	return null;
}


/**
* Function : dump()
* Arguments: The data - array,hash(associative array),object
*    The level - OPTIONAL
* Returns  : The textual representation of the array.
* This function was inspired by the print_r function of PHP.
* This will accept some data as the argument and return a
* text that will be a more readable version of the
* array/hash/object that is given.
*/
function print_r(arr,level) {
var dumped_text = "";
if(!level) level = 0;

//The padding given at the beginning of the line.
var level_padding = "";
for(var j=0;j<level+1;j++) level_padding += "    ";

if(typeof(arr) == 'object') { //Array/Hashes/Objects
 for(var item in arr) {
  var value = arr[item];

  if(typeof(value) == 'object') { //If it is an array,
   dumped_text += level_padding + "'" + item + "' ...\n";
   dumped_text += dump(value,level+1);
  } else {
   dumped_text += level_padding + "'" + item + "' => \"" + value + "\"\n";
  }
 }
} else { //Stings/Chars/Numbers etc.
 dumped_text = "===>"+arr+"<===("+typeof(arr)+")";
}
var html = '<pre>'+dumped_text+'</pre>';
creatediv('print_r',html);
}


//create a new div
function creatediv(id, html, width, height, left, top) {

var newdiv = document.createElement('div'); newdiv.setAttribute('id', id); if (width) { newdiv.style.width = 300; } if (height) { newdiv.style.height = 300; } if ((left || top) || (left && top)) { newdiv.style.position = "absolute"; if (left) { newdiv.style.left = left; } if (top) { newdiv.style.top = top; } } newdiv.style.background = "#FFFFFF"; newdiv.style.border = "1px solid #CCCCCC"; if (html) { newdiv.innerHTML = html; } else { newdiv.innerHTML = "nothing"; } document.body.appendChild(newdiv);
}

function hide_notif(param)
{
$(param).hide();
}

function getViewPortwidth()
{
var viewportwidth;
 // the more standards compliant browsers (mozilla/netscape/opera/IE7) use window.innerWidth and window.innerHeight
 if (typeof window.innerWidth != 'undefined')
 {
 viewportwidth = window.innerWidth;
 }

// IE6 in standards compliant mode (i.e. with a valid doctype as the first line in the document)

 else if (typeof document.documentElement != 'undefined'
     && typeof document.documentElement.clientWidth !=
     'undefined' && document.documentElement.clientWidth != 0)
 {
       viewportwidth = document.documentElement.clientWidth;

 }

 // older versions of IE

 else
 {
       viewportwidth = document.getElementsByTagName('body')[0].clientWidth;
 }
return viewportwidth;
}


function getViewPortHeight()
{

 var viewportwidth;
 var viewportheight;

 // the more standards compliant browsers (mozilla/netscape/opera/IE7) use window.innerWidth and window.innerHeight

 if (typeof window.innerWidth != 'undefined')
 {

      viewportheight = window.innerHeight;
 }

// IE6 in standards compliant mode (i.e. with a valid doctype as the first line in the document)

 else if (typeof document.documentElement != 'undefined'
     && typeof document.documentElement.clientWidth !=
     'undefined' && document.documentElement.clientWidth != 0)
 {
       viewportheight = document.documentElement.clientHeight;
 }

 // older versions of IE

 else
 {
 viewportheight = document.getElementsByTagName('body')[0].clientHeight;
 }
return viewportheight;
}


function load_async(url)
{
(function() {
    function async_load(){
        var s = document.createElement('script');
        s.type = 'text/javascript';
        s.async = true;
        s.src = url;
        var x = document.getElementsByTagName('script')[0];
        x.parentNode.insertBefore(s, x);
    }
    if (window.attachEvent)
        window.attachEvent(addLoadEvent(async_load));
    else
        window.addEventListener(addLoadEvent(async_load), false);
})();
}



function addLoadEvent(func) {
  var oldonload = window.onload;
  if (typeof window.onload != 'function') {
    window.onload = func;
  } else {
    window.onload = function() {
      if (oldonload) {
        oldonload();
      }
      func();
    }
  }
}


function loader()
{
$.ajax({
      //this is the php file that processes the data and send mail
      url: ""+SERVER_PATH+"monkey_server.php",

      //GET method is used
      type: "GET",

      //pass the data
      data: '&loggin_timeout=true&',

      //Do not cache the page
      cache: false,
             complete: function(){
            },


      //success
      success: function (html) {
       // console.log('Loggin ');
      }
    });
}
