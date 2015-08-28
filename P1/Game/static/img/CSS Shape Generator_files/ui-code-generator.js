(function($) {
    var abstractGenerate = function(shapes, width, height, unit, hooks) {
        var bounds = {x: null, y: null, width: null, height: null};
        _.each(shapes, function(shape) {
            if(bounds.x == null || shape.position.x < bounds.x) bounds.x = shape.position.x;
            if(bounds.y == null || shape.position.y < bounds.y) bounds.y = shape.position.y;
            var size = shape.getSize();
            if(bounds.width == null || shape.position.x + size.width > bounds.x + bounds.width) bounds.width = shape.position.x + size.width - bounds.x;
            if(bounds.height == null || shape.position.y + size.height > bounds.y + bounds.height) bounds.height = shape.position.y + size.height - bounds.y;
        });
        
        var dx = 0;
        var dy = 0;
        var zoom = width / bounds.width;
        
        var context = {
            bounds: bounds,
            dx: dx,
            dy: dy,
            zoom: zoom
        };
        
        _.each(shapes, function(shape) {
            
            if(hooks.shapeBegin) hooks.shapeBegin(context, shape);
            
            var shapeCss = shape.generateCss(unit, zoom);
            _.each(shapeCss, function(value, key) {
                if(hooks.handleShapeProperty) hooks.handleShapeProperty(context, shape, key, value);
            });
            
            if(hooks.shapeEnd) hooks.shapeEnd(context, shape);
        });
    };

    
    var generateStandaloneHtml = function(shapes, width, height, unit) {
        var sb = [];
        sb.push('<span style="display: inline-block; width: ', width, unit, '; height: ', height, unit + '">');
        sb.push('<span style="position: relative; display: inline-block; width: ', width, unit, '; height: ', height, unit + '">');
        
        abstractGenerate(shapes, width, height, unit, {
            shapeBegin: function(context, shape) {
                sb.push('<i style="position: absolute');
            },
            handleShapeProperty: function(context, shape, key, value) {
                sb.push(";", key, ":", value);
            },
            shapeEnd: function(context, shape) {
                sb.push(";left:", (shape.position.x - context.bounds.x) * context.zoom + context.dx, unit);
                sb.push(";top:", (shape.position.y - context.bounds.y) * context.zoom + context.dy, unit);
                sb.push('"></i>');
            }
        });
        
        sb.push('</span>');
        sb.push('</span>');
        return sb.join('');
    };
    
    var generateCssAndHtml = function(shapes, width, height, unit, class_) {
        var cssSb = [];
        var lessSb = [];
        var htmlSb = [];
        
        cssSb.push('.', class_, ' {\n');
        cssSb.push('    position: relative;\n');
        cssSb.push('}\n');
        
        htmlSb.push('<i class="', class_, '">');

        var i = "i";
        
        abstractGenerate(shapes, width, height, unit, {
            shapeBegin: function(context, shape) {
                htmlSb.push('<i></i>');
                cssSb.push('.', class_, ' > ',i, ' {\n');
                cssSb.push("    position: absolute;");
            },
            handleShapeProperty: function(context, shape, key, value) {
                cssSb.push("\n    ", key, ": ", value, ';');
            },
            shapeEnd: function(context, shape) {
                cssSb.push("\n    left: ", (shape.position.x - context.bounds.x) * context.zoom + context.dx, unit, ';');
                cssSb.push("\n    top: ", (shape.position.y - context.bounds.y) * context.zoom + context.dy, unit, ';');
                cssSb.push('\n}\n');
                i = i + "+i";
            }
        });
        
        htmlSb.push('</i>');
        
        return {html: htmlSb.join(''), css: cssSb.join('')};
    };
    
    var selectOnFocus = function($element) {
        $element.focus(function() {
            var $this = $(this);
            $this.select();

            // Work around Chrome's little problem
            $this.mouseup(function() {
                // Prevent further mouseup intervention
                $this.unbind("mouseup");
                return false;
            });
        });
        return $element;
    };
    
    $.fn.codeGenerator = function(options) {
        var $element = this;
        
        if(typeof options == "undefined") {
            // method
            
            return $element.data('codeGenerator');
        }
        else {
            // constructor
            var widthInput = $element.find(".input-width");
            var heightInput = $element.find(".input-height");
            var unitInput = $element.find(".input-unit");
            var classInput = $element.find(".input-class");
            
            var standaloneHtmlTextArea = $element.find(".output-standalone-html");
            var htmlTextArea = $element.find(".output-html");
            var cssTextArea = $element.find(".output-css");
            
            selectOnFocus(widthInput);
            selectOnFocus(heightInput);
            selectOnFocus(unitInput);
            selectOnFocus(classInput);
            
            selectOnFocus(standaloneHtmlTextArea);
            selectOnFocus(htmlTextArea);
            selectOnFocus(cssTextArea);
            
            widthInput.val("3");
            heightInput.val("3");
            unitInput.val("em");
            classInput.val("my-icon");
            
            standaloneHtmlTextArea.val("Start drawing, code generation will follow.");
            htmlTextArea.val("Start drawing, code generation will follow.");
            cssTextArea.val("Start drawing, code generation will follow.");
            
            var currentShapes = [];
            
            $element.data('codeGenerator', {
                update: function(shapes) {
                	currentShapes = shapes;
                    var width = parseFloat(widthInput.val(), 10);
                    var height = parseFloat(heightInput.val(), 10);
                    var unit = unitInput.val();
                    var class_ = classInput.val();
                    
                    var standaloneHtml = null;
                    
                    if(isNaN(width)) standaloneHtml = "Invalid width";
                    else if(isNaN(height)) standaloneHtml = "Invalid height";
                    else standaloneHtml = generateStandaloneHtml(shapes, width, height, unit);
                    
                    standaloneHtmlTextArea.val(standaloneHtml);
                    
                    var cssAndHtml;
                    
                    if(isNaN(width)) cssAndHtml = {css: "Invalid width", html: "Invalid width"};
                    else if(isNaN(height)) cssAndHtml = {css: "Invalid height", html: "Invalid height"};
                    else cssAndHtml = generateCssAndHtml(shapes, width, height, unit, class_);
                    
                    htmlTextArea.val(cssAndHtml.html);
                    cssTextArea.val(cssAndHtml.css);
                }
            });
            
            var update = function() {
                $element.data('codeGenerator').update(currentShapes);
            };
            
            widthInput.change(update);
            heightInput.change(update);
            unitInput.change(update);
            classInput.change(update);
            
            return this;
        }
    };
})(jQuery);