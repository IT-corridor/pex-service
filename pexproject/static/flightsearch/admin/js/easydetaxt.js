 //base_url = "";
$(document).ready(function(){
	
	var admin_language='english';
	if(typeof $.cookie('admin_language')!='undefined'){
		admin_language=$.cookie('admin_language');
	} 
	setLanguageCookie(admin_language);
	
});


	$(".languagechang").click(function(){  
			var  admin_language=$(this).attr('id');
			setLanguageCookie( admin_language);
			redirect();
	});

	function setLanguageCookie(admin_language){
		if(typeof  admin_language!='undefined'){
			var setImagepath='';
			if($.trim(admin_language)=="english"){
				setImagepath=base_url+"/images/flag-uk.png";
			}else if($.trim(admin_language)=="french"){ 
				setImagepath=base_url+"/images/flag-fr.png";
			}else{
				setImagepath=base_url+"/images/flag-uk.png";
			}
			
		}else{
			setImagepath=base_url+"/images/flag-uk.png";
			 admin_language="english";
		}
		$("#change_language_image").attr("src",setImagepath);
		$.cookie('admin_language', admin_language);

		
		
	}

	 function redirect(){ 
	 	window.location.reload();
	 }


$("#showhidestatusfrm").click(function(){
	$("#addstatus").hide();
	//$("#showhidestatusfrm").hide();
	$("#addstatusform").show()
	$("#statusbutton").show();
});
$("#cancleform").click(function(){
	$("#addstatus").show();
	$("#addstatusform").hide();
	$("#statusbutton").hide();
});
//*** varify ammount field show or not in manage trip status form **/
$("#status").change(function(){
	var status=$("#status").val();
	var statusval=status.split('#');
	if(statusval[1]==5){
		$("#amount_field").show();
	}else{
		$("#amount_field").hide();
	}
});

/**** Triplist filtered by status and date  **/

$(".triplistfilter").change(function(){
	var status_id=$("#status_filter").val();
	
	var csrf=$("#csrf").val();
	//if(date!='' || status_id!=''){
	filtertriplist(status_id,csrf);
	//}
});

function filtertriplist(status_id,csrf){
	$.ajax({ 
	       type: "POST",
	       url: "triplist/getfilteredtriplist", 
	       data: {"status_id":status_id,"_csrf" :csrf}, 
	       })
	       .done(function( response ) { 
	    	   var obj =  jQuery.parseJSON(response) ;
	    	   
	    	  var  html='';
	    	   $("#changeon_filter").empty();
	    	   if(obj.status==1){
	    		   if((obj.data).length >0){
	    			   
	    			   for(var i=0;i<(obj.data).length;i++){
	    				   html +="<tr><td>"+(i+1) +"</td>";
	    				   html +="<td>"+ obj.data[i].first_name +' ' + obj.data[i].last_name +"</td>";
	    				   html +="<td>"+ obj.data[i].date +"</td>";
	    				   html +="<td>"+obj.data[i].airportlist[0]+', '+ obj.data[i].airportlist[1] +"</td>";
	    				   html +="<td>"+ obj.data[i].status+"</td>";
	    				   html +="<td><a class='btn btn-default btn-sm btn-icon icon-left' href='"+base_url+"/managestatus?act=edit&journey_detail_id="+obj.data[i].journey_detail_id+"'>";
	    				   html +="<i class='entypo-pencil'></i>"+ obj.data[i].button_name +"</a></td></tr>";
	    			   }
	    			   
	    		   }
	    	 
	    	   }else{
	    		   html="<tr><td colspan='5'>"+ obj.data +"</td></tr>";
	    	   }
	    	   $("#changeon_filter").append(html);
	    	   
	       });
}


//CKeditor WYSIWYG
/*if($.isFunction($.fn.ckeditor))
{
	$(".ckeditor").ckeditor({
	//	contentsLangDirection: rtl() ? 'rtl' : 'ltr',
		//config.extraPlugins = 'divarea',
	});
}*/


/*** Manage Blog URL  ***
 */
$("#blog_title_id").keyup(function(){
	blogurlmaker();
	
}); 

function blogurlmaker(){
	
	var bloggivenurl=$("#blog_title_id").val();
	var bloggivenurl1=bloggivenurl.replace(/[^a-z0-9\s]/gi, '').replace(/[_\s]/g, '-');
	var blog_url_string=bloggivenurl1.replace(/\s+/g, '-');
	var blog_url=blog_url_string.toLowerCase();
	$("#show_blog_url").empty();
	$("#show_blog_url").append(blog_url); 
	$("#blog_name_id").val('');
	$("#blog_name_id").val(blog_url);
}
 

