$(() => {
  async function getForm(id, token) {
    let response = await fetch(`${SCT_ADMIN_URL}app/setting/form/${token}/${id}/`);
    if (!response.ok)
      return null;
    let data = await response.text();
    return data;
  }
  var select = $("select[name='plugin']");
  var parent = $(".field-token").parent();
  var token = $("div.field-token>div>div.readonly").text();
  select.change(data => {
    var id = $(data.target).val();
    $("#plugin_specific_settings").remove();
    if (!id) return;
    getForm(id, token).then(ret => {
      if (!ret) return;
      parent.after(ret);
    });
  });
  select.trigger("change");
});
