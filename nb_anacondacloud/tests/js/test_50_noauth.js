var t = casper.test;

function noauth_test(){

  this.baseline_notebook();

  this.runCell(1, [
    "from binstar_client.utils import dirs, get_binstar",
    "!jupyter --paths",
    "!find $HOME",
    "print(dirs.user_data_dir)",
    "print(get_binstar().user())"
  ]);

  //this.runCell(["!anaconda logout"]);

  this.canSeeAndClick("ua the nbac button", "#publish_notebook")
    .waitForSelectorTextChange("#notification_notebook", function(){
      console.error("selector text changed");
      return this;
    })
    .canSeeAndClick("the notification area", "#notification_notebook")
    .canSeeAndClick("the modal", ".modal")
    .canSeeAndClick("the unauthorized message", "h4.modal-title")
    .then(function(){
      t.assertSelectorHasText(" h4.modal-title", "Unauthorized");
    })
    .canSeeAndClick("the dismiss button",
      ".modal .btn[data-dismiss=modal]");
}

casper.notebook_test(function(){
  casper.screenshot.init("50_noauth");
  casper.viewport(1440, 900)
    .then(noauth_test)
});
