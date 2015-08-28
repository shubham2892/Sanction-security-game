(function($) {
    $.fn.shapeClassLibrary = function(options) {
        var $element = this;
        
        if(typeof options == "undefined") {
            // method
            
            return $element.data('shapeClassLibrary');
        }
        else {
            // constructor
            
            var shapeClasses = options.shapeClasses;
            var libraryShapeSize = options.libraryShapeSize;
            var shapeSelectedCallback = function() {};
            
            var update = function(color) {
            	$element.empty();
            	_.each(shapeClasses, function(shapeClass) {
            		var css = shapeClass.generateCss("px", libraryShapeSize, color, shapeClass.getUnitParameters());
            		$element.append(
            				$('<div class="wrapper"></div>')
            				.data('shapeClass', shapeClass)
            				.append($('<i></i>').css(css)).click(function() {
            					shapeSelectedCallback(shapeClass);
            				}));
            	});
            };
            
            update(options.color);
            
            $element.data('shapeClassLibrary', {
                setSelectedClass: function(selectedShapeClass) {
                    $element.children(".wrapper").each(function() {
                        var shapeClass = $(this).data('shapeClass');
                        $(this).toggleClass("selected", selectedShapeClass === shapeClass);
                    });
                },
                setSelectionHandler: function(callback) {
                    shapeSelectedCallback = callback;
                },
                setColor: function(color) {
                	update(color);
                }
            });
            
            return this;
        }
    };
})(jQuery);