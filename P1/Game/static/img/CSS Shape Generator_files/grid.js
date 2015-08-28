(function($) {
    $.fn.grid = function(options) {
        var $element = this;
        
        if(typeof options == "undefined") {
            // method
            
            return $element.data('grid');
        }
        else {
            // constructor
            var viewPort = options.viewPort;
            var zoom = options.zoom;
            var step = options.step;
            
            var gridStepPx = step * zoom;
            var viewPort = $(".drawing-canvas-wrapper");
            
            var gridLines, gridOrigin, viewportWidth, viewportHeight, xMax, xMin, yMax, yMin;
            
            var update = function() {
                gridLines = {
                        positiveX: [],
                        negativeX: [],
                        positiveY: [],
                        negativeY: []
                };
                gridOrigin = $(".drawing-canvas").offset();
                viewportWidth = viewPort.width();
                viewportHeight = viewPort.height();
                
                xMax = viewportWidth - gridOrigin.left;
                xMin = -gridOrigin.left;
                yMax = viewportHeight - gridOrigin.top;
                yMin = -gridOrigin.top;
                
                
                var line;
                
                $element.empty();
                for(var x = 0; x <= xMax; x += gridStepPx) {
                    line = $('<div class="grid-line" style="width: 1px; height: ' + viewportHeight + 'px; top: '
                            + yMin + 'px; left: '
                            + x + 'px"></div>');
                    gridLines.positiveX.push(line);
                    $element.append(line);
                }
                for(var x = -gridStepPx; x >= xMin; x -= gridStepPx) {
                    line = $('<div class="grid-line" style="width: 1px; height: ' + viewportHeight + 'px; top: '
                            + yMin + 'px; left: '
                            + x + 'px"></div>');
                    gridLines.negativeX.push(line);
                    $element.append(line);
                }
                for(var y = 0; y <= yMax; y += gridStepPx) {
                    line = $('<div class="grid-line" style="width: ' + viewportWidth + 'px; height: 1px; top: '
                            + y + 'px; left: '
                            + xMin + 'px"></div>');
                    gridLines.positiveY.push(line);
                    $element.append(line);
                }
                for(var y = -gridStepPx; y >= yMin; y -= gridStepPx) {
                    line = $('<div class="grid-line" style="width: ' + viewportWidth + 'px; height: 1px; top: '
                            + y + 'px; left: '
                            + xMin + 'px"></div>');
                    gridLines.negativeY.push(line);
                    $element.append(line);
                }
            };
            
            update();
            $(window).resize(update);
            
            
            $element.data('grid', {
                unHighlightLines: function() {
                    $element.children(".highlight").removeClass("highlight");
                },
                highlightLinesAtPosition: function(position) {
                    this.unHighlightLines();
                    var line, i;
                    
                    i = position.x;
                    line = i >= 0 ? gridLines.positiveX[i] : gridLines.negativeX[-1 - i];
                    if(line) line.addClass("highlight");
                    
                    i = position.y;
                    line = i >= 0 ? gridLines.positiveY[i] : gridLines.negativeY[-1 - i];
                    if(line) line.addClass("highlight");
                }
            });
            
            return this;
        }
    };
})(jQuery);