jQuery(window).load(function(){
	jQuery('.default').dropkick();
    jQuery('input[type=text], input[type=email], textarea').placeholder();
});

jQuery(document).ready(function() {
    jQuery('#slider_content').flexslider({
        animation: "fade",
        slideshow: true,   
        slideshowSpeed: 7000, 
        animationSpeed: 600,  
        keyboard: true,
        useCSS: true,   
        touch: true, 
        video: false,
        start: function(slider){
            jQuery('body').removeClass('loading');
        }           
    });
    jQuery.fatNav();
    jQuery(window).resize(function() {
        if (jQuery(window).width() > 910) {
            jQuery(".fat-nav.active").css("display","none");
        }
        if (jQuery(window).width() <= 910) {
            jQuery(".fat-nav.active").css("display","block");
        }
    });


    window.scrollTo(0, 0);
    jQuery(".skip1").click(function(event){
         event.preventDefault();
         var dest=0;
         if($(this.hash).offset().top > $(document).height()-$(window).height()){
              dest=$(document).height()-$(window).height();
         }else{
              dest=$(this.hash).offset().top;
         }
         jQuery('html,body').animate({scrollTop:dest-0}, 1500,'swing');
     });


    var $tabs = $('#horizontalTab');
    $tabs.responsiveTabs({
        rotate: true,
        startCollapsed: 'accordion',
        collapsible: 'accordion',
        setHash: false,
        // disabled: [3,4],
        activate: function(e, tab) {
            $('.info').html('Tab <strong>' + tab.id + '</strong> activated!');
        },
        activateState: function(e, state) {
            //console.log(state);
            $('.info').html('Switched from <strong>' + state.oldState + '</strong> state to <strong>' + state.newState + '</strong> state!');
        }
    });

    $('#start-rotation').on('click', function() {
        $tabs.responsiveTabs('startRotation', 1000);
    });
    $('#stop-rotation').on('click', function() {
        $tabs.responsiveTabs('stopRotation');
    });
    $('#start-rotation').on('click', function() {
        $tabs.responsiveTabs('active');
    });
    $('#enable-tab').on('click', function() {
        $tabs.responsiveTabs('enable', 3);
    });
    $('#disable-tab').on('click', function() {
        $tabs.responsiveTabs('disable', 3);
    });
    $('.select-tab').on('click', function() {
        $tabs.responsiveTabs('activate', $(this).val());
    });
});	
