"use strict";

String.prototype.replaceAll = function(search, replacement) {
  var target = this;
  return target.replace(new RegExp(search, "g"), replacement);
};

function escape_tag(text) {
  return text.replace(new RegExp("&lt;(!?)SCT:(.*?)&gt;", "g"), function(
    match,
    open,
    tag,
    offset,
    string
  ) {
    const [_, cmd, x, args] = tag.match(/^(.*?)(|:([a-zA-Z0-9_: ]*))$/, "g");
    open = open == "";
    if (!open) {
      return "</span>";
    }
    if (cmd == "COLOR") {
      return `<span style=\"color:${args.toLowerCase()}\">`;
    }
    if (cmd == "BOLD") {
      return '<span style="font-weight:bold">';
    }
    if (cmd == "HEADER") {
      return `<div class=\"sct_header\"><span>&#8649; ${args} &#8647;</span></div>`;
    }
    if (cmd == "SECTION") {
      return `<div class=\"sct_separator sct_section\"><span>&#8650; ${args} &#8650;</span></div>`;
    }
    if (cmd == "SUBSECTION") {
      return `<div class=\"sct_separator sct_subsection\"><span>&darr; ${args} &darr;</span></div>`;
    }
    return "";
  });
}
function escape(text) {
  // based on https://stackoverflow.com/a/30970751
  let lookup = {
      '&': "&amp;",
      '"': "&quot;",
      '<': "&lt;",
      '>': "&gt;"
  };
  text = text.replace( /[&"<>]/g, (c) => lookup[c] );
  text = escape_tag(text);
  return text;
}
