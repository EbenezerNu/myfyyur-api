window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

$(document).ready(function () {
  var path = location.pathname;
  if (path.search(/edit/i) != -1) {
    console.log("Genres are been selected:");
    var raw = document.getElementById("genresSelect").innerText;
    let result = raw.substring(1, raw.length - 1);
    let spl = result.replace(/'/g, "");
    let arr1 = spl.split(",");
    let arr = [];
    for (let i = 0; i < arr1.length; i++) {
      arr.push(arr1[i].trim());
    }
    console.log("Entire list => ", arr);
    // console.log("Selected Genres: " + selected);
    let select_options = document.querySelector("#genres_selector");
    console.log("Options: ", select_options);
    let selected = select_options.selectedOptions;
    let count = 0;
    for (var i = 0; i < select_options.options.length; i++) {
      if (arr.includes(select_options.options.item(i).innerText)) {
        console.log(select_options.options.item(i).innerText);
        select_options.options.item(i).selected = "selected";
        selected[count++] = select_options.options.item(i);
      }
    }
    console.log("Selected Genres: " + selected);
  }
  // for (var option of options) {
  //   if (selected.includes(option.value)) {
  //     option.selected = true;
  //     console.log(option.value + " is selected");
  //   }
  // }
});

$("#looking_talent").click(function (e) {
  console.log("Checkbox : ", e.target);
  let checkb = e.target.checked;
  if (checkb) e.target.value = true;
  else e.target.value = false;
});

$("#looking_for_venue").click(function (e) {
  console.log("Checkbox : ", e.target);
  let checkb = e.target.checked;
  if (checkb) e.target.value = true;
  else e.target.value = false;
});

$("#delete_link").click(function (e) {
  {
    e.preventDefault();
    let conf = confirm("Are you sure you want to delete this Venue");
    if (conf) {
      window.location = e.currentTarget.href;
    }
  }
});
