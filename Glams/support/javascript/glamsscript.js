$(document).ready(function () {
    //$('aside').hide();
	$('#between_article_and_aside').hide();
	var windowWidth = ((parseInt($(window).width()))) - 50;
	$('#everything').css({'width':windowWidth});
    /*$('article').click(function(){
        $('aside').hide();
        $('#between_article_and_aside').show("fade", {}, 700);
    });
    $('#between_article_and_aside').click(function(){
        $('aside').show("fade", {}, 700);
        $('#between_article_and_aside').hide();
    });*/

var t;
    $('#userLogin').hover(
            function(){
                clearTimeout(t);
                $('#userLoginList').show("fade", {}, 700);
            },function(){
            t=setTimeout("$('#userLoginList').hide('fade', {}, 300);",800);
    });
    $('#userLoginBox').click(function(){
        $('#userLoginList').show("fade", {}, 700);
    });
    $('#userLoginList li a').hover(
        function(){
            clearTimeout(t);
            $('#userLoginList').show();
        },function(){
        t=setTimeout("$('#userLoginList').hide('fade', {}, 300);",800);
    });
});   
    