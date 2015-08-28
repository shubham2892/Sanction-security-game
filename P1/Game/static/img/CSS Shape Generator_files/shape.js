var Shape;
var shapeClasses;

/*****************************  Shape implementation  **************************************/

(function() {

    var COMMON_PROPERTIES = {
        "display" : "inline-block"
    };
    
    var AbstractCornerAction = function(overrides) {
        _.extend(this, overrides);
    };
    AbstractCornerAction.prototype = {
        createContext: function(shape, position) {
            var size = shape.getSize();
            return {
                position: {
                    x: shape.position.x + size.width * (1 - this.handle.x), 
                    y: shape.position.y + size.height * (1 - this.handle.y)
                }
            };
        },
        progress: function(shape, context, position) {
            var parameters = shape.parameters;
            var shapePosition = shape.position;
            var shapeClass = shape.shapeClass;
            var pointerPosition = position;
            
            this.updateSizeParameters(shape, context, position);
            
            var size = shapeClass.getSize(parameters);
            
            if(pointerPosition.x < context.position.x) shapePosition.x = context.position.x - size.width;
            else shapePosition.x = context.position.x;
            
            if(pointerPosition.y < context.position.y) shapePosition.y = context.position.y - size.height;
            else shapePosition.y = context.position.y;
        },
        getFeedback: function(shape, context) {
            var position = shape.position;
            var size = shape.getSize();
            return {
                type: "rectangle",
                x: position.x,
                y: position.y,
                width: size.width,
                height: size.height
            };
        }
    };
    
    var FixedRatioCornerAction = function(x, y, style) {
        AbstractCornerAction.call(this, {handle: {x: x, y: y}, style: style});
    };
    FixedRatioCornerAction.prototype = new AbstractCornerAction({
        updateSizeParameters: function(shape, context, position) {
            var parameters = shape.parameters;
            var shapeClass = shape.shapeClass;
            var pointerPosition = position;
            
            var width = Math.round(Math.abs(pointerPosition.x - context.position.x) / shapeClass.widthRatio);
            var height = Math.round(Math.abs(pointerPosition.y - context.position.y) / shapeClass.heightRatio);
            
            parameters.size = Math.min(width, height);
        }
    });
    
    var VariableRatioCornerAction = function(x, y, style) {
        AbstractCornerAction.call(this, {handle: {x: x, y: y}, style: style});
    };
    VariableRatioCornerAction.prototype = new AbstractCornerAction({
        updateSizeParameters: function(shape, context, position) {
            var parameters = shape.parameters;
            var pointerPosition = position;
            
            var width = Math.round(Math.abs(pointerPosition.x - context.position.x));
            var height = Math.round(Math.abs(pointerPosition.y - context.position.y));
            
            parameters.width = width;
            parameters.height = height;
        }
    });
    
    var DragAction = function(x, y) {};
    DragAction.prototype.createContext = function(shape, position) {
        return {
            shapeStartPosition: {x: shape.position.x, y: shape.position.y},
            dragStartPosition: {x: position.x, y: position.y},
        };
    };
    DragAction.prototype.progress = function(shape, context, position) {
        shape.position.x = context.shapeStartPosition.x + position.x - context.dragStartPosition.x;
        shape.position.y = context.shapeStartPosition.y + position.y - context.dragStartPosition.y;
    };
    DragAction.prototype.getFeedback = function(shape, context) {
        return null;
    };
    DragAction.prototype.style = "move";
    DragAction.prototype.handle = null;
    
    
    var FIXED_RATIO_SHAPE_ACTIONS = [
        new DragAction(0.5, 0.5), 
        new FixedRatioCornerAction(0, 0, 'nw-resize'), 
        new FixedRatioCornerAction(0, 1, 'sw-resize'), 
        new FixedRatioCornerAction(1, 0, 'ne-resize'), 
        new FixedRatioCornerAction(1, 1, 'se-resize')
    ];
    
    var VARIABLE_RATIO_SHAPE_ACTIONS = [
        new DragAction(0.5, 0.5), 
        new VariableRatioCornerAction(0, 0, 'nw-resize'), 
        new VariableRatioCornerAction(0, 1, 'sw-resize'), 
        new VariableRatioCornerAction(1, 0, 'ne-resize'), 
        new VariableRatioCornerAction(1, 1, 'se-resize')
    ];
    
    var AbstractShapeClass = function(overrides) {
        _.extend(this, overrides);
    };
    AbstractShapeClass.prototype = {
        hitTest: function(shapePosition, parameters, position) {
            var dx = position.x - shapePosition.x;
            var dy = position.y - shapePosition.y;
            if(dx <= 0 || dy <= 0) {
                return false;
            }
            else {
                var size = this.getSize(parameters);
                if(dx >= size.width || dy >= size.height) {
                    return false;
                }
                else {
                    return this.hitTestInBounds(dx / size.width, dy / size.height);
                }
            }
        },
        hitTestInBounds: function(x, y) {
            return true;
        }
    };

    var VariableRatioShapeClass = function(overrides) {
        AbstractShapeClass.call(this, overrides);
    };
    VariableRatioShapeClass.prototype = new AbstractShapeClass({
    	length: 2,
        getDefaultParameters: function() {
            return {width: 0, height: 0};
        },
        getUnitParameters: function() {
            return {width: 1, height: 0.75};
        },
        getEditionActions: function() {
            return VARIABLE_RATIO_SHAPE_ACTIONS;
        },
        getSize: function(parameters) {
            return {width: parameters.width, height: parameters.height};
        },
        getCreationAction: function() {
            return new VariableRatioCornerAction(1, 1);
        }
    });

    
    var FixedRatioShapeClass = function(overrides) {
        AbstractShapeClass.call(this, overrides);
    };
    FixedRatioShapeClass.prototype = new AbstractShapeClass({
    	length: 1,
        widthRatio: 1,
        heightRatio: 1,
        getDefaultParameters: function() {
            return {size: 0};
        },
        getUnitParameters: function() {
            return {size: 1};
        },
        getEditionActions: function() {
            return FIXED_RATIO_SHAPE_ACTIONS;
        },
        getSize: function(parameters) {
            return {width: parameters.size * this.widthRatio, height: parameters.size * this.heightRatio};
        },
        getCreationAction: function() {
            return new FixedRatioCornerAction(1, 1);
        }
    });
    
    shapeClasses = [];
    
    var registerClass = function(shapeClass) {
    	shapeClass.id = shapeClasses.length;
    	shapeClasses.push(shapeClass);
    };
    
    registerClass(new VariableRatioShapeClass({
        // rectangle
        generateCss : function(unit, zoom, color, parameters) {
            var result = _.extend({}, COMMON_PROPERTIES, {
                "width" : (parameters.width * zoom) + unit,
                "height" : (parameters.height * zoom) + unit,
                "background-color" : color
            });
            return result;
        }
    }));

    var commonTrianglesCallback = function(unit, size, backgroundColor) {
    	// rectangle
        backgroundColor = backgroundColor || 'transparent';
        return _.extend({}, COMMON_PROPERTIES, {
            "width" : 0,
            "height" : 0,
            "line-height" : 0,
            "border" : size + unit + " solid " + backgroundColor
        });
    };

    var commonRoundTrianglesCallback = function(unit, size, backgroundColor) {
        backgroundColor = backgroundColor || 'transparent';
        return _.extend({}, COMMON_PROPERTIES, {
            "width" : 0,
            "height" : 0,
            "line-height" : 0,
            "border" : size + unit + " solid " + backgroundColor,
            "border-radius" : size + unit
        });
    };
    
    var wrapCircleHitTest = function(hitTest) {
    	return function(x, y) {
    		return hitTest(x, y) && (x - 0.5) * (x - 0.5) + (y - 0.5) * (y - 0.5) < 0.25;
    	};
    };
    
    registerClass(new FixedRatioShapeClass({
        // square
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonTrianglesCallback(unit, size, color), {
            	"border-bottom" : size + unit + " solid " + color
            });
        }
    }));

    registerClass(new FixedRatioShapeClass({
        // top arrow
        heightRatio: 0.5,
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonTrianglesCallback(unit, size), {
                "margin-top" : "-" + size + unit,
                "border-bottom" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: function(x, y) {
    		return y > Math.abs(1 - 2 * x);
    	}
    }));

    registerClass(new FixedRatioShapeClass({
        // left arrow
        widthRatio: 0.5,
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonTrianglesCallback(unit, size), {
                "margin-left" : "-" + size + unit,
                "border-right" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: function(x, y) {
    		return x > Math.abs(1 - 2 * y);
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // right arrow
        widthRatio: 0.5,
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonTrianglesCallback(unit, size), {
                "border-left" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: function(x, y) {
            return 1 - x > Math.abs(1 - 2 * y); 
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // bottom arrow
        heightRatio: 0.5,
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonTrianglesCallback(unit, size), {
                "border-top" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: function(x, y) {
            return 1 - y > Math.abs(1 - 2 * x); 
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // top+bottom arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonTrianglesCallback(unit, size), {
                "border-top" : size + unit + " solid " + color,
                "border-bottom" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: function(x, y) {
            return Math.abs(1 - 2 * x) < Math.abs(1 - 2 * y); 
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // left+right arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonTrianglesCallback(unit, size), {
                "border-left" : size + unit + " solid " + color,
                "border-right" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: function(x, y) {
            return Math.abs(1 - 2 * x) > Math.abs(1 - 2 * y); 
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // top-left arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonTrianglesCallback(unit, size), {
                "border-left" : size + unit + " solid " + color,
                "border-top" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: function(x, y) {
            return x < 1 - y; 
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // top-right arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonTrianglesCallback(unit, size), {
                "border-right" : size + unit + " solid " + color,
                "border-top" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: function(x, y) {
            return x > y; 
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // right-bottom arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonTrianglesCallback(unit, size), {
                "border-right" : size + unit + " solid " + color,
                "border-bottom" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: function(x, y) {
            return x > 1 - y; 
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // left-bottom arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonTrianglesCallback(unit, size), {
                "border-left" : size + unit + " solid " + color,
                "border-bottom" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: function(x, y) {
            return x < y; 
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // inverse top arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonTrianglesCallback(unit, size, color), {
                "border-bottom" : size + unit + " solid transparent"
            });
        },
        hitTestInBounds: function(x, y) {
            return y < 1 - x || y < x;
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // inverse bottom arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonTrianglesCallback(unit, size, color), {
                "border-top" : size + unit + " solid transparent"
            });
        },
        hitTestInBounds: function(x, y) {
            return y > 1 - x || y > x; 
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // inverse left arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonTrianglesCallback(unit, size, color), {
                "border-right" : size + unit + " solid transparent"
            });
        },
        hitTestInBounds: function(x, y) {
            return x < 1 - y || x < y;
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // inverse right arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonTrianglesCallback(unit, size, color), {
                "border-left" : size + unit + " solid transparent"
            });
        },
        hitTestInBounds: function(x, y) {
            return x > 1 - y || x > y;
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // circle
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonRoundTrianglesCallback(unit, size, color), {});
        },
        hitTestInBounds: wrapCircleHitTest(function() {return true;})
    }));
    
    registerClass(new VariableRatioShapeClass({
        // oval
        generateCss : function(unit, zoom, color, parameters) {
            var w = (parameters.width * zoom) / 2;
            var h = (parameters.height * zoom) / 2;
            return _.extend({}, COMMON_PROPERTIES, {
                "width" : 0,
                "height" : 0,
                "line-height" : 0,
                "border-top": h + unit + " solid " + color,
                "border-bottom": h + unit + " solid " + color,
                "border-left": w + unit + " solid " + color,
                "border-right": w + unit + " solid " + color,
                "border-radius" : w + unit + " / " + h + unit
            });
        },
        hitTestInBounds: wrapCircleHitTest(function() {return true;})
    }));

    registerClass(new FixedRatioShapeClass({
        // ne cricle quarter
        generateCss : function(unit, zoom, color, parameters) {
            var size = parameters.size * zoom;
            return _.extend({}, commonTrianglesCallback(unit, size, color), {
            	"border-top": "none",
            	"border-left": "none",
	            "border-bottom-right-radius": size + unit
            });
        },
        hitTestInBounds: function(x, y) {
        	return x * x + y * y < 1;
        }
    }));

    registerClass(new FixedRatioShapeClass({
        // nw cricle quarter
        generateCss : function(unit, zoom, color, parameters) {
            var size = parameters.size * zoom;
            return _.extend({}, commonTrianglesCallback(unit, size, color), {
            	"border-top": "none",
            	"border-right": "none",
	            "border-bottom-left-radius": size + unit
            });
        },
        hitTestInBounds: function(x, y) {
        	return (1-x) * (1-x) + y * y < 1;
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // se cricle quarter
        generateCss : function(unit, zoom, color, parameters) {
            var size = parameters.size * zoom;
            return _.extend({}, commonTrianglesCallback(unit, size, color), {
            	"border-bottom": "none",
            	"border-left": "none",
	            "border-top-right-radius": size + unit
            });
        },
        hitTestInBounds: function(x, y) {
        	return x * x + y * y < 1;
        }
    }));

    registerClass(new FixedRatioShapeClass({
        // sw cricle quarter
        generateCss : function(unit, zoom, color, parameters) {
            var size = parameters.size * zoom;
            return _.extend({}, commonTrianglesCallback(unit, size, color), {
            	"border-bottom": "none",
            	"border-right": "none",
	            "border-top-left-radius": size + unit
            });
        },
        hitTestInBounds: function(x, y) {
        	return (1-x) * (1-x) + y * y < 1;
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // left circle half
    	widthRatio: 0.5,
        generateCss : function(unit, zoom, color, parameters) {
            var size = parameters.size * zoom / 2;
            return _.extend({}, commonTrianglesCallback(unit, size, color), {
            	"border-right": "none",
            	"border-bottom-left-radius": size + unit,
	            "border-top-left-radius": size + unit
            });
        },
        hitTestInBounds: function(x, y) {
        	return ((1-x)/2) * ((1-x)/2) + (y - 0.5) * (y - 0.5) < 0.25;;
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // right circle half
    	widthRatio: 0.5,
        generateCss : function(unit, zoom, color, parameters) {
            var size = parameters.size * zoom / 2;
            return _.extend({}, commonTrianglesCallback(unit, size, color), {
            	"border-left": "none",
            	"border-bottom-right-radius": size + unit,
	            "border-top-right-radius": size + unit
            });
        },
        hitTestInBounds: function(x, y) {
        	return (x/2) * (x/2) + (y - 0.5) * (y - 0.5) < 0.25;
        }
    }));

    registerClass(new FixedRatioShapeClass({
        // top circle half
    	heightRatio: 0.5,
        generateCss : function(unit, zoom, color, parameters) {
            var size = parameters.size * zoom / 2;
            return _.extend({}, commonTrianglesCallback(unit, size, color), {
            	"border-bottom": "none",
            	"border-top-right-radius": size + unit,
	            "border-top-left-radius": size + unit
            });
        },
        hitTestInBounds: function(x, y) {
        	return ((1-y)/2) * ((1-y)/2) + (x - 0.5) * (x - 0.5) < 0.25;;
        }
    }));
    
    registerClass(new FixedRatioShapeClass({
        // bottom circle half
    	heightRatio: 0.5,
        generateCss : function(unit, zoom, color, parameters) {
            var size = parameters.size * zoom / 2;
            return _.extend({}, commonTrianglesCallback(unit, size, color), {
            	"border-top": "none",
            	"border-bottom-right-radius": size + unit,
	            "border-bottom-left-radius": size + unit
            });
        },
        hitTestInBounds: function(x, y) {
        	return (y/2) * (y/2) + (x - 0.5) * (x - 0.5) < 0.25;
        }
    }));
    

    
    
    
    registerClass(new FixedRatioShapeClass({
        // round top arrow
        heightRatio: 0.5,
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonRoundTrianglesCallback(unit, size), {
                "margin-top" : "-" + size + unit,
                "border-bottom" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: function(x, y) {
    		return y > Math.abs(1 - 2 * x) && (x - 0.5) * (x - 0.5) + (y/2) * (y/2) < 0.25;
    	}
    }));

    registerClass(new FixedRatioShapeClass({
    	// round left arrow
        widthRatio: 0.5,
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonRoundTrianglesCallback(unit, size), {
                "margin-left" : "-" + size + unit,
                "border-right" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: function(x, y) {
    		return x > Math.abs(1 - 2 * y) && (y - 0.5) * (y - 0.5) + (x/2) * (x/2) < 0.25;
    	}
    }));
    
    registerClass(new FixedRatioShapeClass({
    	// round right arrow
        widthRatio: 0.5,
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonRoundTrianglesCallback(unit, size), {
                "border-left" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: wrapCircleHitTest(function(x, y) {
            return 1 - x > Math.abs(1 - 2 * y); 
        })
    }));
    
    registerClass(new FixedRatioShapeClass({
    	// round bottom arrow
        heightRatio: 0.5,
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonRoundTrianglesCallback(unit, size), {
                "border-top" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: wrapCircleHitTest(function(x, y) {
            return 1 - y > Math.abs(1 - 2 * x); 
        })
    }));
    
    registerClass(new FixedRatioShapeClass({
    	// round top+bottom arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonRoundTrianglesCallback(unit, size), {
                "border-top" : size + unit + " solid " + color,
                "border-bottom" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: wrapCircleHitTest(function(x, y) {
            return Math.abs(1 - 2 * x) < Math.abs(1 - 2 * y); 
        })
    }));
    
    registerClass(new FixedRatioShapeClass({
    	// round left+right arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonRoundTrianglesCallback(unit, size), {
                "border-left" : size + unit + " solid " + color,
                "border-right" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: wrapCircleHitTest(function(x, y) {
            return Math.abs(1 - 2 * x) > Math.abs(1 - 2 * y); 
        })
    }));
    
    registerClass(new FixedRatioShapeClass({
    	// round top-left arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonRoundTrianglesCallback(unit, size), {
                "border-left" : size + unit + " solid " + color,
                "border-top" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: wrapCircleHitTest(function(x, y) {
            return x < 1 - y; 
        })
    }));
    
    registerClass(new FixedRatioShapeClass({
    	// round top-right arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonRoundTrianglesCallback(unit, size), {
                "border-right" : size + unit + " solid " + color,
                "border-top" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: wrapCircleHitTest(function(x, y) {
            return x > y; 
        })
    }));
    
    registerClass(new FixedRatioShapeClass({
    	// round right-bottom arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonRoundTrianglesCallback(unit, size), {
                "border-right" : size + unit + " solid " + color,
                "border-bottom" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: wrapCircleHitTest(function(x, y) {
            return x > 1 - y; 
        })
    }));
    
    registerClass(new FixedRatioShapeClass({
    	// round left-bottom arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonRoundTrianglesCallback(unit, size), {
                "border-left" : size + unit + " solid " + color,
                "border-bottom" : size + unit + " solid " + color
            });
        },
        hitTestInBounds: wrapCircleHitTest(function(x, y) {
            return x < y; 
        })
    }));
    
    registerClass(new FixedRatioShapeClass({
    	// round inverse top arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonRoundTrianglesCallback(unit, size, color), {
                "border-bottom" : size + unit + " solid transparent"
            });
        },
        hitTestInBounds: wrapCircleHitTest(function(x, y) {
            return y < 1 - x || y < x;
        })
    }));
    
    registerClass(new FixedRatioShapeClass({
    	// round inverse bottom arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonRoundTrianglesCallback(unit, size, color), {
                "border-top" : size + unit + " solid transparent"
            });
        },
        hitTestInBounds: wrapCircleHitTest(function(x, y) {
            return y > 1 - x || y > x; 
        })
    }));
    
    registerClass(new FixedRatioShapeClass({
    	// round inverse left arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonRoundTrianglesCallback(unit, size, color), {
                "border-right" : size + unit + " solid transparent"
            });
        },
        hitTestInBounds: wrapCircleHitTest(function(x, y) {
            return x < 1 - y || x < y;
        })
    }));
    
    registerClass(new FixedRatioShapeClass({
    	// round inverse right arrow
        generateCss : function(unit, zoom, color, parameters) {
            var size = (parameters.size * zoom) / 2;
            return _.extend({}, commonRoundTrianglesCallback(unit, size, color), {
                "border-left" : size + unit + " solid transparent"
            });
        },
        hitTestInBounds: wrapCircleHitTest(function(x, y) {
            return x > 1 - y || x > y;
        })
    }));

    Shape = function(shapeClass, initialColor, position) {
        Shape.currentId = (Shape.currentId || 0) + 1;
        this.id = Shape.currentId;
        
        this.shapeClass = shapeClass;
        this.color = initialColor;
        this.parameters = shapeClass.getDefaultParameters();
        this.position = {x: position.x, y: position.y};
    };
    Shape.prototype.generateCss = function(unit, zoom, selected) {
    	var color = this.color;
    	if(selected) {
    		var percent = 25;
		    var num = parseInt(color.slice(1),16), amt = Math.round(2.55 * percent), R = (num >> 16) + amt, B = (num >> 8 & 0x00FF) + amt, G = (num & 0x0000FF) + amt;
		    color = "#" + (0x1000000 + (R<255?R<1?0:R:255)*0x10000 + (B<255?B<1?0:B:255)*0x100 + (G<255?G<1?0:G:255)).toString(16).slice(1);
    	}
        return this.shapeClass.generateCss(unit, zoom, color, this.parameters);
    };
    Shape.prototype.getSize = function() {
        return this.shapeClass.getSize(this.parameters);
    };
    Shape.prototype.hitTest = function(position) {
        return this.shapeClass.hitTest(this.position, this.parameters, position);
    };
    Shape.prototype.getEditionActions = function() {
        return this.shapeClass.getEditionActions();
    };
    Shape.prototype.getCreationAction = function() {
        return this.shapeClass.getCreationAction();
    };
})();
