// Quick patches to javascript go here
$(document).ready(function() {
   $("#results .pod").each(function() {
     var nonNull = 0;
     $(this).find('img').each(function() {
       var img_src = String($(this).attr('src'));
       if (img_src.indexOf('MSP') == -1) {
         $(this).css('display', 'none').next('hr').css('display', 'none');
       } else {
         nonNull++;
       }
     });
     if (nonNull == 0) {
       $(this).css('display', 'none');
     }
   });
});

// Quick patches to javascript go here
function podOnload(id, statusCode, url){
  // removing sbsexample identifiers in case the next pod is above this one
  $.each($(".popupbutton"), function() {
    $(this).removeClass("sbsexample");
  });
  window.lastPodTime = (new Date).getTime() - window.startTime;
  if(statusCode=='success'){statusCode = 200;}
    if(statusCode=='error'){statusCode = 500;}
    var pod = $("#"+id);
    $("#pod_").remove();
    $("[id$='popup_dyn']").remove();
    pod.removeClass('subpod-showcdf');
    //if(typeof window.recalculate_loaded != undefined){
        //setTimeout(function(){ $("#recalculateBar").remove();},1000);
    //}
    $("html").removeClass("loading");
    switch(+statusCode){
      case 200:
    	  //If no pod(img) or no interactive pod(object) is returned hide pod
        if( pod.find('img, object').length == 0) { 
            pod.removeClass("loading");
            pod.hide();
        } else {
            //If this pod is interactive
            var objs = pod.find("embed");
            if(typeof objs == "undefined" || $.browser.msie)
                objs = pod.find("object");


            var count = 0;
            while(objs.get(count))
            {
                var obj = objs.get(count);
                count++;
                bindCDFPluginAutoResize(obj);
                $(".pod-interactive").removeClass("lding");
                $(".pod-interactive:not(.subpod-ascdf)", pod).hide();
                pod.find(".subpod-zoom, .subpod-saveas, .subpod-export").addClass("disabled");
	        }

            if( $('#'+id).find('div.subpod-wrap').hasClass('stubpod') ) { //Stubpods
                $('#'+id).addClass('stubpod');
            }
	        if(!$('#showsteps .sub').length > 0) {
	    	    pod.show(); 
	        }else{ 
		    if(url.indexOf("text=Step-by-step") != -1 || url.indexOf("text=StepÃ¢â‚¬ÂbyÃ¢â‚¬Âstep") != -1){
			$("#showsteps #loader").remove();	
		    }
		    
                    if ( (url.indexOf("text=Step-by-step") != -1 || url.indexOf("StepÃ¢â‚¬ÂbyÃ¢â‚¬Âstep") != -1)) {
			if($(".free-ind").length > 0){
			    if($("#"+id+".err").length > 0) {
			        appendBlurErr(id);
			        if($(".ns").height() < 305){
                                    $(".free-pod .sub-free").height(198);
                                }
			    }
			    else {
                                appendBlur(id);
			        if($(".ns").height() < 305){
                                    $(".free-pod .sub-free").height(360);
                                }
			    }
			    $(".sbs-bot .btn").hide();
                        //$("#showsteps #loader").remove();
			}
			else if($("#"+id+".err").length >0 ){
			    appendBlurErr(id);
			    if($(".ns").height() < 305){
                                    $(".free-pod .sub-free").height(198);
                            }
			    $(".sbs-bot .btn").hide();
			}
		    }
		    
	    	    pod.css("left","-99999px");
	    	    pod.show();
	        }
	     
        }
        if(pod.hasClass("premium")){pod.show();}

        /* Opera and IE6 won't trigger an onload event for an image it's already loading, thus we detect it here and force the alternate behavior.  TODO -- look for a better way to do this */
        pod.find('img').each(function(e){
            if (!this.complete && !$.browser.opera && !($.browser.msie && $.browser.version == '6.0')) {
                var img_src = String($(this).attr('src'));
                if (img_src.indexOf('MSP') == -1) {
                  if (!pod.hasClass('has-content')) {
                    pod.css('display', 'none');
                  }
                  $(this).closest('[id^=subpod]').css('display', 'none').next('hr').css('display', 'none');
                  pod.removeClass('loading');
                } else {  
                  $(this).load(function() {
                        pod.removeClass("loading").css("display","block");
                        pod.addClass('has-content');
                        //$(this).css("display", "none");
                        $(this).show();
                        //$("#answers").css("display","").css("display","block");
                        if (!(navigator.userAgent.indexOf('Safari') != -1 && navigator.userAgent.indexOf('Chrome') == -1))
                          if($(this).is('img[usemap]'))
                           {$(this).maphilight();}

  
                        setTimeout(function(){$('area[alt="Frame"]').each(function(){
                          crosshair(this);
                        });},1000);
                    
                        if($('#showsteps .sub').length > 0) {
                          pod.css("left", "auto");
                          //If no buttons on first load, this must mean it failed so revert the try taken away
                          if($('#showsteps .h').data("first") && $('#showsteps .h').data("btncount") == 0) {
                              var ssc = $.cookie("wa_sbs");
                              $.cookie("wa_sbs", ssc-1, {domain: '.wolframalpha.com', path: '/', expires: 1 });
                          }
                          if(getURLParam("noscroll", url) != 'true') {
                            $('#showsteps .sub').scrollTop($('#showsteps .sub')[0].scrollHeight);
                          }
                       }
                   }); // end of load function
                }
                
           } else {
                pod.removeClass("loading").css("display","block");
                //$("#answers").css("display","").css("display","block");
if (!(navigator.userAgent.indexOf('Safari') != -1 && navigator.userAgent.indexOf('Chrome') == -1))
                if($(this).is('img[usemap]') && !($.browser.msie && ($.browser.version == "5.0" || $.browser.version == "6.0"))){$(this).maphilight();}


                setTimeout(function(){$('area[alt="Frame"]').each(function(){
                    crosshair(this);
                });},1000);
                
                if($('#showsteps .sub').length > 0) {
                    pod.css("left", "auto"); 
                    //If no buttons on first load, this must mean it failed so revert the try taken away
                    if($('#showsteps .h').data("first") && $('#showsteps .h').data("btncount") == 0) {
                         var ssc = $.cookie("wa_sbs");
                        $.cookie("wa_sbs", ssc-1, {domain: '.wolframalpha.com', path: '/', expires: 1 });
                    }
                    if(getURLParam("noscroll", url) != 'true') {
                        $('#showsteps .sub').scrollTop($('#showsteps .sub')[0].scrollHeight);
                    }
                 }
            
            }
            /*  add scrollbars after we add map highlights to avoid strange behavior */
            if(!$(this).hasClass("ns")){
                addScrollBars(this, $(this));
            }

        }); // end of each img

        if ($.browser.msie) {
          $("#" + id).hover(function() {
            if ($.browser.version == "7.0") {
              $("#" + id).css("z-index", "11");
            }
          }, function() {
            if ($.browser.version == "7.0") {
              $("#" + id).css("z-index", "2");
            }
          });
          $("#" + id + " .note, #" + id + " .bot").mouseover(function() {
          if ($.browser.version == "6.0") {
            if ($(this).is(".note")) {
              $(this).find("em").css("display", "none");
              $(this).find("span").css("display", "inline");
            }
          }
          });
          $("#" + id + " .note, #" + id + " .bot").mouseout(function() {
          if ($.browser.version == "6.0") {
            if ($(this).is(".note")) {
              $(this).find("em").css("display", "inline");
              $(this).find("span").css("display", "none");
            }
          }
      });
        }
        // In theory, more than one progress bar could exist...in practice this won't happen
    $(".progress").stop(true).hide("slow",function(){$(this).remove();});
    if(id){ $('.assuming, #warnings, #calculateAssum').show();}

    //highlightMaxImage();
        
    break;
    case 403:

    pod.removeClass("loading");
    break;
      case 500: // TODO test these and look for better detection methods
          podRetry(id, url);
          if($("#"+id+" .output").length != 0){
          podtimeout(id, statusCode, $('#showsteps').length > 0);
              if($.browser.mozilla){
                  setTimeout(function(){ pod.find("iframe").remove(); },10000);
              }
              else {
                  pod.find("iframe").remove();
              }
    }
        else {
            pod.hide();
            if ($(".pod:visible").length == 0) {
                $('#timeout').show();
            }
    }
        $('#dbg-failed').append(id+' (timeout), ');//DEBUG: update list of failed pods
        //if (typeof debuginfo != "undefined") { debuginfo.failedpods++; debuginfo.updateall(); }

        pod.removeClass("loading");
        break;
      case 404:
        pod.removeClass("loading");
      default:
        pod.removeClass("loading");
    if(scroll == 0 && statusCode == 500){

      if ($.browser.msie && $.browser.version == "9.0" && window.XDomainRequest) {
      }
      podtimeout(id, statusCode, $('#showsteps').length > 0); 
    }
        else {
          pod.hide();
          $('#'+id.substring(4) +'_podtimeout_dyn').hide();
    }
    $('#dbg-failed').append(id+' (invalid), ');//DEBUG: update list of failed pods
        //if (typeof debuginfo != "undefined") { debuginfo.failedpods++; debuginfo.updateall(); }
        break;
    }

        //if (isDevelPro() || isCurrentPro()) {
        /*
            if (typeof user == "undefined" || user == "") {
                if (typeof drilldownlock != "undefined" && drilldownlock == "1") {
                    var clicks = $.cookie('WolframAlphaPodBtnClicks');
                    if (clicks != null && clicks >= 3) {
                        lockAllButtons(pod);
                    }
                }
            } else {
                if (exportdata == "1") {
                }
            }
            */
        //}

      // remove the first 3 subpod actions from data-attributed image pods
      /*var dataImagesSelector = '.sub map area[data-attribution], .sub map area[data-has-cdn-content]';
      pod.find(dataImagesSelector).each(function() {
      $(this).closest('.output').siblings('.subpod-controls').find('a')
             .slice(0, 3).addClass("disabled");
      });*/
      $(".progress").stop(true).hide("slow",function(){$(this).remove();});
      $("#"+id).each(function(){
//mlog("b:"+$(this).find(".copyablept").length);
         $(this).find(".copyablept").hide();
         if(jsonArray.popups[this.id.toString()]){
             for(var a=0,len=jsonArray.popups[this.id.toString()].length;a<len;a++){
                   if(jsonArray.popups[this.id.toString()][a].mOutput != "" || jsonArray.popups[this.id.toString()][a].mInput != "" || jsonArray.popups[this.id.toString()][a].stringified != "") {
                     $(this).find(".copyablept").show();
                   }
             }
         }
         //if(!Modernizr.borderradius){
           // $(this).find(".btn a").append('<i class="l"></i><i class="r"></i>');
         //}
     // $.ie6_pt is defined in ie.js
         if ($.browser.msie && $.browser.version < 7 && typeof($.ie6_pt) == "function") $.ie6_pt($("#"+id));
      });

//adding sbsexample identifier to first popupbutton
//    checking to see if pro features aside is being display
//    (i.e., whitelisted SBS)

if (isWhitelisted == 'true' && location.search.indexOf('lk=3') > -1 && localStorage.getItem("viewedSBS") != 1) {
    $(".popupbutton:first").addClass("sbsexample");
    
}

};
