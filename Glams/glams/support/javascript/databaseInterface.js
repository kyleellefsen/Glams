jQuery.fn.single_double_click = function(single_click_callback, double_click_callback, timeout) {
  return this.each(function(){
    var clicks = 0, self = this;
    jQuery(this).click(function(event){
      clicks++;
      if (clicks == 1) {
        setTimeout(function(){
          if(clicks == 1) {
            single_click_callback.call(self, event);
          } else {
            double_click_callback.call(self, event);
          }
          clicks = 0;
        }, timeout || 300);
      }
    });
  });
}

function getToday(){
var d = new Date();

var month = d.getMonth()+1;
var day = d.getDate();

var output = d.getFullYear() + '-' +
    ((''+month).length<2 ? '0' : '') + month + '-' +
    ((''+day).length<2 ? '0' : '') + day;
return output;
}

$(init);
function init() {
	var query=''; 
	$.post(
		"/database/ajax/refresh/",
		function(data){
			$('#db').html(data);
			$('#db').dragtable("destroy"); 
			$('#db').dragtable({dragHandle:'.col-handle', maxMovingRows:1}); // http://akottr.github.io/dragtable/ I just included the css file, the js file.  
            var nrows=$('#db tr').length-1;
            if(nrows==1)
                $('#nrows').text(nrows+' result');
            else
                $('#nrows').text(nrows+' results');
			reload();
		}
		,"text");
}
            
function reload(){
	$('.bubble, .getBubbleButton, tr').hover(function(){mouse_is_inside=true; },function(){ mouse_is_inside=false;});
	$('.tooltip').tooltipster({interactive: 'true'});
	$('.mouse_notes, .cagenotes').css({"white-space":"nowrap","text-overflow":'ellipsis'});
    $('#db th').single_double_click(
        function(){ // A single click event occurred
            var col=$(this).attr('data-header');
            $.post( "/database/ajax/sortby/", {col:col},function(data){init();});
        },
        function(){  //A double click event occurred 
            var col=$(this).attr('data-header');
            $.post( "/database/ajax/getFilterForm/", {col:col},
                function(data){
                    $('.bubble').html(data);
                    $('#filter').submit(function(){
                        $('.bubble').hide(); 
                        $.post(    "/database/ajax/setfilter/",
                                   {col: $('#filter').attr('col'), filt: $("#filter").serialize()},
                                   function(data){
                                        init();
                                    },
                                 "text");  
                        return false; 
                    });
                    $('.bubble .close_button').click(function(){
                        $('.bubble').hide(); 
                        $('#everything').fadeTo("medium", 1);
                    });
                    $('.bubble').show();
                },'text');
        });
        


	$("#db tr .mousename").click(function(){
		$('.bubble').show();
		
		var mouseID=$(this).attr('mouseID');
		editmice(mouseID);
		$('#everything').fadeTo("slow", 0.55);
   });
   $(".cagename, .cagename2").click(function(){
        var cagename=$(this).html();
        displaycage(cagename);
	});
    


	var el=$("#db tr .mousename")
	el.attr("draggable",'True');
	el.on('dragstart', function(e){
		e.originalEvent.dataTransfer.effectAllowed = 'copy';
		e.originalEvent.dataTransfer.setData('mousename', $(this).html());
		e.originalEvent.dataTransfer.setData('mouseID', $(this).attr('mouseid'));
	});
	
	var el=$("#db tr td.cagename2")
	el.attr("draggable",'True');
	el.on('dragstart', function(e){
		e.originalEvent.dataTransfer.effectAllowed = 'copy';
		e.originalEvent.dataTransfer.setData('cagename', $(this).html());
	});
	
	// I'm implimenting the drag and drop from http://html5demos.com/drag#view-source.

}



var mouse_is_inside = false;
$(document).ready(function(){
	$('#db').dragtable({dragHandle:'.col-handle', maxMovingRows:1}); // http://akottr.github.io/dragtable/ I just included the css file, the js file.  
	$( '.bubble' ).draggable({cancel:'fieldset, input, textarea, select'});
	$('input:checkbox[name="view"]').change(function(){
		if($(this).is(':checked'))
			var viewtype='mouse';
		else
			var viewtype='cage';
		$.post("/database/ajax/pickView/", {viewtype:viewtype}, 
			function(data){
				$(init);
			}, "text");
	});
	
	var bin=$('#trashcan');
	bin.on('dragover', function(e){
		if (e.preventDefault) e.preventDefault(); // allows us to drop
		e.originalEvent.dataTransfer.dropEffect = 'copy';
		return false;
	});
	bin.on('drop',function(e){
		var mousename=e.originalEvent.dataTransfer.getData('mousename');
		var plname=e.originalEvent.dataTransfer.getData('plname');
		var cagename=e.originalEvent.dataTransfer.getData('cagename');
		var oldcagename=e.originalEvent.dataTransfer.getData('oldcagename'); //sometimes PLs and mice have old cage id.  The old cage needs to be updated.
		var name;
		var typ='';
		if (mousename!=''){
			typ='mouse';
			name=mousename;}
		else if(plname!=''){
			typ='pl';
			name=plname;}
		else if(cagename!=''){
			typ='cage';
			name=cagename;}
		if(typ!=''){
			if (confirm('Are you sure you want to permanently delete this?  This action cannot be undone.')){
				$.post("/database/ajax/trash/", {name:name,typ:typ},
					   function(data){
                            init();
							alert(data);
							if(oldcagename!='')
								refreshcage(oldcagename);
					   }, "text");
			   } else{
				   alert('Not deleted.');
			   }
		   }
	});
	
	$("html").click(function(){
		if(! mouse_is_inside) {
			$('#everything').fadeTo("medium", 1);
		}
	});

	$('#editmice').click(function(){
		$('.bubble').show();
		editmice('');
		$('#everything').fadeTo("slow", 0.55);
	});
	
	$('#addcage').click(function(){
		var nCages=$('.cage').length;
		addcage(nCages+1,'');
	});
	
	$('#pickColumns').click(function(){
		$('.bubble').show();
		pickColumns();
		$('#everything').fadeTo("slow", 0.55);
	});
    
});


function closePopup(popup){
	$(popup).hide();
	$('#everything').fadeTo("medium", 1);
}

//*******************************************************************************************************************************
//************************************     COLUMN AND FILTER STUFF      *********************************************************
//*******************************************************************************************************************************

var t;
var convert={'mousename':'Mouse','strain':'Strain','sex':'Sex','life_status':'Life Status','breeding_status':'Breeding Status','DOB':'DOB','DOD':'DOD','cause_of_death':'Cause of Death','tag':'Tag','mouse_notes':'Notes','genotyped':'Genotyped','cagename':'Cage','cagename2':'Cage','mother':'Mother','father':'Father','reserve_lab_member':'Experimentor','reserve_date':'Experiment Date','reserve_description':'Experiment Description','cagename':'Cage','notes':'Notes','date_activated':'Date Activated','date_inactivated':'Date Inactivated','location':'Location','active':'Active','caretaker':'Caretaker'}

function removefilter(col){
    $.post('/database/ajax/removefilter/',{col:col}, function(data){ init();});}
	
function removeGeneSelectFilter(a){
	var thisselect=$(a).parent();
	var count=thisselect.parent().children().length-1;
	var idx=thisselect.index();
	if(thisselect.find('.genelist').val()==''){ //if the gene name is blank, 
		if(idx<count && (idx>1 || (idx>0 && count>1))) // and its not the last select or part of the first two selections 
			thisselect.remove(); //remove it
	}else if(idx==count && idx!=0){
			thisselect.clone().insertAfter(thisselect);
	}
	idx=0;
	$('.geneselect').each(function( index ) { 
		$(this).find('.logiccomb').attr('name','logiccomb'+idx);
		$(this).find(".genelist").attr('name','gene'+idx);  
		$(this).find(".zygosity").attr('name','zygosity'+idx); 
		idx+=1; });
}
		
function removeGeneSelect(a){
	var count=0;
	$('.geneselect').each(function( index ) { if($(this).find(".genelist").val()=='') count+=1;});
	$('.geneselect').each(function( index ) { if($(this).find(".genelist").val()=='' && count>1) {$(this).remove();count-=1;}     });
	if (count==0) {$('.geneselect:last').clone().insertAfter(".geneselect:last")};
	count=1;
	$('.geneselect').each(function( index ) { $(this).find(".genelist").attr('name','gene'+count);  $(this).find(".zygosity").attr('name','zygosity'+count); count+=1; });
}
function removecageHistorySelect(a){
   var count=0;
	$('.cageHistorySelect').each(function( index ) { if($(this).find("input").first().val()=='') count+=1;});
	$('.cageHistorySelect').each(function( index ) { if($(this).find("input").first().val()=='' && count>1) {$(this).remove();count-=1;}     });
	if (count==0) { $('.cageHistorySelect:last').clone().insertAfter(".cageHistorySelect:last"); 
					$('.cageHistorySelect:last input').val(''); }
	count=1;
	$('.cageHistorySelect').each(function( index ) {    $(this).children('input').eq(0).attr('name','oldcagename'+count);  
														$(this).children('input').eq(1).attr('name','startDate'+count);  
														$(this).children('input').eq(2).attr('name','endDate'+count);  
														count+=1; });
}
function removeReserveSelect(a){
	var count=0;
	$('.reserveSelect').each(function( index ) { if($(this).find(".reservenamelist").val()=='') count+=1;});
	$('.reserveSelect').each(function( index ) { if($(this).find(".reservenamelist").val()=='' && count>1) {$(this).remove();count-=1;}     });
	if (count==0) {$('.reserveSelect:last').clone().insertAfter(".reserveSelect:last")};
	count=1;
	$('.reserveSelect').each(function( index ) {    $(this).find(".reservenamelist").attr('name','reserve_lab_member'+count);  
													$(this).find(".reserve_date").attr('name','reserve_date'+count);
													$(this).find(".reserve_description").attr('name','reserve_description'+count);
													$(this).find(".reserve_status").attr('name','reserve_status'+count);
													$(this).find(".reserve_filenames").attr('name','reserve_filenames'+count);
													$(this).find(".reserve_notes").attr('name','reserve_notes'+count);
													count+=1; });
}

function pickColumns(){
	$.post("/database/ajax/pickColumnsForm/",
	{},
	function(data){
		$('.bubble').html(data);
		$('#selectColumns').submit(function(){
			$.post(    "/database/ajax/selectColumns/",
					   {columns: $("#selectColumns").serialize()},
					   function(data){
						  headers='';
						  data2=data.split(',')
						  for (var i=0;i<data2.length-1;i=i+2){ headers+="<th data-header='"+data2[i]+"' filter='"+data2[i+1]+"'>"+convert[data2[i]]+"</th>"; }
						  $('#db thead tr').html(headers);
						  init();
						  $('.bubble').hide(); 
						  $('#everything').fadeTo("medium", 1);

						},
					 "text");  
			return false; });
	}, "text");
}



//*******************************************************************************************************************************
//************************************     CAGE STUFF      **********************************************************************
//*******************************************************************************************************************************
var cageTabIdx=2;
function addcage(cageN,cagename){
	$.post("/database/ajax/addcageForm/", 
	   {cageN:cageN, cagename:cagename},
		function(data){
			var i=0;
			$('body').append(data);
			$( '.cage').each(function(){
				i+=1;
				$(this).attr('id','cage'+i);
			});
			var id='#cage'+i;
			$(id).draggable();
			
			
			if(cagename==''){
				cagename='New Cage';
				$( ".tabs" ).tabs();
				var cage=$('.cage').filter(function(){return $(this).find('h1').text()=='New Cage';});
				cage.find('form').submit(function(){
					$.post(    "/database/ajax/addcage/",
					   {data: $(id+' form').serialize(), cagename:''},
						function(data){
						if(data=='');
						else{
							clearTimeout(t);
							$(id+' .cageAlert').html(data);
							$(id+' .cageAlert').show();
							init();
							}
						var fadefunc="$('#cage"+i+" .cageAlert').hide('fade', {}, 200);";
						t=setTimeout(fadefunc,2000);
						},
						"text");                
					return false;});
					}
			else
				initializecage(cagename);
		}, 
		"text");
}


function refreshcage(cagename){
	var cage=$('.cage').filter(function(){return $(this).find('h1').text()==cagename;});
    if(cage.length==0)
        return false;
	var cageid=cage.attr('id');
	$.post("/database/ajax/refreshcage",
		   {cageid:cageid, cagename:cagename},
		   function(data){
			   cage.html(data);    
			   initializecage(cagename);
		   },
		   "text");
	
}

function displaycage(cagename){
    nCages=$('.cage').length;
    var exists=0;
    $('.cage h1').each(function(){if($(this).html()==cagename) exists=1;});
    if (exists==0 && cagename!='None'){
        addcage(nCages+1,cagename);}
    else if(cagename!='None'){
        refreshcage(cagename);}
}

function initializecage(cagename){ // This function sets up all the javascript after a cage is loaded
	var cage=$('.cage').filter(function(){return $(this).find('h1').text()==cagename;});
	var cageid=cage.attr('id');
	$( ".tabs" ).tabs();
	var id='#'+cageid;
	$( id+" .tabs" ).tabs({activate: function( event, ui ) {
		cageTabIdx = $( this).tabs( "option", "active" ); //This sets the cageTabIdx whenever user selects a new tab.
	}});
	$(id+' .tabs').tabs({ active: cageTabIdx }); //This opens the tab that was most recently used.
	$(id+' h1').dblclick(function(){
		if ($(this).parent().find("form").css('display') == 'none'){
			$(this).parent().find("form").css('display','block');
			$(this).parent().find(".tabs").css('display','block');
			$(this).parent().find('.residents .button-link').css('display','block');
			}
		else{
			$(this).parent().find('.residents .button-link').css('display','none');
			$(this).parent().find("form").css('display','none');
			$(this).parent().find(".tabs").css('display','none');
			}
		});
	$('.cage').draggable({cancel : 'form, .residents'}); // prevents the user from being able to drag the cage when clicking form or residents
	$(id+' form').submit(function(){
		$.post(    "/database/ajax/addcage/",
			   {data: $(id+' form').serialize(), cagename:cagename},
				function(data){
				if(data=='');
				else{
					clearTimeout(t);
					$(id+' .cageAlert').html(data);
					$(id+' .cageAlert').show();
					init();
					}
				var fadefunc="$('"+id+" .cageAlert').hide('fade', {}, 200);";
				t=setTimeout(fadefunc,2000);
				},
				"text");                
			return false; });
    $(id+" select[name='active']").change(function(){
        if($(this).val()=='No'){
                $(id+" input[name='date_inactivated']").val(getToday());
        }
    });
		
	if($(id).find('h1').text()!='New Cage'){
		var el=$(id+' .resident');
		initializeResident(el);
		cage.on('dragover', function(e){
			if (e.preventDefault) e.preventDefault(); // allows us to drop
			var oldcagename=e.originalEvent.dataTransfer.getData('oldcagename');
			if(cagename!=oldcagename){
				$(this).addClass('over');
			}
			e.originalEvent.dataTransfer.dropEffect = 'copy';
			return false;
		});
		cage.on('dragleave',function(e){
			$(this).removeClass('over');
		});
		cage.on('drop',function(e){
			var mousename=e.originalEvent.dataTransfer.getData('mousename');
			var mouseID=e.originalEvent.dataTransfer.getData('mouseID');
			var oldcagename=e.originalEvent.dataTransfer.getData('oldcagename');
			if(mousename!=''){ // if we are dropping a mouse object
				var newcage=$(this).find('h1').html();
				var newcageID=$(this).attr('id');
				if(cagename!=oldcagename){
					$(".residents .mousename").each(function(){
						if ($(this).html()==mousename)
							$(this).parent().remove();
						});
					moveMouse(mousename,mouseID,newcage,newcageID);
					}
				}
			$(this).removeClass('over');
			
		});
	}
}




//*******************************************************************************************************************************
//************************************     MOUSE STUFF      **********************************************************************
//*******************************************************************************************************************************

function moveMouse(mousename,mouseID,newcage,cageid){
	var answer;
	$.post("/database/ajax/moveMouse/",{mouseID:mouseID, newcage:newcage},function(data){
		if(data=='');
		else{
			var d=data.split(',');
			var el=$.parseHTML(d[1]);
			$('#'+cageid+' .cageAlert').html(d[0]);
			$('#'+cageid+' .cageAlert').show();
			$('#'+cageid+' .residents').append(el);   
			
			el=$('#'+cageid+' .resident');
			el=el.filter(function (){return $(this).find('.mousename').text() == mousename;});
			initializeResident(el);
			init();
		}
		t=setTimeout("$('.cageAlert').hide('fade', {}, 200);",2000);
		
	}, "text");
}
function initializeResident(el){
	el.attr("draggable",'True');
	el.on('dragstart', function(e){
		e.originalEvent.dataTransfer.effectAllowed = 'copy';
		if($(this).find('.mousename').length==1){
			e.originalEvent.dataTransfer.setData('text/plain', $(this).children(".mousename").html()); //this is for dragging into text fields
			e.originalEvent.dataTransfer.setData('mousename', $(this).children(".mousename").html());
			e.originalEvent.dataTransfer.setData('mouseID', $(this).children(".mousename").attr('mouseid'));
			e.originalEvent.dataTransfer.setData('oldcagename', $(this).parents('.cage').find('h1').html());
			}
		else{
			e.originalEvent.dataTransfer.setData('plname',$(this).children('.pl').attr('cageDOBmotherid'));}              
			e.originalEvent.dataTransfer.setData('oldcagename', $(this).parents('.cage').find('h1').html());
	});
	el.hover(
		//function(){$(this).find('img').css({'width' : '10px', 'height' : '10px'}); $(this).css({'margin-right':'0px', 'border-right-width':'0px'});  },
		//function(){$(this).find('img').css({'width' : '5px', 'height' : '5px'});      $(this).css({'margin-right':'4px', 'border-right-width':'1px'});  }
	);
	
	
	el.click(function(){
		if ($(this).find('.mousename').length==1){
			var mouseID=$(this).find('.mousename').attr('mouseID');
			$('.bubble').show();
			editmice(mouseID);
		}
		if ($(this).find('.pl').length==1){
			var plinfo=$(this).find('.pl').attr('cageDOBmotherid');
			editpl(plinfo);
		}
	});
}


function removeMouseFromCage(a){ //mouseID is the mysql ID of the mouse.  cageID is the javascript ID of the cage,  not the mysql ID

	var mouseID=$(a).parents().prev().attr('mouseid')
	var cageID=$(a).parents('.cage').attr('id')
	$.post("/database/ajax/removeMouseFromCage/",{mouseID:mouseID},                           
		function(data){
		  if(data=='');
		  else{
				$(a).parent().parent().remove();
			  clearTimeout(t);
			  $('#'+cageID+' .cageAlert').html(data);
			  $('#'+cageID+' .cageAlert').show();
			  init();
		  }
		  t=setTimeout("$('#"+cageID+" .cageAlert').hide('fade', {}, 200);",6000);
		}, "text");
}


var mouseTabIdx=0;

function editmice(mouseID){
	$.post("/database/ajax/mouseform/", {mouseID: mouseID }, function(data){
		mouseTabIdx = $( ".bubble .tabs" ).tabs( "option", "active" );
		if(mouseTabIdx.length==0){mouseTabIdx=0;}
		$('.bubble').html(data);
		$( ".tabs" ).tabs();
		$('.bubble .tabs').tabs({ active: mouseTabIdx });
		
        $(".bubble select[name='life_status']").change(function(){
            if($(this).val()=='euthanized'){
                $(".bubble input[name='DOD']").val(getToday())
            }
        });
        
        
		
		$('#editmouse').submit(function(){
            var data=$("#editmouse").serialize();
            $('.reserve_notes').each(function() {
                data+='&'+$(this).attr('name')+'='+encodeURIComponent($(this).text().trim()); //The serialize function doesn't work on the experiment notes because they are a div.  So I have to manually encode. 
            });
			$.post(    "/database/ajax/editmouse/",
					   {data: data, mouseID: mouseID},
					   function(data){
						  if(data=='');
						  else{
							  clearTimeout(t);
							  $('#mouseAlert').html(data);
							  $('#mouseAlert').show();
                              var cagename=$('#editmouse').find('[name="cagename"]').val();
                              if (cagename!='')
                                refreshcage(cagename);
							  init();
						  }
						  t=setTimeout("$('#mouseAlert').hide('fade', {}, 200);",6000);
						},
					 "text");                
			return false; });
		
		}, "text");
}	

function clickedOnMouseName(mouseID){
    $('.bubble').show();
    editmice(mouseID);
}




//*******************************************************************************************************************************
//************************************     PL STUFF      **********************************************************************
//*******************************************************************************************************************************
function addPLForm(cagename){
	$('.bubble').show();
	$.post("/database/ajax/addPLForm/",{cagename:cagename},function(data){$('.bubble').html(data);},'text');
}        

function editpl(plinfo){ //this is to display the pl form
$.post("/database/ajax/editplForm/",{plinfo:plinfo},function(data){
		$('.bubble').html(data);
		$('.bubble').show();
	},'text');
}

function editPL(fields,cagename){ // this actually edits a pl
	$.post("/database/ajax/editPL/",{fields:fields},function(data){
		$('.bubbleAlert').html(data);
		$('.bubbleAlert').show();
		refreshcage(cagename);
		},'text');
}

function addPL(fields,cagename){
	$.post("/database/ajax/addPL/",{fields:fields},function(data){
		$('.bubbleAlert').html(data);
		$('.bubbleAlert').show();
		refreshcage(cagename);
	},'text');
}     

function separatePLform(plinfo){
    $.post("/database/ajax/separatePLform/",{plinfo:plinfo},function(data){
        $('.bubble').html(data);
       },'text');
}
function separatePL(plinfo){
    $.post("/database/ajax/separatePL/",{plinfo:plinfo},function(data){
        if(data=='');
        else{
            clearTimeout(t);
            bubbleAlert=$('.bubble').find('.bubbleAlert');
            bubbleAlert.html(data)
            bubbleAlert.show();
            }
        var fadefunc="bubbleAlert.hide('fade', {}, 200);";
        t=setTimeout(fadefunc,2000);
        var cagename=plinfo.split('cagename=')[1].split('&')[0];
        refreshcage(cagename);
       },'text');
}
		
        
        

		