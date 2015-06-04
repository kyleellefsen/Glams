
$(init);
function init() {
	var query=''; 
	$.post(
		"/experimentlog/ajax/refresh/",
		function(data){
			$('#db').html(data);
			$('#db').dragtable("destroy"); 
			$('#db').dragtable({dragHandle:'.col-handle', maxMovingRows:1}); // http://akottr.github.io/dragtable/ I just included the css file, the js file.  
			reload();
		}
		,"text");
}
function reload(){
	$('table').tablesorter();
	$('#db tbody tr').hover(
		function () {
			$(this).css({'background':'#F1ECFF', 'border':'1px'});
		}, 
		function() {
			$(this).css({'background':''});
		}
	);
	$('.tooltip').tooltipster({interactive: 'true'});
	
}



$( document ).ready(function() {
	$('#db').dragtable({dragHandle:'.col-handle', maxMovingRows:1}); // http://akottr.github.io/dragtable/ I just included the css file, the js file.  
	$( '.bubble' ).draggable();
	            $('.tooltip').tooltipster();

});