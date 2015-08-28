
// Function for dragging and dropping resources
  $(function() {

    $( ".resource" ).draggable({ revert: "invalid",
                                                snap:".resource-container",
                                                snapMode:"inner"});
    $( ".resource-container" ).droppable({ hoverClass: "ui-state-hover" });
  });
