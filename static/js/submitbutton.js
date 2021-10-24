$(document).ready(function() {
    $(".submit").click(function() {
      $(".submit").addClass("loading");
      setTimeout(function() {
        $(".submit").addClass("hide-loading");
        // For failed icon just replace ".done" with ".failed"
        $(".done").addClass("finish");
      }, 3000);
      setTimeout(function() {
        $(".submit").removeClass("loading");
        $(".submit").removeClass("hide-loading");
        $(".done").removeClass("finish");
        $(".failed").removeClass("finish");
      }, 5000);
    })
  });