document.getElementById('icon').addEventListener('click', function () {
    var nav = document.getElementsByTagName('nav')[0];
    if (nav.style.display == 'block') {
        nav.style.display = 'none';
    } else {
        nav.style.display = 'block';
    }
}, false);

// ============ Sliding images JS =================================//

$(function() {
   $(".heart").on("click", function() {
     $(this).toggleClass("is-active");
   });
 });

// =================Sliding Images JS End ==========================//



$('.carousel').carousel({
  interval: false,
});
